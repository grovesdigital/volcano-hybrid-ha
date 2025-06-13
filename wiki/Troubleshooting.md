# Troubleshooting Guide

This guide helps resolve common issues with the Volcano Hybrid Home Assistant integration. Most problems fall into a few categories: connectivity, configuration, or performance issues.

## 🔍 **Quick Diagnostics**

### Integration Health Check
1. **Go to Settings** → **Devices & Services** → **Volcano Hybrid**
2. **Check Entity Status**:
   - `sensor.volcano_connection_status` should show "Connected"
   - Temperature sensors should show real values (not "Unknown")
   - Entities should update regularly

3. **Test Basic Functions**:
   - Set temperature via climate entity
   - Turn fan on/off
   - Check that changes appear on device

### Log Analysis
Enable debugging to see detailed logs:
```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.volcano_hybrid: debug
    homeassistant.components.bluetooth: debug
```

## 🔌 **Connection Issues**

### Problem: Integration Can't Find Device

**Symptoms:**
- "No devices found" during setup
- Integration setup fails immediately
- Bluetooth discovery doesn't work

**Solutions:**

#### 1. Check Bluetooth Setup
```bash
# Test Bluetooth on HA host
bluetoothctl
power on
scan on
# Look for "VOLCANO" device
```

#### 2. Verify Device State
- **Power on** your Volcano Hybrid
- Check device is in **discoverable mode**
- **Distance**: Move HA host closer to Volcano
- **Interference**: Turn off other Bluetooth devices temporarily

#### 3. Manual MAC Address Discovery
```python
# Run on HA host or similar system
import asyncio
from bleak import BleakScanner

async def scan_for_volcano():
    devices = await BleakScanner.discover(timeout=10.0)
    for device in devices:
        if device.name and "VOLCANO" in device.name.upper():
            print(f"Found: {device.name} - {device.address}")

asyncio.run(scan_for_volcano())
```

#### 4. USB Bluetooth Issues (Docker/Supervised)
```yaml
# docker-compose.yml
services:
  homeassistant:
    devices:
      - /dev/bus/usb:/dev/bus/usb
    privileged: true
    # or specific capabilities:
    cap_add:
      - NET_ADMIN
      - SYS_ADMIN
```

### Problem: "Already Configured" Error

**Symptoms:**
- Setup fails with "already_configured" error
- Can't add integration even after removal
- Discovery keeps failing

**Solutions:**

#### 1. Complete Integration Removal
1. **Remove Integration**: Settings → Devices & Services → Volcano Hybrid → Delete
2. **Clear Entity Registry**: Developer Tools → States → Clear any lingering `volcano_*` entities
3. **Restart HA**: Full restart required
4. **Re-add Integration**: Should work cleanly now

#### 2. Manual Registry Cleanup (Advanced)
```bash
# Stop Home Assistant first!
cd /config/.storage/
cp core.config_entries core.config_entries.backup
# Edit core.config_entries to remove volcano entries
# Restart HA
```

#### 3. Force New Unique ID
The integration now handles this automatically, but if issues persist:
1. Power cycle the Volcano device
2. Wait 5 minutes for Bluetooth cache to clear
3. Try setup again

### Problem: Connection Drops Frequently

**Symptoms:**
- `sensor.volcano_connection_status` shows "Disconnected"
- Entities become "Unknown" regularly
- Automation triggers inconsistently

**Solutions:**

#### 1. Optimize Update Intervals
```python
# The integration already uses dynamic intervals, but you can verify:
# Check coordinator update intervals in logs
```

#### 2. Bluetooth Range/Interference
- **Move closer**: HA host within 3-5 meters of Volcano
- **Reduce interference**: Move away from WiFi routers, microwaves
- **Use USB extension**: Move Bluetooth adapter away from HA host
- **Update drivers**: Ensure latest Bluetooth drivers

#### 3. Power Management (Linux)
```bash
# Disable USB power management for Bluetooth
echo 'on' > /sys/bus/usb/devices/*/power/control
# Or add to systemd service
```

## ⚙️ **Configuration Issues**

### Problem: Entities Not Updating

**Symptoms:**
- Temperature sensors stuck at old values
- Statistics not incrementing
- Events not firing

**Solutions:**

#### 1. Check Update Intervals
The integration uses dynamic intervals:
- **Active (heating/fan)**: 1-2 seconds
- **Idle**: 5 seconds
- **Device info**: 10 minutes

If updates seem slow, check device activity state.

#### 2. Verify Event System
```yaml
# Test automation to verify events
automation:
  - alias: "Debug Volcano Events"
    trigger:
      - platform: event
        event_type: volcano_session_event
    action:
      - service: persistent_notification.create
        data:
          title: "Volcano Event"
          message: "Event: {{ trigger.event.data.type }}"
```

#### 3. Force Entity Updates
```yaml
# Manual entity update service call
service: homeassistant.update_entity
target:
  entity_id: sensor.volcano_current_temperature
```

### Problem: Statistics Not Tracking

**Symptoms:**
- `sensor.volcano_sessions_today` stays at 0
- Session durations not recorded
- Time since last use not updating

**Solutions:**

#### 1. Check Session Detection Logic
Session detection requires:
- Temperature increase from <50°C to >100°C (session start)
- Temperature decrease to <60°C (session end)
- Or explicit heating on/off

Force a test session:
1. Ensure Volcano is cold (<50°C)
2. Set temperature to 180°C
3. Turn heating on
4. Wait for session_started event

#### 2. Verify Event Data
Use **Developer Tools** → **Events**:
- Listen for `volcano_session_event`
- Check event data includes session counters
- Verify timestamps are correct

#### 3. Reset Statistics (if corrupted)
```yaml
# Reset daily counter at midnight
automation:
  - alias: "Reset Daily Stats"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: homeassistant.update_entity
        target:
          entity_id: sensor.volcano_sessions_today
```

## 🚀 **Performance Issues**

### Problem: Slow Response Times

**Symptoms:**
- Long delay between command and device response
- Temperature updates lag behind actual device
- Fan control feels sluggish

**Solutions:**

#### 1. Check Update Intervals
The integration should automatically use faster intervals when active:
```python
# Verify in logs - should see messages like:
# "Update interval changed to 1 seconds"
```

#### 2. Bluetooth Performance
```bash
# Check Bluetooth adapter capabilities
hciconfig -a
# Look for "Up RUNNING" status

# Test connection latency
hcitool ping XX:XX:XX:XX:XX:XX
```

#### 3. Home Assistant Performance
```yaml
# Check HA performance
sensor:
  - platform: systemmonitor
    resources:
      - type: processor_use
      - type: memory_use_percent
```

### Problem: High CPU/Memory Usage

**Symptoms:**
- HA becomes sluggish after adding integration
- High CPU usage from python3 processes
- Memory usage climbing over time

**Solutions:**

#### 1. Optimize Polling
The integration uses efficient dynamic polling, but verify:
- No manual `homeassistant.update_entity` automation loops
- No excessive event-based automations
- Update intervals are appropriate

#### 2. Check for Memory Leaks
```bash
# Monitor HA memory usage
watch -n 30 'ps aux | grep home-assistant'
```

#### 3. Restart Integration
```yaml
# Reload integration without restarting HA
service: homeassistant.reload_config_entry
target:
  entity_id: climate.volcano_hybrid
```

## 📱 **Automation Issues**

### Problem: Automations Not Triggering

**Symptoms:**
- Event-based automations don't fire
- Entity state changes don't trigger automations
- Template automations fail

**Solutions:**

#### 1. Test Event Triggers
```yaml
# Simple test automation
automation:
  - alias: "Test Volcano Trigger"
    trigger:
      - platform: state
        entity_id: sensor.volcano_current_temperature
    action:
      - service: persistent_notification.create
        data:
          message: "Temperature changed to {{ trigger.to_state.state }}"
```

#### 2. Check Automation Conditions
```yaml
# Add debugging to existing automation
action:
  - service: persistent_notification.create
    data:
      message: "Automation triggered: {{ trigger.event.data }}"
  # ... rest of automation
```

#### 3. Template Debugging
```yaml
# Test templates in Developer Tools → Template
{{ states('sensor.volcano_current_temperature') | int >= 
   (states('sensor.volcano_target_temperature') | int - 5) }}
```

### Problem: Template Errors

**Symptoms:**
- "Template Error" in logs
- Automations fail with template issues
- Dashboard cards show errors

**Solutions:**

#### 1. Safe Template Patterns
```yaml
# Bad: Can fail if entity is unavailable
temperature: "{{ states('sensor.volcano_current_temperature') | int }}"

# Good: Safe defaults
temperature: "{{ states('sensor.volcano_current_temperature') | int(0) }}"

# Better: Availability check
temperature: >
  {% if states('sensor.volcano_current_temperature') not in ['unavailable', 'unknown'] %}
    {{ states('sensor.volcano_current_temperature') | int }}
  {% else %}
    0
  {% endif %}
```

#### 2. Entity Availability
```yaml
# Check entity availability in conditions
condition:
  - condition: template
    value_template: >
      {{ states('sensor.volcano_current_temperature') not in 
         ['unavailable', 'unknown', 'none'] }}
```

## 🔧 **Device-Specific Issues**

### Problem: Fan Timer Not Working

**Symptoms:**
- Fan runs indefinitely
- Timer setting ignored
- Fan doesn't auto-stop

**Solutions:**

#### 1. Check Timer Value
```yaml
# Verify timer is set properly
- service: number.set_value
  target:
    entity_id: number.volcano_fan_timer
  data:
    value: 36  # 36 seconds
```

#### 2. Manual Fan Stop Automation
```yaml
# Backup timer automation
automation:
  - alias: "Manual Fan Timer"
    trigger:
      - platform: state
        entity_id: fan.volcano_hybrid_fan
        to: "on"
    action:
      - delay: "{{ states('number.volcano_fan_timer') | int }}"
      - condition: state
        entity_id: fan.volcano_hybrid_fan
        state: "on"
      - service: fan.turn_off
        target:
          entity_id: fan.volcano_hybrid_fan
```

### Problem: Temperature Readings Inaccurate

**Symptoms:**
- Temperature doesn't match device display
- Readings seem delayed or incorrect
- Calibration issues

**Solutions:**

#### 1. Sensor Calibration
```yaml
# Create calibrated sensor
template:
  - sensor:
      - name: "Volcano Temperature Calibrated"
        state: "{{ (states('sensor.volcano_current_temperature') | float) + 2.5 }}"
        unit_of_measurement: "°C"
        device_class: temperature
```

#### 2. Compare with Device
- Check readings match device display
- Verify temperature units (should be Celsius)
- Test across temperature range

## 🚨 **Emergency Procedures**

### Complete Integration Reset

If all else fails, complete reset procedure:

#### 1. Full Backup
```bash
# Backup HA configuration
tar -czf ha_backup_$(date +%Y%m%d).tar.gz /config/
```

#### 2. Remove Integration
1. Settings → Devices & Services → Volcano Hybrid → Delete
2. Remove custom_components/volcano_hybrid folder
3. Clear `.storage/core.config_entries` entries
4. Remove any volcano automations/dashboards

#### 3. Clean Restart
1. Restart Home Assistant
2. Verify no volcano entities remain
3. Re-install integration fresh
4. Test basic functionality

### Emergency Device Shutoff

```yaml
# Emergency automation to turn off volcano
automation:
  - alias: "Emergency Volcano Shutoff"
    trigger:
      - platform: state
        entity_id: input_boolean.emergency_shutoff
        to: "on"
    action:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.volcano_hybrid
        data:
          hvac_mode: "off"
      - service: fan.turn_off
        target:
          entity_id: fan.volcano_hybrid_fan
      - service: notify.mobile_app_your_phone
        data:
          title: "Emergency Shutoff Activated"
          message: "Volcano has been turned off immediately"
```

## 📞 **Getting Help**

### Information to Provide

When asking for help, include:

1. **Home Assistant Version**: Check Settings → About
2. **Integration Version**: Check HACS or custom_components
3. **Device Model**: Confirm Volcano Hybrid (not Classic)
4. **Host Platform**: HA OS, Supervised, Docker, Core
5. **Bluetooth Adapter**: Built-in or USB, make/model
6. **Error Logs**: Full error messages with timestamps
7. **Configuration**: Relevant YAML (sanitize sensitive data)

### Support Channels

- **GitHub Issues**: [volcano-hybrid-ha/issues](https://github.com/grovesdigital/volcano-hybrid-ha/issues)
- **Home Assistant Community**: [community.home-assistant.io](https://community.home-assistant.io)
- **Reddit**: r/homeassistant
- **Discord**: Home Assistant Discord server

### Debug Information Collection

```yaml
# Enable comprehensive logging
logger:
  default: warning
  logs:
    custom_components.volcano_hybrid: debug
    homeassistant.components.bluetooth: debug
    homeassistant.components.climate: debug
    homeassistant.helpers.entity: debug
```

---

**Still having issues?** Open a [GitHub issue](https://github.com/grovesdigital/volcano-hybrid-ha/issues) with detailed information about your problem.
