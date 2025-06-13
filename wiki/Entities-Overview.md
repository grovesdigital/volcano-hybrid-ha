# Entities Overview

The Volcano Hybrid integration creates multiple entities across different platforms. This page provides a comprehensive overview of all available entities and their purposes.

## 🌡️ **Climate Platform**

### `climate.volcano_hybrid`
**Main temperature control entity**

| Property | Value |
|----------|-------|
| **Device Class** | `None` (Thermostat) |
| **HVAC Modes** | `off`, `heat` |
| **Temperature Range** | 40°C - 230°C |
| **Temperature Step** | 1°C |
| **Features** | Temperature setting, heat on/off |

**Usage:**
```yaml
# Set temperature
service: climate.set_temperature
target:
  entity_id: climate.volcano_hybrid
data:
  temperature: 190

# Turn heating on/off
service: climate.set_hvac_mode
target:
  entity_id: climate.volcano_hybrid
data:
  hvac_mode: heat  # or 'off'
```

## 💨 **Fan Platform**

### `fan.volcano_hybrid_fan`
**Fan control with timer support**

| Property | Value |
|----------|-------|
| **Speed Modes** | `off`, `on` |
| **Timer Support** | Yes (via `number.volcano_fan_timer`) |
| **Features** | On/off, timer integration |

**Usage:**
```yaml
# Turn fan on
service: fan.turn_on
target:
  entity_id: fan.volcano_hybrid_fan

# Turn fan on with specific duration
service: fan.turn_on
target:
  entity_id: fan.volcano_hybrid_fan
data:
  duration: 30  # seconds
```

## 📊 **Sensor Platform**

### Temperature Sensors

#### `sensor.volcano_current_temperature`
| Property | Value |
|----------|-------|
| **Device Class** | `temperature` |
| **Unit** | `°C` |
| **Update Frequency** | Dynamic (1-5s based on activity) |
| **Description** | Real-time device temperature |

#### `sensor.volcano_target_temperature`  
| Property | Value |
|----------|-------|
| **Device Class** | `temperature` |
| **Unit** | `°C` |
| **Update Frequency** | On change |
| **Description** | Currently set target temperature |

### Status Sensors

#### `sensor.volcano_connection_status`
| Property | Value |
|----------|-------|
| **States** | `Connected`, `Disconnected`, `Connecting` |
| **Icon** | Dynamic (bluetooth/bluetooth-off) |
| **Description** | Bluetooth connection status |

#### `sensor.volcano_heat_status`
| Property | Value |
|----------|-------|
| **States** | `On`, `Off` |
| **Icon** | Dynamic (fire/fire-off) |
| **Description** | Real-time heating status |

#### `sensor.volcano_fan_status`
| Property | Value |
|----------|-------|
| **States** | `On`, `Off` |
| **Icon** | Dynamic (fan/fan-off) |
| **Description** | Real-time fan status |

### Device Information Sensors

#### `sensor.volcano_total_operation_time`
| Property | Value |
|----------|-------|
| **Format** | `"5d 14h 23m"` (human-readable) |
| **Device Class** | `duration` |
| **Attributes** | `total_hours`, `total_minutes`, `days`, `hours`, `minutes` |
| **Description** | Total device runtime |

#### `sensor.volcano_firmware_version`
| Property | Value |
|----------|-------|
| **Format** | `"1.2.3"` |
| **Update Frequency** | Every 10 minutes |
| **Description** | Device firmware version |

#### `sensor.volcano_ble_firmware_version`
| Property | Value |
|----------|-------|
| **Format** | `"2.1.0"` |
| **Update Frequency** | Every 10 minutes |
| **Description** | Bluetooth firmware version |

#### `sensor.volcano_serial_number`
| Property | Value |
|----------|-------|
| **Format** | `"VH-XXXXXX"` |
| **Update Frequency** | Every 10 minutes |
| **Description** | Device serial number |

### Session Statistics Sensors

#### `sensor.volcano_sessions_today`
| Property | Value |
|----------|-------|
| **Unit** | Sessions |
| **Reset** | Daily at midnight |
| **Icon** | `mdi:counter` |
| **Description** | Number of sessions today |

#### `sensor.volcano_total_sessions`
| Property | Value |
|----------|-------|
| **Unit** | Sessions |
| **Persistence** | Lifetime counter |
| **Icon** | `mdi:chart-line` |
| **Description** | Total sessions since integration installed |

#### `sensor.volcano_last_session_duration`
| Property | Value |
|----------|-------|
| **Unit** | Minutes |
| **Device Class** | `duration` |
| **Icon** | `mdi:timer` |
| **Description** | Duration of most recent session |

#### `sensor.volcano_average_session_duration`
| Property | Value |
|----------|-------|
| **Unit** | Minutes |
| **Device Class** | `duration` |
| **Icon** | `mdi:chart-timeline-variant` |
| **Description** | Average duration over last 100 sessions |

#### `sensor.volcano_time_since_last_use`
| Property | Value |
|----------|-------|
| **Format** | Human-readable ("2 hours ago") |
| **Update Frequency** | Every minute |
| **Icon** | `mdi:clock-outline` |
| **Description** | Time elapsed since last session |

## 🔢 **Number Platform**

### `number.volcano_fan_timer`
**Fan timer duration setting**

| Property | Value |
|----------|-------|
| **Range** | 5 - 300 seconds |
| **Step** | 5 seconds |
| **Default** | 36 seconds |
| **Unit** | `s` |
| **Description** | Fan auto-shutoff timer |

**Usage:**
```yaml
# Set fan timer to 45 seconds
service: number.set_value
target:
  entity_id: number.volcano_fan_timer
data:
  value: 45
```

### `number.volcano_screen_brightness`
**Display brightness control**

| Property | Value |
|----------|-------|
| **Range** | 0 - 100% |
| **Step** | 5% |
| **Default** | 50% |
| **Unit** | `%` |
| **Description** | Device display brightness |

## 🔘 **Button Platform**

### Button Entities
Currently, button entities are **not automatically created**. The integration follows a building blocks philosophy - you create your own button helpers and automations.

**Why no built-in buttons?**
- Different users want different temperature presets
- Button workflows vary significantly between users
- Building blocks approach provides maximum flexibility

**Creating Your Own Buttons:**
See [Automation Examples](Automation-Examples) for creating custom button helpers and workflows.

## 📈 **Entity Attributes**

Many entities include additional attributes beyond their main state:

### Climate Entity Attributes
```yaml
# climate.volcano_hybrid attributes
current_temperature: 65
temperature: 190
hvac_mode: heat
hvac_modes: [off, heat]
supported_features: 1
friendly_name: "Volcano Hybrid"
```

### Operation Time Attributes
```yaml
# sensor.volcano_total_operation_time attributes
total_hours: 1247
total_minutes: 74820
days: 51
hours: 23
minutes: 0
friendly_name: "Volcano Total Operation Time"
```

### Session Statistics Attributes
```yaml
# sensor.volcano_sessions_today attributes
reset_time: "2025-06-13T00:00:00"
last_session_start: "2025-06-13T14:30:00"
last_session_end: "2025-06-13T14:42:18"
friendly_name: "Volcano Sessions Today"
```

## 🎯 **Entity Usage Patterns**

### Dashboard Display
```yaml
# Basic entities card
type: entities
entities:
  - climate.volcano_hybrid
  - fan.volcano_hybrid_fan
  - sensor.volcano_current_temperature
  - sensor.volcano_sessions_today
  - number.volcano_fan_timer
title: "Volcano Control"
```

### Status Overview
```yaml
# Status grid
type: grid
square: false
columns: 2
cards:
  - type: stat
    entity: sensor.volcano_current_temperature
    name: "Current Temp"
  - type: stat
    entity: sensor.volcano_target_temperature  
    name: "Target Temp"
  - type: stat
    entity: sensor.volcano_sessions_today
    name: "Sessions Today"
  - type: stat
    entity: sensor.volcano_time_since_last_use
    name: "Last Use"
```

### Automation Triggers
```yaml
# Using entities in automations
automation:
  - alias: "Temperature Reached"
    trigger:
      - platform: template
        value_template: >
          {{ states('sensor.volcano_current_temperature') | int >= 
             (states('sensor.volcano_target_temperature') | int - 5) }}
    action:
      - service: notify.mobile_app
        data:
          message: "Volcano ready at {{ states('sensor.volcano_current_temperature') }}°C"
```

## 🔄 **Update Frequencies**

The integration uses **dynamic update intervals** based on device activity:

| Device State | Update Interval | Entities Affected |
|--------------|----------------|-------------------|
| **Fan On** | 1 second | Temperature, status sensors |
| **Heating (close to target)** | 1 second | Temperature, status sensors |  
| **Heating (far from target)** | 2 seconds | Temperature, status sensors |
| **Cooling down** | 3 seconds | Temperature, status sensors |
| **Idle/Cold** | 5 seconds | Temperature, status sensors |
| **Device Info** | 10 minutes | Firmware, serial number |
| **Statistics** | On change | Session counters |

## 🎨 **Customization**

All entities can be customized in Home Assistant:

### Renaming Entities
```yaml
# customize.yaml
sensor.volcano_current_temperature:
  friendly_name: "Volcano Temperature"
  icon: mdi:thermometer-high

climate.volcano_hybrid:
  friendly_name: "My Volcano"
```

### Creating Template Sensors
```yaml
# configuration.yaml
template:
  - sensor:
      - name: "Volcano Status Summary"
        state: >
          {% if is_state('sensor.volcano_heat_status', 'On') %}
            Heating to {{ states('sensor.volcano_target_temperature') }}°C
          {% elif is_state('sensor.volcano_fan_status', 'On') %}
            Fan Running
          {% else %}
            Idle ({{ states('sensor.volcano_current_temperature') }}°C)
          {% endif %}
```

---

**Next**: Learn how to use these entities in [Automation Examples](Automation-Examples) or dive deeper into specific platforms like [Sensors](Sensors) or [Climate Control](Climate-Control).
