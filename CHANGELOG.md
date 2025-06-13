# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-06-13

### ⚠️ BREAKING CHANGES
- **Combined Operation Sensors**: `sensor.volcano_hours_of_operation` and `sensor.volcano_minutes_of_operation` have been replaced with a single `sensor.volcano_total_operation_time` showing "Xd Yh Zm" format

### 🎯 Added
- **Enhanced Session Statistics**: Restored and improved session tracking sensors
  - `sensor.volcano_sessions_today` - Daily session count with automatic midnight reset
  - `sensor.volcano_total_sessions` - Lifetime session counter
  - `sensor.volcano_last_session_duration` - Duration of most recent session
  - `sensor.volcano_average_session_duration` - Running average across last 100 sessions
  - `sensor.volcano_time_since_last_use` - Time since last session with human-readable format
- **Device Status Sensors**: Real-time status monitoring
  - `sensor.volcano_heat_status` - Heat on/off with dynamic fire icons
  - `sensor.volcano_fan_status` - Fan on/off with dynamic fan icons
- **Enhanced Event System**: Rich event-driven automation support
  - `volcano_session_event` with types: `session_started`, `temperature_reached`, `fan_started`, `fan_stopped`, `session_ended`
  - Detailed event data including timestamps, temperatures, durations, and session counts
- **Smart Session Detection**: Automatic session tracking based on temperature and usage patterns
- **Dynamic Update Intervals**: Performance optimization based on device activity
  - 1 second updates during fan operation (balloon sessions)
  - 1 second updates when approaching target temperature
  - 2 seconds when actively heating
  - 3 seconds when cooling down
  - 5 seconds when idle
- **Improved Discovery Flow**: Elegant handling of already-configured devices without errors

### 🔧 Changed
- **Operation Time Display**: Combined hours and minutes into single human-readable sensor
- **Update Performance**: Dynamic polling rates for better responsiveness during active use
- **Error Handling**: Improved "already configured" detection allows entity adoption
- **Session Tracking**: Enhanced algorithms for more accurate session detection

### 🐛 Fixed
- **Configuration Flow**: Resolved "already configured" errors during device reactivation
- **Entity Adoption**: Integration can now elegantly reuse existing entities after reinstallation
- **Discovery Errors**: Bluetooth discovery no longer throws errors for configured devices
- **Update Intervals**: Optimized for better real-time feedback during active sessions

### 📖 Enhanced
- **Building Blocks Philosophy**: Integration provides rich data and events for user customization
- **Automation Examples**: Comprehensive documentation for user-built automations
- **Event Documentation**: Detailed examples of event-driven automation patterns
- **Statistics Usage**: Clear examples of using session data in automations

### 🎨 Benefits
- **Near Real-Time Updates**: 1-second response during active use
- **Rich Automation Data**: Comprehensive statistics and events for custom workflows
- **User-Friendly Display**: Human-readable operation time format
- **Elegant Reactivation**: Seamless integration reinstallation without manual cleanup
- **Performance Optimized**: Dynamic update rates reduce unnecessary polling

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

### Fixed
- Improved error handling in custom card
- Better mobile responsiveness
- Card state synchronization issues

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

[Unreleased]: https://github.com/grovesdigital/volcano-hybrid-ha/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/grovesdigital/volcano-hybrid-ha/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/grovesdigital/volcano-hybrid-ha/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/grovesdigital/volcano-hybrid-ha/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/grovesdigital/volcano-hybrid-ha/releases/tag/v1.0.0
