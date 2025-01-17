# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2025-01-10
### Changed
- Migrated from SQLite to MySQL on Google Cloud.
- Updated table schema to support aggregate scores (`n1`, `n2`, `n3`) with values between 0 and 600.
- Added constraints for question responses (`q1_response` to `q6_response`) to ensure values are between 1 and 6.

### Fixed
- Normalized scores to handle large aggregates correctly.

## [1.1.4] - 2025-01-07
### Added
- No Adds

### Changed
- DB captures browser, region, version, and session info
- DB Captures response ID instead of response text
- PDF footer looks better; fixed URL link to philosophics.blog

# [1.1.3] - 2024-12-28
### Added
- No Adds

### Changed
- PDF is paginated and looks better
- PDF renders in a single click (instead of 2)
- Summary pages cleaned up

## [1.1.2] - 2024-12-28
### Added
- No Adds

### Changed
- Cleaned up Survey page and error handling
- Cleaned up Results page, specifically ternary chart presentment
- Removed Sidebar and pages

### Technical
- Removed deprecated files

## [1.1.1] - 2024-12-27

### Changed
- Deprecated writing responses to CSV in favour of SQLite
- Minor report interface modifications

## [1.1.0] - 2024-12-25
### Added
- SQLite database support
- SQLite data viewer

### Changed
- Deprecated writing responses to CSV in favour of SQLite
- Minor report interface modifications

## [1.0.0] - 2024-12-24
### Added
- Initial release with working survey and ternary plot
- Core application features
  - Interactive questionnaire
  - Real-time ternary chart visualization
  - Response aggregation

### Changed
- Reorganized project structure into modular components:
  - Core survey logic
  - Data handling
  - Visualization
  - Question management
  - User interface
- Moved data files to structured locations
- Added data viewer component

### Technical
- Implemented proper Python package structure
- Added version tracking
- Created separate data viewer tool