## [1.2.1] - 2024-03-25
### Changed
- Fixed packaging issue that prevent the CLI from working.

## [1.2.0] - 2023-09-06
### Added
- Added decoding of description, user version and last updated.

### Changed
- #4 Added support for autoincrement fields (which when encountered caused an error)

## [1.1.0] - 2022-06-01
### Added
- DATE field support (unverified). Closes #3.
- Acknowledge empty field byte, stop decoding and return `None`.

## [1.0.2] - 2022-02-06
### Changed
- Fixed handling of deleted rows. Closes #1.
- Fixed a `ResourceWarning: unclosed file`, close the DB file after reading it into memory.

## [1.0.1] - 2021-09-11
### Changed
- Fixed issue with empty DateTime's throwing a `OverflowError: date value out of range` exception.
- Decode strings fields using cp1252 rather than UTF-8. As part of this, if an unknown character is found it will be replaced with `\ufffd` rather than throwing an exception.

## [1.0.0] - 2021-09-08
### Added
- Explanation of the recommended reverse chronological release ordering.
- Added `fields()` to get field names.
- Added `rows()` generator to get efficiently get row data.

### Removed
- Last updated was incorrectly being extracted and will return None until it's fixed.
- Various debugging methods using during initial development.

## [0.1.0] - 2021-09-06
- Initial alpha release.

[Unreleased]: https://github.com/linville/pydbisam/compare/v1.2.1...HEAD
[1.2.1]: https://github.com/linville/pydbisam/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/linville/pydbisam/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/linville/pydbisam/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/linville/pydbisam/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/linville/pydbisam/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/linville/pydbisam/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/linville/pydbisam/releases/tag/v0.1.0
