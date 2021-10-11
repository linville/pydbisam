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

[Unreleased]: https://github.com/linville/pydbisam/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/linville/pydbisam/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/linville/pydbisam/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/linville/pydbisam/releases/tag/v0.1.0
