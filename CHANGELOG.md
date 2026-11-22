# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Update checker: the application now detects when a newer release tag is available
  and offers to update (y/n). The check runs in the background (at most once every
  24 hours) so it never delays startup.
- MIT License.

### Changed
- Reworked the project deletion flow: choose the project to delete, choose whether
  the project folder should also be deleted, then confirm by typing the full project name.

### Fixed
- Data.json: changed creation of data.json file, now puts file in the correct root folder. Before: made a file where user ran the program.
- README: removed `cd` from the terminal `if` block in the `.zshrc` example.
