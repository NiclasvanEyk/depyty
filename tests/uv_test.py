import json
import subprocess
from io import StringIO
from pathlib import Path

from depyty.cli.commands.analyze import AnalyzeCommand
from depyty.reporting import ReporterName
from src.depyty.cli.context import CliContext


def test_works_with_default_package(tmpdir: Path):
    # Given a monorepo with 2 packages
    subprocess.run(["uv", "init", "my-monorepo", "--bare"], cwd=tmpdir)
    monorepodir = tmpdir / "my-monorepo"

    subprocess.run(["uv", "init", "package-a", "--package"], cwd=monorepodir)
    subprocess.run(["uv", "init", "package-b", "--package"], cwd=monorepodir)

    # A declares a dependency on b
    subprocess.run(["uv", "add", "package-b"], cwd=monorepodir / "package-a")

    # both import each other
    (monorepodir / "package-a" / "src" / "package_a" / "__init__.py").write_text(
        "import package_b", "utf-8"
    )
    (monorepodir / "package-b" / "src" / "package_b" / "__init__.py").write_text(
        "import package_a", "utf-8"
    )

    with StringIO() as buffer:
        command = AnalyzeCommand(
            reporter=ReporterName.JSON,
            globs=[],
            python_path=None,
            stdout=buffer,
        )

        AnalyzeCommand.run(command, CliContext(cwd=monorepodir, verbose=True))

        # We expect a violation in package b, since it does not explicitly declare
        # its dependency on package a
        output = json.loads(buffer.getvalue())
        assert output[0]["context"]["distribution_name"] == "package-b"
        assert output[0]["undeclared_dependency"] == "package_a"
