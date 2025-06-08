# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-08-06

### Added
- **Custom Lovelace Card**: Beautiful interactive volcano card with SVG background
  - Real-time temperature display (current/target)
  - Heat and fan toggle buttons with visual status indicators
  - Temperature preset buttons (185°C, 190°C, 195°C, 200°C, Next Session)
  - Responsive design for all screen sizes
  - Configuration UI for easy dashboard setup
- Complete card installation guide with troubleshooting
- Enhanced documentation with card usage examples

## [1.0.1] - 2025-06-08

### Removed
- Removed unavailable statistical sensors that were causing entity errors:
  - `sensor.volcano_sessions_today` - Daily session count
  - `sensor.volcano_avg_session_duration` - Average session length
  - `sensor.volcano_favorite_temperature` - Most used temperature
  - `sensor.volcano_time_since_last_use` - Time since last session
  - `sensor.volcano_total_runtime_today` - Total usage today

### Fixed
- Fixed device info sensors (firmware versions, serial number, operation hours) switching to "unknown" after initial load
- Improved BLE connection stability for static device information
- Device info sensors now update every 10 minutes while temperature sensors remain at 5-second intervals

## [1.0.0] - 2025-06-04

### Added
- Initial public release
- Complete Home Assistant integration for Volcano Hybrid
- All core functionality implemented and tested
- Documentation and setup guides
- HACS compatibility

[Unreleased]: https://github.com/grovesdigital/volcano-hybrid-ha/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/grovesdigital/volcano-hybrid-ha/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/grovesdigital/volcano-hybrid-ha/releases/tag/v1.0.0
