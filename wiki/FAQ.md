# Frequently Asked Questions (FAQ)

Quick answers to common questions about the Volcano Hybrid Home Assistant integration.

## 🔧 **Installation & Setup**

### Q: Which Home Assistant installation methods are supported?
**A:** All installation methods are supported:
- ✅ **Home Assistant OS** (recommended)
- ✅ **Home Assistant Supervised** 
- ✅ **Home Assistant Container** (requires Bluetooth access)
- ✅ **Home Assistant Core** (manual Bluetooth setup required)

### Q: Do I need HACS to install this integration?
**A:** No, manual installation is fully supported. HACS support is planned for future releases.

### Q: What Bluetooth adapters work best?
**A:** Most modern Bluetooth adapters work fine:
- **Built-in Bluetooth**: Usually works great on modern hardware
- **USB Adapters**: Any Bluetooth 4.0+ adapter should work
- **Recommended**: USB adapters with external antenna for better range
- **Range**: Keep within 3-5 meters for reliable connection

### Q: Can I use this with the original Volcano Classic?
**A:** No, this integration is specifically for the **Volcano Hybrid**. The Classic doesn't have Bluetooth connectivity.

### Q: Why can't the integration find my Volcano?
**A:** Most common causes:
1. **Device powered off**: Ensure Volcano is on
2. **Not discoverable**: Check device is in pairing/discoverable mode
3. **Range**: Move Home Assistant host closer to device
4. **Bluetooth disabled**: Verify Bluetooth is enabled in HA
5. **Wrong model**: Confirm you have Volcano Hybrid, not Classic

## 🎯 **Features & Functionality**

### Q: What entities does the integration create?
**A:** The integration creates:
- **1 Climate entity**: Temperature control and heating
- **1 Fan entity**: Fan control with timer
- **2 Number entities**: Fan timer and screen brightness
- **10+ Sensor entities**: Temperature, status, and statistics
- **0 Button entities**: Following building blocks philosophy

### Q: Why are there no built-in preset temperature buttons?
**A:** By design! The integration follows a **building blocks philosophy**:
- Different users want different temperatures
- Button workflows vary significantly
- You can easily create your own preset buttons using input helpers
- Maximum flexibility for custom automation

See [Automation Examples](Automation-Examples) for creating custom presets.

### Q: How often does the integration update sensor data?
**A:** The integration uses **dynamic update intervals**:
- **1 second**: During fan operation or approaching target temperature
- **2 seconds**: When actively heating
- **3 seconds**: When cooling down
- **5 seconds**: When idle/cold
- **10 minutes**: Device information (firmware, serial number)

### Q: What's the difference between session tracking and operation time?
**A:** 
- **Session tracking**: Counts user sessions (heating cycles) with start/end times
- **Operation time**: Total device runtime from the Volcano's internal counter
- **Sessions today**: Resets daily at midnight
- **Total sessions**: Lifetime counter since integration installed
- **Operation time**: Hardware counter, never resets

## 🤖 **Automation & Events**

### Q: What events does the integration fire?
**A:** The integration fires `volcano_session_event` with these types:
- `session_started`: Heating begins
- `temperature_reached`: Target temperature achieved  
- `fan_started`: Fan turned on
- `fan_stopped`: Fan turned off
- `session_ended`: Session complete (cooling down)

Each event includes rich data like temperatures, durations, and session counts.

### Q: Can I build my own automation workflows?
**A:** Absolutely! That's the whole point. The integration provides:
- **Rich sensor data** for decision making
- **Comprehensive events** for automation triggers
- **Flexible controls** for device operation
- **Professional documentation** with examples

See [Automation Examples](Automation-Examples) and [Building Blocks](Building-Blocks).

### Q: How do I create temperature preset buttons?
**A:** Use input button helpers:
```yaml
# configuration.yaml
input_button:
  volcano_preset_190:
    name: "Volcano 190°C"
    icon: mdi:thermometer

# automation
automation:
  - alias: "Volcano 190°C Preset"
    trigger:
      - platform: state
        entity_id: input_button.volcano_preset_190
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.volcano_hybrid
        data:
          temperature: 190
```

### Q: Can I schedule automatic sessions?
**A:** Yes! Use time-based automations:
```yaml
automation:
  - alias: "Evening Session"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.volcano_hybrid
        data:
          temperature: 190
      - service: climate.turn_on
        target:
          entity_id: climate.volcano_hybrid
```

## 📊 **Statistics & Monitoring**

### Q: How accurate is session detection?
**A:** Very accurate with these criteria:
- **Session start**: Temperature rises from <50°C to >100°C
- **Session end**: Temperature drops below 60°C or heating turned off
- **Minimum duration**: 60 seconds to filter false positives
- **Manual override**: Heating on/off also triggers session events

### Q: Why is my session count different from what I expect?
**A:** Common reasons:
- **False starts**: Brief heating that doesn't reach temperature
- **Multiple cycles**: Heating on/off multiple times counts as separate sessions
- **Timing**: Sessions are counted when they actually start, not when planned
- **Reset timing**: Daily counter resets at midnight system time

### Q: Can I export session data for analysis?
**A:** Yes, several ways:
- **Home Assistant history**: Built-in statistics tracking
- **Event logging**: Capture events to files or external systems
- **CSV export**: Create automations that log to CSV files
- **Database**: HA stores all data in SQLite/PostgreSQL

### Q: How far back does statistics data go?
**A:** Depends on setup:
- **Sensor states**: HA's default retention (10 days history, 10 days statistics)
- **Long-term statistics**: Can be kept indefinitely
- **Event data**: Stored in HA database with same retention
- **Custom logging**: You control retention with your automations

## 🔌 **Connection & Performance**

### Q: Why does the connection drop sometimes?
**A:** Common causes and solutions:
- **Range**: Move HA host closer to Volcano
- **Interference**: Reduce WiFi/microwave interference
- **Power saving**: Disable USB power management on Linux
- **Multiple connections**: Only connect from one device at a time
- **Device sleep**: Volcano may sleep after inactivity

### Q: Can I connect multiple Home Assistant instances?
**A:** No, the Volcano can only maintain one Bluetooth connection at a time. Multiple HA instances will conflict.

### Q: Does the integration work with Volcano through WiFi?
**A:** No, the Volcano Hybrid only supports Bluetooth LE connectivity. There's no WiFi option.

### Q: Why is the integration slow to respond sometimes?
**A:** Performance factors:
- **Update intervals**: Integration automatically optimizes based on activity
- **Bluetooth latency**: BLE has inherent latency (1-2 seconds normal)
- **HA performance**: Check overall HA system performance
- **Distance**: Bluetooth range affects response time

### Q: Can I use this with other Bluetooth devices simultaneously?
**A:** Yes, the integration shares Bluetooth properly. However:
- Don't connect other apps to the Volcano simultaneously
- Heavy Bluetooth traffic may slow responses
- USB Bluetooth adapters generally handle multiple devices better

## 🛠️ **Troubleshooting**

### Q: Integration setup says "already configured" but I don't see it?
**A:** The v1.2.0+ integration handles this gracefully. If issues persist:
1. Remove any existing integration completely
2. Restart Home Assistant
3. Check for lingering entities in Developer Tools → States
4. Try setup again

### Q: Entities show "Unknown" or "Unavailable"?
**A:** Check:
- Bluetooth connection status (`sensor.volcano_connection_status`)
- Device is powered on and in range
- HA logs for connection errors
- Try restarting the integration

### Q: Temperature readings don't match the device display?
**A:** This can happen due to:
- **Sensor location**: Internal vs display temperature may differ
- **Update timing**: Slight delays in Bluetooth communication
- **Calibration**: Some units may need calibration offset
- **Units**: Verify both are using Celsius

### Q: Events aren't firing for my automations?
**A:** Debug steps:
1. Check **Developer Tools** → **Events** for `volcano_session_event`
2. Verify session detection criteria are met
3. Test with simple automation that just creates notifications
4. Check automation conditions and triggers

### Q: Fan timer doesn't work?
**A:** Troubleshooting:
- Verify `number.volcano_fan_timer` is set to desired value
- Check fan entity state changes correctly
- Device may have its own timer that overrides integration
- Create backup timer automation if needed

## 🔮 **Future Features**

### Q: Will there be HACS support?
**A:** Yes, HACS submission is planned for a future release.

### Q: Any plans for cloud connectivity or remote access?
**A:** No plans for cloud features. The integration is designed for local control only, which is more reliable and private.

### Q: Will you add support for other Storz & Bickel devices?
**A:** Possibly! If there's demand and the devices have accessible APIs, other products could be supported.

### Q: Can you add automatic cleaning reminders?
**A:** This is possible and being considered. The integration already tracks usage statistics that could trigger maintenance reminders.

### Q: Will there be a mobile app?
**A:** No dedicated app planned. The integration works perfectly with the Home Assistant mobile app for full remote control.

## 🤝 **Community & Support**

### Q: How can I contribute to the project?
**A:** Several ways:
- **Bug reports**: Open GitHub issues with detailed information
- **Feature requests**: Suggest improvements via GitHub
- **Documentation**: Help improve wiki and examples
- **Code**: Submit pull requests for bug fixes or features
- **Community**: Help other users in forums and Discord

### Q: Where can I get help if I'm stuck?
**A:** Support channels:
- **GitHub Issues**: Technical problems and bug reports
- **Home Assistant Community**: General discussion and help
- **Discord**: Real-time chat with HA community
- **Reddit**: r/homeassistant for broader discussion

### Q: Can I hire someone to set this up for me?
**A:** While the developer doesn't offer setup services, many Home Assistant integrators and smart home professionals can help. Check local home automation installers.

### Q: Is commercial use allowed?
**A:** Yes, the integration uses the MIT license which allows commercial use. Please review the license terms for full details.

## 💡 **Tips & Best Practices**

### Q: What's the best way to organize Volcano automations?
**A:** Recommended structure:
- **Input helpers**: Group all volcano-related helpers
- **Automations**: Use clear naming and descriptions
- **Scripts**: Break complex workflows into reusable scripts
- **Dashboard**: Create dedicated volcano control panel
- **Documentation**: Comment your automations for future reference

### Q: How can I make the most of the statistics features?
**A:** Ideas:
- Set up daily/weekly usage reports
- Create charts showing usage patterns
- Build maintenance reminders based on sessions/time
- Track efficiency (temperature reached vs target)
- Monitor for unusual usage patterns

### Q: Any security considerations?
**A:** Best practices:
- **Local only**: Integration doesn't connect to internet
- **Bluetooth range**: Keep HA host secure since it controls device
- **Access control**: Use HA's user management for multi-user setups
- **Automation safety**: Consider maximum daily session limits
- **Data privacy**: All data stays local unless you explicitly export it

---

**Didn't find your answer?** Check the [Troubleshooting](Troubleshooting) guide or open a [GitHub issue](https://github.com/grovesdigital/volcano-hybrid-ha/issues).
