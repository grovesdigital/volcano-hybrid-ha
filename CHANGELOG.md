# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Volcano Hybrid Home Assistant Integration
- Full climate control with temperature setting and heating on/off
- Fan control with speed settings and timer functionality
- Comprehensive sensor suite for device monitoring
- Switch entities for heat and fan control
- Button entities for quick actions and presets
- Number entities for precise temperature and fan speed control
- Automatic Bluetooth device discovery
- Usage statistics tracking
- Custom services for advanced control
- Multi-language support (English)

### Features
- **Climate Entity**: Complete temperature control with current/target temperature display
- **Fan Entity**: Variable speed fan with timer support
- **Sensors**: Real-time monitoring of temperature, fan status, device state, and statistics
- **Switches**: Binary controls for heat and fan
- **Buttons**: Quick preset actions (185°C, 190°C, 195°C, 200°C, Heat On/Off, Fan On/Off)
- **Numbers**: Precise sliders for temperature and fan speed
- **Services**: Advanced control services for automation
- **Statistics**: Session tracking and usage analytics
- **Diagnostics**: Device information and troubleshooting data

### Technical
- Bluetooth LE communication using bleak library
- Robust connection handling with automatic reconnection
- Comprehensive error handling and logging
- Home Assistant 2023.1+ compatibility
- Type hints throughout the codebase
- Extensive documentation and examples

## [1.0.0] - 2025-06-04

### Added
- Initial public release
- Complete Home Assistant integration for Volcano Hybrid
- All core functionality implemented and tested
- Documentation and setup guides
- HACS compatibility

[Unreleased]: https://github.com/yourusername/volcano-hybrid-ha/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/volcano-hybrid-ha/releases/tag/v1.0.0
