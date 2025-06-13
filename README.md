# Volcano Hybrid Home Assistant Integration

A complete Home Assistant integration for the Storz & Bickel Volcano Hybrid vaporizer, providing full device control, rich usage statistics, and comprehensive automation building blocks.

## Features

### Device Control
- **Climate Entity**: Temperature control and heating on/off
- **Fan Entity**: Fan control with timer functionality  
- **Status Monitoring**: Real-time heat and fan status sensors
- **Screen Brightness**: Adjustable display brightness
- **Dynamic Performance**: Smart update rates based on device activity

### Statistics & Monitoring
- **Session Tracking**: Daily sessions, total sessions, session durations
- **Usage Analytics**: Time since last use, average session duration
- **Real-time Status**: Connection status, heat/fan status, current settings
- **Operation Time**: Combined runtime display in human-readable "Xd Yh Zm" format
- **Historical Data**: Long-term usage patterns via HA statistics

### Automation Features
- **Rich Event System**: Comprehensive session events for advanced automation
- **Building Blocks Philosophy**: Provides data and controls for user-built automations
- **Smart Session Detection**: Automatic session tracking based on usage patterns
- **Performance Optimized**: Dynamic update intervals (1s active, 5s idle)

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

If your Volcano is powered on and discoverable, the integration will automatically detect it via Bluetooth. The integration now elegantly handles already-configured devices without errors.

### Manual Setup

1. Find your Volcano's MAC address:
   - Use the included `getMacAddress.py` script
   - Or check your system's Bluetooth settings

2. During setup, enter the MAC address in format: `XX:XX:XX:XX:XX:XX`

## Usage

### Basic Control

- **Climate Entity**: Set temperature and turn heating on/off
- **Fan Entity**: Control fan manually or with timers
- **Status Monitoring**: Real-time heat and fan status
- **Dynamic Updates**: Near real-time response during active use

### Advanced Features

Build your own automations using the rich building blocks provided:

**Simple Session Automation:**
```yaml
automation:
  - trigger: event
    event_type: volcano_session_event
    event_data:
      type: temperature_reached
    action:
      - delay: 30  # Wait 30 seconds at temperature
      - service: fan.turn_on
        target:
          entity_id: fan.volcano_hybrid_fan
```

**Usage Statistics Dashboard:**
```yaml
type: entities
entities:
  - sensor.volcano_sessions_today
  - sensor.volcano_time_since_last_use
  - sensor.volcano_average_session_duration
  - sensor.volcano_total_operation_time
title: "Volcano Usage Stats"
```

## Entities Created

### Climate
- `climate.volcano_hybrid` - Main temperature control

### Fan  
- `fan.volcano_hybrid_fan` - Fan control with timer support

### Sensors

#### Core Status
- `sensor.volcano_current_temperature` - Current device temperature
- `sensor.volcano_target_temperature` - Target/set temperature
- `sensor.volcano_connection_status` - Bluetooth connection status
- `sensor.volcano_heat_status` - **NEW**: Heat on/off status with dynamic icons
- `sensor.volcano_fan_status` - **NEW**: Fan on/off status with dynamic icons

#### Device Information
- `sensor.volcano_ble_firmware_version` - BLE firmware version
- `sensor.volcano_firmware_version` - Device firmware version
- `sensor.volcano_serial_number` - Device serial number
- `sensor.volcano_total_operation_time` - **ENHANCED**: Total device runtime in "Xd Yh Zm" format

#### Session Statistics
- `sensor.volcano_sessions_today` - **RESTORED**: Number of sessions today
- `sensor.volcano_total_sessions` - **NEW**: Total lifetime sessions
- `sensor.volcano_last_session_duration` - **NEW**: Duration of last session (minutes)
- `sensor.volcano_average_session_duration` - **NEW**: Average session duration (minutes)
- `sensor.volcano_time_since_last_use` - **RESTORED**: Time since last session (human-readable)

### Numbers
- `number.volcano_fan_timer` - Fan timer duration (5-300 seconds)
- `number.volcano_screen_brightness` - Display brightness (0-100%)

## 🎪 Event System

The integration fires detailed events for automation building blocks:

### Event Types

#### Session Events
```yaml
# Session started
event_type: volcano_session_event
event_data:
  type: session_started
  target_temperature: 195
  current_temperature: 65
  timestamp: "2025-06-13T14:30:00"
  session_count_today: 3
  total_sessions: 847

# Temperature reached target
event_type: volcano_session_event  
event_data:
  type: temperature_reached
  target_temperature: 195
  actual_temperature: 192
  timestamp: "2025-06-13T14:32:15"
  session_active: true

# Session ended
event_type: volcano_session_event
event_data:
  type: session_ended
  duration_minutes: 12.3
  start_time: "2025-06-13T14:30:00"  
  end_time: "2025-06-13T14:42:18"
  timestamp: "2025-06-13T14:42:18"
```

#### Fan Events
```yaml
# Fan started
event_type: volcano_session_event
event_data:
  type: fan_started
  timestamp: "2025-06-13T14:32:30"
  session_active: true

# Fan stopped  
event_type: volcano_session_event
event_data:
  type: fan_stopped
  timestamp: "2025-06-13T14:33:00"
  session_active: true
```

### Using Events in Automations

#### Automatic Fan Control
```yaml
automation:
  - alias: "Auto Fan After Temperature"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: temperature_reached
    action:
      - delay: "{{ states('input_number.preheat_wait') | int }}"
      - service: fan.turn_on
        target:
          entity_id: fan.volcano_hybrid_fan
```

#### Session Notifications
```yaml
automation:
  - alias: "Session Complete Notification"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_ended
    action:
      - service: notify.mobile_app
        data:
          message: "Session completed: {{ trigger.event.data.duration_minutes }} minutes"
```

#### Usage Statistics
```yaml
automation:
  - alias: "Daily Usage Summary"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: notify.persistent_notification
        data:
          title: "Daily Volcano Usage"
          message: "Today: {{ states('sensor.volcano_sessions_today') }} sessions, {{ states('sensor.volcano_time_since_last_use') }} since last use"
```

## 🛠️ Building Your Own Automations

This integration provides **building blocks** rather than pre-made workflows. Here are examples of what you can build:

### Simple Session Flow
```yaml
script:
  my_volcano_session:
    sequence:
      # Set your preferred temperature
      - service: climate.set_temperature
        target:
          entity_id: climate.volcano_hybrid
        data:
          temperature: 190
      
      # Turn on heating
      - service: climate.turn_on
        target:
          entity_id: climate.volcano_hybrid
      
      # Wait for temperature to be reached (using event)
      - wait_for_trigger:
          - platform: event
            event_type: volcano_session_event
            event_data:
              type: temperature_reached
      
      # Optional: Wait additional time at temperature  
      - delay: 30
      
      # Start fan for configured duration
      - service: fan.turn_on
        target:
          entity_id: fan.volcano_hybrid_fan
      
      # Fan will auto-stop based on timer setting
```

### Advanced Usage Tracking
```yaml
automation:
  - alias: "Track Heavy Usage"
    trigger:
      - platform: numeric_state
        entity_id: sensor.volcano_sessions_today
        above: 5
    action:
      - service: notify.mobile_app
        data:
          message: "Heavy usage day: {{ states('sensor.volcano_sessions_today') }} sessions"
  
  - alias: "Maintenance Reminder"
    trigger:
      - platform: template
        value_template: "{{ state_attr('sensor.volcano_total_operation_time', 'total_hours') | int > 1000 }}"
    action:
      - service: notify.persistent_notification
        data:
          title: "Maintenance Due"
          message: "Your Volcano has {{ state_attr('sensor.volcano_total_operation_time', 'total_hours') }} hours of operation"
```

## Performance Features

### Dynamic Update Intervals
The integration automatically adjusts update frequency based on device activity:

- **1 second**: During fan operation (balloon sessions)
- **1 second**: When approaching target temperature
- **2 seconds**: When actively heating
- **3 seconds**: When cooling down
- **5 seconds**: When idle/cold

This provides near real-time feedback during active use while conserving resources when idle.

## Troubleshooting

### Device Not Found
- Ensure Volcano is powered on and discoverable
- Check Bluetooth is enabled on Home Assistant host
- Verify MAC address format: `XX:XX:XX:XX:XX:XX`

### Already Configured Error
- The integration now elegantly handles this situation
- If issues persist, remove the existing integration and restart HA before re-adding

### Connection Issues
- Ensure device is within Bluetooth range
- Check for Bluetooth interference
- Restart Home Assistant if connection becomes unstable

### Performance Issues
- Dynamic update intervals automatically optimize performance
- Check Home Assistant logs for any BLE connection errors
- Ensure no other devices are simultaneously connecting to the Volcano

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
