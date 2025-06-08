# Volcano Hybrid Home Assistant Integration

A complete Home Assistant integration for the Storz & Bickel Volcano Hybrid vaporizer, providing full device control, usage statistics, and automation capabilities.

## Features

### Device Control
- **Climate Entity**: Temperature control and heating on/off
- **Fan Entity**: Fan control with timer functionality  
- **Preset Buttons**: Quick access to temperature presets (185°C, 190°C, 195°C, 200°C)
- **Screen Brightness**: Adjustable display brightness
- **Next Session**: Cycle through temperature presets

### Statistics & Monitoring
- **Usage Statistics**: Sessions per day, average duration, favorite temperature
- **Real-time Status**: Connection status, current settings
- **Historical Data**: Long-term usage patterns via HA statistics

### Automation Features
- **Custom Services**: Start sessions, temperature sequences, fan timers
- **Device Triggers**: Automation triggers for session events
- **Advanced Controls**: Fan timers, screen animations

## Installation

### Manual Installation (for testing)

1. Copy the `volcano_hybrid` folder to your Home Assistant `custom_components` directory:
   ```
   config/
   └── custom_components/
       └── volcano_hybrid/
   ```

2. Restart Home Assistant

3. Go to **Settings** → **Devices & Services** → **Add Integration**

4. Search for "Volcano Hybrid" and follow the setup wizard

### HACS Installation (when available)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Search for "Volcano Hybrid"
4. Install and restart Home Assistant

## Setup

### Automatic Discovery

If your Volcano is powered on and discoverable, the integration will automatically detect it via Bluetooth. Simply confirm the device when prompted.

### Manual Setup

1. Find your Volcano's MAC address:
   - Use the included `getMacAddress.py` script
   - Or check your system's Bluetooth settings

2. During setup, enter the MAC address in format: `XX:XX:XX:XX:XX:XX`

## Usage

### Basic Control

- **Climate Entity**: Set temperature and turn heating on/off
- **Fan Entity**: Control fan manually or with timers
- **Preset Buttons**: Quick temperature selection

### Advanced Features

#### Custom Services

**Start Session**:
```yaml
service: volcano_hybrid.start_session
data:
  entity_id: climate.volcano_hybrid
  temperature: 190
  duration: 15  # Optional auto-off timer
```

**Temperature Sequence** (Flavor Chasing):
```yaml
service: volcano_hybrid.temperature_sequence
data:
  entity_id: climate.volcano_hybrid
  temperatures: [185, 190, 195, 200]
  interval: 5  # Minutes between changes
```

**Fan Timer**:
```yaml
service: volcano_hybrid.fan_timer
data:
  entity_id: fan.volcano_hybrid_fan
  duration: 36  # Seconds
```

### Automation Examples

**Auto-heat before arriving home**:
```yaml
automation:
  - alias: "Preheat Volcano"
    trigger:
      - platform: zone
        entity_id: person.you
        zone: zone.home
    action:
      - service: volcano_hybrid.start_session
        data:
          entity_id: climate.volcano_hybrid
          temperature: 190
```

**Voice Control** (via Google/Alexa):
- "Set the volcano to 185 degrees"
- "Turn on the volcano fan for 30 seconds"
- "Start the volcano quick session"

## Entities Created

### Climate
- `climate.volcano_hybrid` - Main temperature control

### Fan  
- `fan.volcano_hybrid_fan` - Fan control with timer support

### Sensors
- `sensor.volcano_target_temperature` - Current target temp
- `sensor.volcano_current_temperature` - Current actual temp
- `sensor.volcano_connection_status` - BLE connection status
- `sensor.volcano_ble_firmware_version` - BLE firmware version
- `sensor.volcano_firmware_version` - Device firmware version
- `sensor.volcano_serial_number` - Device serial number
- `sensor.volcano_hours_of_operation` - Total operation hours
- `sensor.volcano_minutes_of_operation` - Total operation minutes

### Buttons
- `button.volcano_flavor_185c` - 185°C preset
- `button.volcano_balanced_190c` - 190°C preset  
- `button.volcano_potent_195c` - 195°C preset
- `button.volcano_maximum_200c` - 200°C preset
- `button.volcano_next_session` - Cycle presets
- `button.volcano_quick_session` - Start at 190°C

### Numbers
- `number.volcano_fan_timer` - Fan timer duration
- `number.volcano_screen_brightness` - Display brightness

## Troubleshooting

### Connection Issues
1. Ensure Volcano is powered on and in range
2. Check Bluetooth is enabled on HA host
3. Verify MAC address is correct
4. Restart the integration if needed

### Bluetooth Permissions (Linux)
```bash
sudo usermod -a -G bluetooth homeassistant
```

### Logs
Enable debug logging:
```yaml
logger:
  default: info
  logs:
    custom_components.volcano_hybrid: debug
```

## Development

### Local Testing
1. Copy integration to `custom_components/`
2. Enable developer mode in HA
3. Use "Check Configuration" to validate
4. Test with actual Volcano device

### Contributing
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## Compatibility

- **Home Assistant**: 2024.1.0+
- **Python**: 3.11+
- **Bluetooth**: Requires BLE support
- **Device**: Storz & Bickel Volcano Hybrid

## Migration from Original Project Onyx Server from ImACoder

If you're currently using the original `volcanoBleServer.py`:

1. Stop the existing server
2. Install this integration
3. Use the same MAC address during setup
4. Replace batch scripts with HA automations

All functionality from the original TCP server is preserved and enhanced.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the original Volcano BLE server implementation
- Storz & Bickel for the Volcano Hybrid device
- Home Assistant community for integration patterns

## Custom Lovelace Card

This integration includes a beautiful custom Lovelace card with an interactive SVG volcano background and intuitive controls.

### Card Installation

#### Automatic Installation (Recommended)
1. Copy the entire `www/` folder from this repository to your Home Assistant configuration directory:
   ```
   config/
   └── www/
       ├── volcano-card.js
       ├── volcano-card-editor.js
       └── trace.svg
   ```

2. Add the resource in Home Assistant:
   - **Via UI**: Go to **Settings** → **Dashboards** → **Resources** → **Add Resource**
     - URL: `/local/volcano-card.js`
     - Resource type: **JavaScript module**
   
   - **Via YAML**: Add to your `configuration.yaml`:
     ```yaml
     lovelace:
       resources:
         - url: /local/volcano-card.js
           type: module
     ```

3. Restart Home Assistant and refresh your browser cache (Ctrl+F5)

#### Manual Installation
1. Download the files from the `www/` folder:
   - `volcano-card.js` (main card)
   - `volcano-card-editor.js` (configuration UI)
   - `trace.svg` (volcano background)

2. Place them in your `config/www/` directory

3. Follow step 2-3 from automatic installation above

### Using the Card

Add the card to your dashboard:

```yaml
type: custom:volcano-card
entity: climate.volcano_hybrid
fan_entity: fan.volcano_hybrid_fan
title: "Volcano Hybrid"
show_title: true
compact: false
```

**Card Configuration Options:**
- `entity` (required): Your volcano climate entity
- `fan_entity` (required): Your volcano fan entity  
- `title`: Card title (default: "Volcano Hybrid")
- `show_title`: Show/hide title (default: true)
- `compact`: Compact mode for smaller spaces (default: false)

**Card Features:**
- Interactive SVG volcano background
- Real-time temperature display (current/target)
- Heat and fan toggle buttons with status indicators
- Temperature preset buttons (185°C, 190°C, 195°C, 200°C, Next)
- Responsive design that works on all screen sizes
- Visual feedback for all interactions

### Card Troubleshooting

**"Custom element doesn't exist" error:**
1. Verify files are in `config/www/` directory
2. Check resource is registered correctly in Settings → Dashboards → Resources
3. Clear browser cache (Ctrl+F5) and restart Home Assistant
4. Check browser console (F12) for JavaScript errors

**Card not updating:**
1. Ensure entity names match your actual volcano entities
2. Check entities are available in Developer Tools → States
3. Verify entities are not "unavailable" or "unknown"

**Layout issues:**
1. Try toggling compact mode: `compact: true`
2. Card is designed to be responsive - avoid fixed width containers
3. Test on different screen sizes for optimal experience
