# Building Blocks Guide

This guide explains the **building blocks philosophy** behind the Volcano Hybrid integration and provides patterns for creating your own custom automation workflows.

## 🧱 **Philosophy: Building Blocks, Not Recipes**

### Why Building Blocks?

The Volcano Hybrid integration is designed as a **professional toolkit** rather than a collection of pre-made automations. This approach provides:

- **Maximum Flexibility**: Build exactly what you want
- **User Empowerment**: You control every aspect of behavior  
- **Future-Proof**: Easily adapt as your needs change
- **Community Growth**: Share and remix automation patterns
- **Professional Grade**: Industrial-strength foundation for any workflow

### Target Users

This integration is designed for **Home Assistant tinkerers** who:
- Enjoy building custom automations
- Want control over every detail
- Like to experiment and iterate
- Share knowledge with the community
- Prefer flexibility over simplicity

## 🔧 **Core Building Blocks**

### 1. **Control Entities**
The foundation for device interaction:

```yaml
# Climate: Temperature control and heating
climate.volcano_hybrid:
  - Set target temperature (40-230°C)
  - Turn heating on/off
  - Monitor current temperature
  - HVAC modes: off, heat

# Fan: Airflow control with timing
fan.volcano_hybrid_fan:
  - Turn fan on/off
  - Automatic timer shutoff
  - Speed control (on/off only)

# Numbers: Device settings
number.volcano_fan_timer:     # 5-300 seconds
number.volcano_screen_brightness:  # 0-100%
```

### 2. **Information Sensors**
Rich data for decision making:

```yaml
# Real-time Status
sensor.volcano_current_temperature    # Live temperature reading
sensor.volcano_target_temperature     # Currently set target
sensor.volcano_connection_status      # Bluetooth connectivity
sensor.volcano_heat_status           # Heat on/off with icons
sensor.volcano_fan_status            # Fan on/off with icons

# Device Information  
sensor.volcano_total_operation_time   # "5d 14h 23m" format
sensor.volcano_firmware_version       # Device firmware
sensor.volcano_serial_number          # Device serial

# Session Statistics
sensor.volcano_sessions_today         # Daily session count
sensor.volcano_total_sessions         # Lifetime sessions
sensor.volcano_last_session_duration  # Most recent session time
sensor.volcano_average_session_duration # Running average
sensor.volcano_time_since_last_use    # Human-readable time
```

### 3. **Event System**
Rich automation triggers:

```yaml
# Session Events
volcano_session_event:
  - type: session_started
  - type: temperature_reached  
  - type: fan_started
  - type: fan_stopped
  - type: session_ended

# Each event includes rich context data:
# - Timestamps
# - Temperature data
# - Session counters
# - Duration information
```

## 🎯 **Design Patterns**

### Pattern 1: **Input Helper + Automation**
Create user-configurable controls:

```yaml
# User Configuration
input_button:
  my_volcano_session:
    name: "Start My Session"
    icon: mdi:volcano

input_number:
  my_preferred_temp:
    name: "My Temperature"
    min: 160
    max: 220
    initial: 190
    unit_of_measurement: "°C"

# Automation Logic
automation:
  - alias: "My Custom Session"
    trigger:
      - platform: state
        entity_id: input_button.my_volcano_session
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.volcano_hybrid
        data:
          temperature: "{{ states('input_number.my_preferred_temp') | int }}"
      - service: climate.turn_on
        target:
          entity_id: climate.volcano_hybrid
```

**Benefits:**
- User can adjust preferences via UI
- Automation logic is separated from configuration
- Easy to clone for multiple users/scenarios

### Pattern 2: **Event-Driven Workflows**
React to device state changes:

```yaml
automation:
  - alias: "Smart Session Response"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: temperature_reached
    action:
      # Dynamic response based on temperature
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.actual_temperature < 180 }}"
            sequence:
              - delay: 60  # Wait longer for lower temps
          - conditions:
              - condition: template  
                value_template: "{{ trigger.event.data.actual_temperature > 200 }}"
            sequence:
              - delay: 15  # Shorter wait for higher temps
        default:
          - delay: 30
      
      # Start fan
      - service: fan.turn_on
        target:
          entity_id: fan.volcano_hybrid_fan
```

**Benefits:**
- Responds to actual device state, not assumptions
- Rich event data enables intelligent decision making
- Resilient to timing variations

### Pattern 3: **Script-Based Workflows**
Reusable automation logic:

```yaml
script:
  volcano_preset_session:
    alias: "Preset Session"
    description: "Configurable session with any temperature"
    fields:
      temperature:
        description: "Target temperature"
        example: 190
      wait_time:
        description: "Wait time at temperature"
        example: 30
    sequence:
      # Set temperature from parameter
      - service: climate.set_temperature
        target:
          entity_id: climate.volcano_hybrid
        data:
          temperature: "{{ temperature }}"
      
      # Turn on heating
      - service: climate.turn_on
        target:
          entity_id: climate.volcano_hybrid
      
      # Wait for temperature
      - wait_for_trigger:
          - platform: event
            event_type: volcano_session_event
            event_data:
              type: temperature_reached
        timeout: "00:10:00"
      
      # Wait specified time
      - delay: "{{ wait_time | default(30) }}"
      
      # Start fan
      - service: fan.turn_on
        target:
          entity_id: fan.volcano_hybrid_fan

# Use script from automations
automation:
  - alias: "Evening Session"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: script.volcano_preset_session
        data:
          temperature: 190
          wait_time: 45
```

**Benefits:**
- Reusable across multiple triggers
- Parameters make scripts flexible
- Easy to test and debug independently

### Pattern 4: **Conditional Logic**
Smart decision making:

```yaml
automation:
  - alias: "Smart Auto Session"
    trigger:
      - platform: state
        entity_id: input_button.auto_session
    action:
      # Choose temperature based on time of day
      - service: climate.set_temperature
        target:
          entity_id: climate.volcano_hybrid
        data:
          temperature: >
            {% set hour = now().hour %}
            {% if hour < 12 %}
              175  # Morning: lower temp
            {% elif hour < 18 %}
              190  # Afternoon: medium temp  
            {% else %}
              200  # Evening: higher temp
            {% endif %}
      
      # Adjust fan timer based on session count
      - service: number.set_value
        target:
          entity_id: number.volcano_fan_timer
        data:
          value: >
            {% set sessions = states('sensor.volcano_sessions_today') | int %}
            {% if sessions < 3 %}
              45  # Longer for early sessions
            {% else %}
              30  # Shorter for later sessions
            {% endif %}
      
      # Start heating
      - service: climate.turn_on
        target:
          entity_id: climate.volcano_hybrid
```

**Benefits:**
- Adapts behavior based on context
- Uses rich sensor data for intelligence
- Single automation handles multiple scenarios

## 🔄 **Composition Patterns**

### Multi-Step Workflows
Chain multiple patterns together:

```yaml
# Step 1: User Input (Pattern 1)
input_select:
  session_type:
    name: "Session Type"
    options:
      - "Quick Session"
      - "Long Session" 
      - "High Temp Session"

# Step 2: Event Monitoring (Pattern 2)  
automation:
  - alias: "Session Type Handler"
    trigger:
      - platform: state
        entity_id: input_select.session_type
    action:
      # Step 3: Script Execution (Pattern 3)
      - service: script.turn_on
        target:
          entity_id: >
            {% if trigger.to_state.state == 'Quick Session' %}
              script.quick_session
            {% elif trigger.to_state.state == 'Long Session' %}
              script.long_session
            {% else %}
              script.high_temp_session
            {% endif %}

# Step 4: Conditional Logic (Pattern 4)
script:
  quick_session:
    sequence:
      - service: script.volcano_preset_session
        data:
          temperature: >
            {{ 180 if states('sensor.volcano_sessions_today') | int < 3 else 185 }}
          wait_time: 20
```

### State Machine Pattern
Complex workflow management:

```yaml
# Track session state
input_select:
  volcano_session_state:
    name: "Session State"
    options:
      - "idle"
      - "heating"
      - "ready"
      - "active"
      - "complete"

# State transitions based on events
automation:
  - alias: "Session State Machine"
    trigger:
      - platform: event
        event_type: volcano_session_event
    action:
      - service: input_select.select_option
        target:
          entity_id: input_select.volcano_session_state
        data:
          option: >
            {% set event_type = trigger.event.data.type %}
            {% if event_type == 'session_started' %}
              heating
            {% elif event_type == 'temperature_reached' %}
              ready
            {% elif event_type == 'fan_started' %}
              active
            {% elif event_type == 'session_ended' %}
              complete
            {% else %}
              {{ states('input_select.volcano_session_state') }}
            {% endif %}

# React to state changes
automation:
  - alias: "Session State Actions"
    trigger:
      - platform: state
        entity_id: input_select.volcano_session_state
    action:
      - choose:
          - conditions:
              - condition: state
                entity_id: input_select.volcano_session_state
                state: "ready"
            sequence:
              - service: notify.mobile_app
                data:
                  message: "Volcano ready for session!"
          - conditions:
              - condition: state
                entity_id: input_select.volcano_session_state
                state: "complete"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.living_room
                data:
                  brightness_pct: 100
```

## 📊 **Data-Driven Patterns**

### Statistics-Based Logic
Use session data for smart decisions:

```yaml
automation:
  - alias: "Usage-Based Recommendations"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_started
    action:
      # Recommend temperature based on history
      - service: notify.mobile_app
        data:
          title: "Session Started"
          message: >
            Session #{{ trigger.event.data.session_count_today }}.
            {% set avg_duration = states('sensor.volcano_average_session_duration') | float %}
            {% if avg_duration > 15 %}
              Your sessions average {{ avg_duration | round(1) }} minutes. 
              Consider a lower temperature for efficiency.
            {% elif avg_duration < 8 %}
              Your quick {{ avg_duration | round(1) }} minute sessions suggest
              you might enjoy a higher temperature.
            {% endif %}
```

### Time-Series Analysis
Track patterns over time:

```yaml
# Log detailed session data
automation:
  - alias: "Session Data Logger"
    trigger:
      - platform: event
        event_type: volcano_session_event
        event_data:
          type: session_ended
    action:
      # CSV logging for analysis
      - service: notify.file
        data:
          filename: /config/volcano_sessions.csv
          message: >
            {{ trigger.event.data.timestamp }},
            {{ trigger.event.data.duration_minutes }},
            {{ trigger.event.data.peak_temperature }},
            {{ trigger.event.data.average_temperature }},
            {{ trigger.event.data.fan_cycles }},
            {{ now().strftime('%A') }},
            {{ now().hour }}

# Weekly analysis
automation:
  - alias: "Weekly Usage Analysis"
    trigger:
      - platform: time
        at: "09:00:00"
      - condition: time
        weekday:
          - sun
    action:
      # Could trigger external analysis script
      - service: shell_command.analyze_volcano_usage
```

## 🎨 **User Experience Patterns**

### Progressive Disclosure
Start simple, add complexity:

```yaml
# Beginner: Simple button
input_button:
  volcano_simple_session:
    name: "Start Session"
    icon: mdi:play

# Intermediate: Choice of presets  
input_select:
  volcano_preset:
    name: "Session Type"
    options:
      - "Light (180°C)"
      - "Medium (190°C)"
      - "Strong (200°C)"

# Advanced: Full control
input_number:
  volcano_custom_temp:
    name: "Custom Temperature"
    min: 160
    max: 230
    unit_of_measurement: "°C"

input_number:
  volcano_wait_time:
    name: "Wait Time"
    min: 0
    max: 300
    unit_of_measurement: "s"
```

### Contextual Interfaces
Adapt UI based on state:

```yaml
# Dynamic dashboard based on volcano state
type: conditional
conditions:
  - entity: sensor.volcano_heat_status
    state: "On"
card:
  type: entities
  title: "Session In Progress"
  entities:
    - sensor.volcano_current_temperature
    - sensor.volcano_target_temperature
    - entity: climate.volcano_hybrid
      name: "Cancel Session"

# Different card when idle
type: conditional  
conditions:
  - entity: sensor.volcano_heat_status
    state: "Off"
card:
  type: horizontal-stack
  cards:
    - type: button
      name: "Quick Session"
      tap_action:
        action: call-service
        service: script.quick_session
    - type: button
      name: "Custom Session"
      tap_action:
        action: navigate
        navigation_path: /volcano-custom
```

## 🚀 **Advanced Patterns**

### Machine Learning Integration
Use HA's ML capabilities:

```yaml
# Predict optimal temperature based on time/usage
bayesian:
  - platform: "template"
    name: "Optimal Temperature Prediction"
    prior: 190
    observations:
      - platform: "numeric_state"
        entity_id: "sensor.volcano_sessions_today"
        below: 3
        prob_given_true: 0.8
        prob_given_false: 0.2
        to_state: 185
      - platform: "time"
        after: "18:00:00"
        prob_given_true: 0.7
        prob_given_false: 0.3
        to_state: 200
```

### External Integration
Connect with other systems:

```yaml
# MQTT bridge for external control
automation:
  - alias: "MQTT Volcano Control"
    trigger:
      - platform: mqtt
        topic: "volcano/command"
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.payload_json.action == 'start_session' }}"
            sequence:
              - service: script.volcano_preset_session
                data:
                  temperature: "{{ trigger.payload_json.temperature | default(190) }}"

  - alias: "MQTT Status Updates"
    trigger:
      - platform: event
        event_type: volcano_session_event
    action:
      - service: mqtt.publish
        data:
          topic: "volcano/status"
          payload: >
            {{
              {
                "type": trigger.event.data.type,
                "temperature": states('sensor.volcano_current_temperature'),
                "session_count": states('sensor.volcano_sessions_today'),
                "timestamp": trigger.event.data.timestamp
              } | to_json
            }}
```

## 💡 **Best Practices**

### 1. **Start Simple, Iterate**
- Begin with basic button + automation
- Add complexity gradually
- Test each piece before combining

### 2. **Use Descriptive Names**
- Clear automation names: "Volcano Evening Session"
- Descriptive input helpers: "volcano_preferred_evening_temp"
- Comment complex logic

### 3. **Error Handling**
```yaml
# Always include error handling
automation:
  - alias: "Safe Volcano Session"
    trigger:
      - platform: state
        entity_id: input_button.volcano_session
    action:
      - condition: state
        entity_id: sensor.volcano_connection_status
        state: "Connected"
      # ... automation logic ...
    mode: single  # Prevent multiple simultaneous runs
```

### 4. **Testing Patterns**
```yaml
# Test automation with notifications
automation:
  - alias: "Test Volcano Logic"
    trigger:
      - platform: state
        entity_id: input_button.test_volcano
    action:
      - service: persistent_notification.create
        data:
          title: "Test Result"
          message: >
            Current temp: {{ states('sensor.volcano_current_temperature') }}
            Target temp: {{ states('sensor.volcano_target_temperature') }}
            Sessions today: {{ states('sensor.volcano_sessions_today') }}
```

### 5. **Documentation**
```yaml
# Document your automations
automation:
  - alias: "My Volcano Session"
    description: >
      Custom session that:
      - Uses preferred temperature based on time of day
      - Adjusts fan timer based on usage count
      - Sends mobile notification when ready
      - Automatically turns off after 30 minutes
    # ... automation logic ...
```

## 🔮 **Future Patterns**

As the integration evolves, new patterns will emerge:
- **AI-powered session optimization**
- **Multi-user preference management**  
- **Cross-device coordination**
- **Predictive maintenance scheduling**
- **Community pattern sharing**

---

**Next Steps:**
- Explore [Automation Examples](Automation-Examples) for complete implementations
- Check [Advanced Patterns](Advanced-Patterns) for complex scenarios
- Join the community to share your building block creations!
