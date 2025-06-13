# Event System

The Volcano Hybrid integration features a comprehensive event system that fires detailed events during device operations. These events are the foundation for building sophisticated automations.

## 🎪 **Event Philosophy**

The event system follows the integration's **building blocks approach**:

- **Rich Event Data**: Each event includes comprehensive context
- **Automation Triggers**: Events are designed as automation triggers
- **User Flexibility**: Build exactly the workflows you want
- **Professional Grade**: Detailed timestamps and session tracking

## 📋 **Event Types Overview**

All events use the event type: **`volcano_session_event`**

The specific event is identified by the `type` field in the event data.

### Session Events
- `session_started` - New session begins (heating starts)
- `temperature_reached` - Target temperature achieved
- `session_ended` - Session concluded (device returns to idle)

### Fan Events  
- `fan_started` - Fan turned on
- `fan_stopped` - Fan turned off

### Future Events (Planned)
- `maintenance_due` - Based on operation hours
- `temperature_changed` - Significant temperature changes
- `connection_lost` - Bluetooth disconnection

## 📊 **Event Data Structure**

### Session Started Event
```yaml
event_type: volcano_session_event
event_data:
  type: session_started
  target_temperature: 195
  current_temperature: 65
  timestamp: "2025-06-13T14:30:00.123456"
  session_count_today: 3
  total_sessions: 847
  time_since_last_session: 7200  # seconds
```

### Temperature Reached Event
```yaml
event_type: volcano_session_event
event_data:
  type: temperature_reached
  target_temperature: 195
  actual_temperature: 192
  timestamp: "2025-06-13T14:32:15.789012"
  session_active: true
  heating_duration: 135  # seconds to reach temp
```

### Fan Started Event
```yaml
event_type: volcano_session_event
event_data:
  type: fan_started
  timestamp: "2025-06-13T14:32:30.456789"
  session_active: true
  fan_timer_duration: 36  # seconds
  current_temperature: 192
```

### Fan Stopped Event
```yaml
event_type: volcano_session_event
event_data:
  type: fan_stopped
  timestamp: "2025-06-13T14:33:06.789123"
  session_active: true
  fan_duration: 36  # actual runtime seconds
  current_temperature: 188
```

### Session Ended Event
```yaml
event_type: volcano_session_event
event_data:
  type: session_ended
  duration_minutes: 12.3
  start_time: "2025-06-13T14:30:00.123456"
  end_time: "2025-06-13T14:42:18.456789"
  timestamp: "2025-06-13T14:42:18.456789"
  peak_temperature: 195
  average_temperature: 187
  fan_cycles: 2
```

## 🔧 **Using Events in Automations**

### Basic Event Trigger
```yaml
automation:
  - alias: "React to Temperature Reached"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: temperature_reached
    action:
      - service: notify.mobile_app
        data:
          message: "Volcano ready at {{ trigger.event.data.actual_temperature }}°C!"
```

### Multiple Event Types
```yaml
automation:
  - alias: "Session Status Updates"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_started
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: temperature_reached
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_ended
    action:
      - service: notify.persistent_notification
        data:
          title: "Volcano {{ trigger.event.data.type | replace('_', ' ') | title }}"
          message: >
            {% if trigger.event.data.type == 'session_started' %}
              Session #{{ trigger.event.data.session_count_today }} started, targeting {{ trigger.event.data.target_temperature }}°C
            {% elif trigger.event.data.type == 'temperature_reached' %}
              Temperature reached: {{ trigger.event.data.actual_temperature }}°C
            {% elif trigger.event.data.type == 'session_ended' %}
              Session completed in {{ trigger.event.data.duration_minutes }} minutes
            {% endif %}
```

### Conditional Event Responses
```yaml
automation:
  - alias: "Smart Fan Control"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: temperature_reached
    condition:
      # Only auto-start fan if temperature is high enough
      - condition: template
        value_template: "{{ trigger.event.data.actual_temperature >= 180 }}"
    action:
      # Wait user-defined time
      - delay: "{{ states('input_number.preheat_wait_time') | int }}"
      # Start fan for user-defined duration
      - service: fan.turn_on
        target:
          entity_id: fan.volcano_hybrid_fan
```

## 🎯 **Event-Driven Automation Patterns**

### Automatic Session Flow
```yaml
automation:
  - alias: "Complete Auto Session"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_started
    action:
      # Wait for temperature
      - wait_for_trigger:
          - platform: event
            event_type: volcano_session_event
            event_data:
              type: temperature_reached
        timeout: "00:10:00"
        continue_on_timeout: false
      
      # Wait at temperature
      - delay: 30
      
      # Start fan
      - service: fan.turn_on
        target:
          entity_id: fan.volcano_hybrid_fan
      
      # Notification
      - service: notify.mobile_app
        data:
          message: "Balloon session ready!"
```

### Session Statistics Tracking
```yaml
automation:
  - alias: "Track Session Stats"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_ended
    action:
      # Log to CSV file
      - service: notify.file
        data:
          filename: /config/volcano_sessions.csv
          message: >
            {{ trigger.event.data.timestamp }},
            {{ trigger.event.data.duration_minutes }},
            {{ trigger.event.data.peak_temperature }},
            {{ trigger.event.data.fan_cycles }}
      
      # Update input helpers for dashboard
      - service: input_number.set_value
        target:
          entity_id: input_number.last_session_duration
        data:
          value: "{{ trigger.event.data.duration_minutes }}"
```

### Usage Monitoring
```yaml
automation:
  - alias: "Heavy Usage Alert"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_started
    condition:
      # More than 8 sessions today
      - condition: template
        value_template: "{{ trigger.event.data.session_count_today > 8 }}"
    action:
      - service: notify.mobile_app
        data:
          title: "Heavy Usage Day"
          message: "Session #{{ trigger.event.data.session_count_today }} - consider taking a break!"
```

### Maintenance Reminders
```yaml
automation:
  - alias: "Maintenance Based on Usage"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_ended
    condition:
      # Every 100 sessions
      - condition: template
        value_template: "{{ trigger.event.data.total_sessions % 100 == 0 }}"
    action:
      - service: notify.persistent_notification
        data:
          title: "Maintenance Reminder"
          message: >
            Congratulations on {{ trigger.event.data.total_sessions }} sessions! 
            Time to clean your Volcano for optimal performance.
```

## 🔍 **Event Debugging**

### Listening to Events
Use **Developer Tools** → **Events** to monitor volcano events:

1. **Event Type**: `volcano_session_event`
2. **Start Listening**
3. Use your device and watch events fire

### Event History
Check **Developer Tools** → **States** for event-related sensors:
- `sensor.volcano_sessions_today`
- `sensor.volcano_last_session_duration`
- `sensor.volcano_time_since_last_use`

### Automation Tracing
Enable automation tracing to debug event-triggered automations:
```yaml
# configuration.yaml
logger:
  default: info
  logs:
    homeassistant.components.automation: debug
    custom_components.volcano_hybrid: debug
```

## 📈 **Advanced Event Usage**

### Template Sensors Based on Events
```yaml
# configuration.yaml
template:
  - trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_ended
    sensor:
      - name: "Last Session Summary"
        state: "{{ trigger.event.data.duration_minutes }} min"
        attributes:
          start_time: "{{ trigger.event.data.start_time }}"
          end_time: "{{ trigger.event.data.end_time }}"
          peak_temp: "{{ trigger.event.data.peak_temperature }}"
          fan_cycles: "{{ trigger.event.data.fan_cycles }}"
```

### Event-Based Scripts
```yaml
# scripts.yaml
script:
  volcano_session_complete:
    alias: "Session Complete Actions"
    sequence:
      # Turn off heating
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.volcano_hybrid
        data:
          hvac_mode: "off"
      
      # Dim screen
      - service: number.set_value
        target:
          entity_id: number.volcano_screen_brightness
        data:
          value: 20
      
      # Log completion
      - service: logbook.log
        data:
          name: "Volcano Session"
          message: "Session completed after {{ session_duration }} minutes"
          entity_id: climate.volcano_hybrid

# Automation to call script
automation:
  - alias: "Auto Session Cleanup"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_ended
    action:
      - service: script.volcano_session_complete
        data:
          session_duration: "{{ trigger.event.data.duration_minutes }}"
```

### Multi-Device Coordination
```yaml
automation:
  - alias: "Smart Home Session Integration"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_started
    action:
      # Dim lights for session
      - service: light.turn_on
        target:
          entity_id: light.living_room
        data:
          brightness_pct: 30
          color_name: red
      
      # Start ambient music
      - service: media_player.play_media
        target:
          entity_id: media_player.spotify
        data:
          media_content_type: playlist
          media_content_id: "37i9dQZF1DX0XUsuxWHRQd"  # Chill playlist
      
      # Set thermostat for comfort
      - service: climate.set_temperature
        target:
          entity_id: climate.house
        data:
          temperature: 22
```

## 🎨 **Event System Benefits**

### For Users
- **Flexible Automation**: Build exactly what you want
- **Rich Context**: Detailed event data for complex logic
- **Real-time Response**: Events fire immediately
- **Professional Integration**: Works with all HA automation features

### For Developers
- **Extensible**: Easy to add new event types
- **Standardized**: Consistent event structure
- **Debuggable**: Clear event data for troubleshooting
- **Performance**: Efficient event firing without polling

## 🚀 **Future Event Enhancements**

Planned future event types:
- **Predictive Events**: Based on usage patterns
- **Maintenance Events**: Automatic cleaning reminders
- **Health Events**: Device performance monitoring
- **Integration Events**: Multi-device coordination

---

**Next Steps**: 
- Explore [Automation Examples](Automation-Examples) for complete workflows
- Check [Building Blocks](Building-Blocks) for design patterns
- See [Advanced Patterns](Advanced-Patterns) for complex scenarios
