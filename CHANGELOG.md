# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `depyty env` subcommand to print information about the Python environment
- JSON reports using `--reporter=json` 

### Changed

- Analyzing files is now done using a separate `depyty check` subcommand
- Analysis now works on a "fully qualified" basis. Before we only checked
  top-level names of modules, which had limitiations, e.g. it did not work
  reliably for namespace packages.

## [0.2.0] - 2025-04-12

### Added

- `--python` flag to inspect a Python environment other than the current one
- `--verbose` flag for more extensive output and debugging information
- `--reporter` flag for more configuring the output format
- GitLab Code Quality reporter
- a proper commandline interface using `argparse`
- automatic configuration detection when using a `uv` workspace

### Changed

- exit with code `2` when there are violations
- display _relative_ paths to files when using the console reporter
- Packages not found in the environment are now skipped, instead of directly throwing an error
- If no source files were analyzed, the analysis is treated as failed
- console reporter prints clearer messages

## [0.1.1] - 2025-03-30

### Added

- initial proof of concept

