from dataclasses import dataclass
from pprint import pprint
from depyty.environment import get_available_modules_by_name


@dataclass
class PackageContext:
    distribution_name: str
    declared_dependencies: set[str]


def main():
    # First we inspect the environment, to see what packages are installed.
    available_modules_by_name = get_available_modules_by_name()

    # TODO: These still need some work, the detection is not 100% perfect.
    pprint(
        {
            name
            for name, module in available_modules_by_name.items()
            if not module.belongs_to_stdlib and not module.distribution_names
        }
    )

    # Now, we'll check each of the given first-party packages to see what they
    # import, and if their imports are properly declared.


if __name__ == "__main__":
    main()
