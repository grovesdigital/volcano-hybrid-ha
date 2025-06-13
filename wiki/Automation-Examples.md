# Automation Examples

This page provides complete, copy-paste automation examples for common Volcano workflows. These examples demonstrate the **building blocks approach** - showing you how to combine the integration's entities and events into powerful automation workflows.

## 🎯 **Quick Start Automations**

### 1. **Simple Session Flow**
Complete session from button press to finished:

```yaml
# Create input button helper first
input_button:
  volcano_session:
    name: "Start Volcano Session"
    icon: mdi:volcano

# Main automation
automation:
  - alias: "Complete Volcano Session"
    description: "Full session workflow from button press"
    trigger:
      - platform: state
        entity_id: input_button.volcano_session
    action:
      # Set your preferred temperature
      - service: climate.set_temperature
        target:
          entity_id: climate.volcano_hybrid
        data:
          temperature: 190
      
      # Turn on heating
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.volcano_hybrid
        data:
          hvac_mode: heat
      
      # Wait for temperature to be reached
      - wait_for_trigger:
          - platform: event
            event_type: volcano_session_event
            event_data:
              type: temperature_reached
        timeout: "00:10:00"
        continue_on_timeout: false
      
      # Wait 30 seconds at temperature
      - delay: 30
      
      # Start fan for configured duration
      - service: fan.turn_on
        target:
          entity_id: fan.volcano_hybrid_fan
      
      # Notify when ready
      - service: notify.mobile_app_your_phone
        data:
          title: "Volcano Ready!"
          message: "Session ready at {{ states('sensor.volcano_current_temperature') }}°C"
```

### 2. **Temperature Presets**
Multiple temperature preset buttons:

```yaml
# Input helpers for preset buttons
input_button:
  volcano_preset_low:
    name: "Volcano 180°C"
    icon: mdi:thermometer
  volcano_preset_medium:
    name: "Volcano 195°C"
    icon: mdi:thermometer
  volcano_preset_high:
    name: "Volcano 210°C"
    icon: mdi:thermometer-high

# Preset automations
automation:
  - alias: "Volcano Low Temp Preset"
    trigger:
      - platform: state
        entity_id: input_button.volcano_preset_low
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.volcano_hybrid
        data:
          temperature: 180
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.volcano_hybrid
        data:
          hvac_mode: heat

  - alias: "Volcano Medium Temp Preset"
    trigger:
      - platform: state
        entity_id: input_button.volcano_preset_medium
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.volcano_hybrid
        data:
          temperature: 195
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.volcano_hybrid
        data:
          hvac_mode: heat

  - alias: "Volcano High Temp Preset"
    trigger:
      - platform: state
        entity_id: input_button.volcano_preset_high
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.volcano_hybrid
        data:
          temperature: 210
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.volcano_hybrid
        data:
          hvac_mode: heat
```

## 🤖 **Smart Automations**

### 3. **Adaptive Session Timer**
Fan timer that adapts based on temperature:

```yaml
automation:
  - alias: "Smart Fan Timer"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: temperature_reached
    action:
      # Calculate fan duration based on temperature
      - service: number.set_value
        target:
          entity_id: number.volcano_fan_timer
        data:
          value: >
            {% set temp = trigger.event.data.actual_temperature | int %}
            {% if temp < 175 %}
              30
            {% elif temp < 190 %}
              36
            {% elif temp < 200 %}
              40
            {% else %}
              45
            {% endif %}
      
      # Wait user-defined time at temperature
      - delay: "{{ states('input_number.preheat_wait') | int }}"
      
      # Start fan with calculated duration
      - service: fan.turn_on
        target:
          entity_id: fan.volcano_hybrid_fan
```

### 4. **Session Scheduling**
Automatic sessions based on time/day:

```yaml
# Input helpers for scheduling
input_boolean:
  volcano_auto_sessions:
    name: "Enable Auto Sessions"
    icon: mdi:calendar-clock

input_datetime:
  volcano_evening_session:
    name: "Evening Session Time"
    has_date: false
    has_time: true

input_select:
  volcano_evening_temp:
    name: "Evening Temperature"
    options:
      - "180°C"
      - "190°C" 
      - "200°C"
    initial: "190°C"

# Scheduled session automation
automation:
  - alias: "Evening Volcano Session"
    trigger:
      - platform: time
        at: input_datetime.volcano_evening_session
    condition:
      # Only on weekdays
      - condition: time
        weekday:
          - mon
          - tue
          - wed
          - thu
          - fri
      # Only if enabled
      - condition: state
        entity_id: input_boolean.volcano_auto_sessions
        state: "on"
    action:
      # Set temperature from dropdown
      - service: climate.set_temperature
        target:
          entity_id: climate.volcano_hybrid
        data:
          temperature: >
            {% set temp_str = states('input_select.volcano_evening_temp') %}
            {{ temp_str.replace('°C', '') | int }}
      
      # Start heating
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.volcano_hybrid
        data:
          hvac_mode: heat
      
      # Notify
      - service: notify.mobile_app_your_phone
        data:
          title: "Evening Session Starting"
          message: "Volcano heating to {{ states('input_select.volcano_evening_temp') }}"
```

## 📊 **Monitoring & Statistics**

### 5. **Usage Tracking Dashboard**
Comprehensive usage monitoring:

```yaml
# Template sensors for dashboard
template:
  - sensor:
      - name: "Volcano Usage Today"
        state: >
          {% set sessions = states('sensor.volcano_sessions_today') | int %}
          {% set duration = states('sensor.volcano_average_session_duration') | float %}
          {% set total = sessions * duration %}
          {{ total | round(1) }} min
        attributes:
          sessions: "{{ states('sensor.volcano_sessions_today') }}"
          avg_duration: "{{ states('sensor.volcano_average_session_duration') }}"
          last_used: "{{ states('sensor.volcano_time_since_last_use') }}"

# Daily usage report
automation:
  - alias: "Daily Volcano Report"
    trigger:
      - platform: time
        at: "23:00:00"
    condition:
      - condition: template
        value_template: "{{ states('sensor.volcano_sessions_today') | int > 0 }}"
    action:
      - service: notify.persistent_notification
        data:
          title: "Daily Volcano Report"
          message: >
            📊 Today's Usage:
            • Sessions: {{ states('sensor.volcano_sessions_today') }}
            • Total Time: {{ states('sensor.volcano_usage_today') }}
            • Average Duration: {{ states('sensor.volcano_average_session_duration') }} min
            • Last Use: {{ states('sensor.volcano_time_since_last_use') }}
```

### 6. **Heavy Usage Alerts**
Monitor and alert on heavy usage:

```yaml
automation:
  - alias: "Heavy Usage Warning"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_started
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.session_count_today >= 8 }}"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Heavy Usage Alert"
          message: >
            This is session #{{ trigger.event.data.session_count_today }} today.
            Consider taking a break! 🌿
          data:
            priority: high
            color: orange

  - alias: "Usage Milestone Celebration"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_ended
    condition:
      # Every 50 total sessions
      - condition: template
        value_template: "{{ trigger.event.data.total_sessions % 50 == 0 }}"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🎉 Session Milestone!"
          message: >
            Congratulations! You've completed {{ trigger.event.data.total_sessions }} sessions.
            Keep enjoying responsibly! 
```

## 🏠 **Smart Home Integration**

### 7. **Ambient Environment Control**
Create the perfect session environment:

```yaml
automation:
  - alias: "Session Environment Setup"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_started
    action:
      # Dim lights
      - service: light.turn_on
        target:
          entity_id: light.living_room_lights
        data:
          brightness_pct: 20
          color_name: red
      
      # Close blinds if daytime
      - condition: sun
        after: sunrise
        before: sunset
      - service: cover.close_cover
        target:
          entity_id: cover.living_room_blinds
      
      # Start chill music
      - service: media_player.play_media
        target:
          entity_id: media_player.spotify
        data:
          media_content_type: playlist
          media_content_id: "spotify:playlist:37i9dQZF1DX0XUsuxWHRQd"
      
      # Adjust climate
      - service: climate.set_temperature
        target:
          entity_id: climate.house_thermostat
        data:
          temperature: 21

  - alias: "Session Environment Cleanup"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_ended
    action:
      # Restore normal lighting
      - service: light.turn_on
        target:
          entity_id: light.living_room_lights
        data:
          brightness_pct: 80
          color_temp: 350
      
      # Open blinds if still daytime
      - condition: sun
        before: sunset
      - service: cover.open_cover
        target:
          entity_id: cover.living_room_blinds
      
      # Lower music volume
      - service: media_player.volume_set
        target:
          entity_id: media_player.spotify
        data:
          volume_level: 0.3
```

### 8. **Security & Safety**
Safety features for responsible use:

```yaml
# Input helpers for safety features
input_number:
  volcano_max_daily_sessions:
    name: "Max Daily Sessions"
    min: 1
    max: 20
    initial: 10
    icon: mdi:speedometer

input_boolean:
  volcano_safety_mode:
    name: "Safety Mode"
    icon: mdi:shield-check

# Safety automations
automation:
  - alias: "Daily Session Limit"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_started
    condition:
      - condition: state
        entity_id: input_boolean.volcano_safety_mode
        state: "on"
      - condition: template
        value_template: >
          {{ trigger.event.data.session_count_today >= 
             states('input_number.volcano_max_daily_sessions') | int }}
    action:
      # Turn off volcano
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.volcano_hybrid
        data:
          hvac_mode: "off"
      
      # Notify user
      - service: notify.mobile_app_your_phone
        data:
          title: "Daily Limit Reached"
          message: >
            You've reached your daily session limit of 
            {{ states('input_number.volcano_max_daily_sessions') }} sessions.
            Volcano has been turned off for your safety.
          data:
            priority: high

  - alias: "Auto Shutoff Timer"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_started
    action:
      # Set 30-minute auto shutoff
      - delay: "00:30:00"
      # Check if still heating
      - condition: state
        entity_id: sensor.volcano_heat_status
        state: "On"
      # Turn off if no activity
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.volcano_hybrid
        data:
          hvac_mode: "off"
      - service: notify.mobile_app_your_phone
        data:
          title: "Auto Shutoff"
          message: "Volcano automatically turned off after 30 minutes"
```

## 🔧 **Maintenance & Care**

### 9. **Maintenance Reminders**
Smart maintenance scheduling:

```yaml
# Maintenance tracking
input_datetime:
  volcano_last_cleaning:
    name: "Last Cleaning Date"
    has_date: true
    has_time: false

automation:
  - alias: "Cleaning Reminder (Sessions)"
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
          title: "🧽 Cleaning Time!"
          message: >
            After {{ trigger.event.data.total_sessions }} sessions, 
            it's time to clean your Volcano for optimal performance.
            
            Cleaning Tips:
            • Use isopropyl alcohol for chamber
            • Clean balloon and mouthpiece
            • Check air filter

  - alias: "Cleaning Reminder (Time)"
    trigger:
      - platform: time
        at: "10:00:00"
    condition:
      # Every 2 weeks
      - condition: template
        value_template: >
          {{ (as_timestamp(now()) - as_timestamp(states('input_datetime.volcano_last_cleaning'))) 
             > (14 * 24 * 3600) }}
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Weekly Maintenance"
          message: >
            It's been 2+ weeks since your last cleaning.
            Clean your Volcano for the best experience!
```

## 📱 **Mobile Integration**

### 10. **Mobile Quick Actions**
iOS/Android notification actions:

```yaml
automation:
  - alias: "Mobile Quick Session"
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "start_volcano_session"
    action:
      # Use default temperature
      - service: climate.set_temperature
        target:
          entity_id: climate.volcano_hybrid
        data:
          temperature: 190
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.volcano_hybrid
        data:
          hvac_mode: heat
      - service: notify.mobile_app_your_phone
        data:
          message: "Volcano session started remotely!"

  - alias: "Temperature Reached Mobile Action"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: temperature_reached
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🌡️ Volcano Ready!"
          message: "Temperature reached {{ trigger.event.data.actual_temperature }}°C"
          data:
            actions:
              - action: "start_fan"
                title: "Start Fan"
              - action: "wait_more"
                title: "Wait 30s More"
```

## 🎨 **Dashboard Configurations**

### 11. **Complete Dashboard Card**
Comprehensive control dashboard:

```yaml
# Lovelace dashboard card
type: vertical-stack
cards:
  # Status overview
  - type: horizontal-stack
    cards:
      - type: stat
        entity: sensor.volcano_current_temperature
        name: "Current"
        icon: mdi:thermometer
      - type: stat
        entity: sensor.volcano_target_temperature
        name: "Target"
        icon: mdi:thermometer-high
      - type: stat
        entity: sensor.volcano_sessions_today
        name: "Sessions"
        icon: mdi:counter

  # Quick controls
  - type: entities
    entities:
      - climate.volcano_hybrid
      - fan.volcano_hybrid_fan
      - number.volcano_fan_timer
    title: "Controls"

  # Session buttons
  - type: horizontal-stack
    cards:
      - type: button
        tap_action:
          action: call-service
          service: input_button.press
          target:
            entity_id: input_button.volcano_preset_low
        name: "180°C"
        icon: mdi:thermometer
      - type: button
        tap_action:
          action: call-service
          service: input_button.press
          target:
            entity_id: input_button.volcano_preset_medium
        name: "195°C"
        icon: mdi:thermometer
      - type: button
        tap_action:
          action: call-service
          service: input_button.press
          target:
            entity_id: input_button.volcano_preset_high
        name: "210°C"
        icon: mdi:thermometer-high

  # Statistics
  - type: entities
    entities:
      - sensor.volcano_time_since_last_use
      - sensor.volcano_average_session_duration
      - sensor.volcano_total_operation_time
    title: "Statistics"
```

## 🚀 **Advanced Patterns**

See [Advanced Patterns](Advanced-Patterns) for more complex examples including:
- Multi-user session management
- Integration with other vaporizers
- Machine learning usage predictions
- Advanced statistics and reporting

---

**Next Steps:**
- Adapt these examples to your preferences
- Combine multiple patterns for complex workflows
- Share your creations with the community
- Check [Building Blocks](Building-Blocks) for design principles
