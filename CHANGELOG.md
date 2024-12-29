# Changelog

All notable changes to this project will be documented in this file.

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