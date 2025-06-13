# Installation Guide

This guide walks you through installing the Volcano Hybrid integration in Home Assistant.

## 📋 **Prerequisites**

### Hardware Requirements
- **Volcano Hybrid vaporizer** (Storz & Bickel)
- **Home Assistant** with Bluetooth support
- **Bluetooth adapter** on your HA host (built-in or USB)

### Software Requirements
- **Home Assistant**: 2023.1 or later
- **Bluetooth Integration**: Enabled in HA
- **Python**: 3.11+ (automatically handled by HA)

### Supported Platforms
- **Home Assistant OS** ✅
- **Home Assistant Supervised** ✅  
- **Home Assistant Container** ✅ (with Bluetooth access)
- **Home Assistant Core** ✅ (manual Bluetooth setup required)

## 🔧 **Installation Methods**

### Method 1: Manual Installation (Current)

#### Step 1: Download the Integration
1. Go to the [GitHub repository](https://github.com/grovesdigital/volcano-hybrid-ha)
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file

#### Step 2: Copy Files
1. Copy the `volcano_hybrid` folder to:
   ```
   /config/custom_components/volcano_hybrid/
   ```

2. Your directory structure should look like:
   ```
   config/
   └── custom_components/
       └── volcano_hybrid/
           ├── __init__.py
           ├── manifest.json
           ├── config_flow.py
           ├── climate.py
           ├── fan.py
           ├── sensor.py
           ├── number.py
           ├── button.py
           ├── diagnostics.py
           ├── strings.json
           ├── services.yaml
           └── volcano/
               ├── api.py
               ├── exceptions.py
               └── statistics.py
   ```

#### Step 3: Restart Home Assistant
1. Go to **Settings** → **System** → **Restart**
2. Wait for HA to fully restart

#### Step 4: Add Integration
1. Go to **Settings** → **Devices & Services**
2. Click **"Add Integration"**
3. Search for **"Volcano Hybrid"**
4. Follow the setup wizard

### Method 2: HACS Installation (Future)

> **Note**: HACS submission is planned for a future release

1. Open **HACS** → **Integrations**
2. Search for **"Volcano Hybrid"**
3. Click **"Install"**
4. Restart Home Assistant
5. Add integration via **Settings** → **Devices & Services**

## 🔍 **Device Discovery**

### Automatic Discovery
The integration can automatically discover your Volcano via Bluetooth:

1. **Power on** your Volcano Hybrid
2. Ensure it's in **discoverable mode**
3. The integration will detect it automatically
4. Follow the setup prompts

### Manual Setup
If automatic discovery doesn't work:

1. Find your Volcano's **MAC address**:
   ```bash
   # On Linux/macOS:
   bluetoothctl
   scan on
   # Look for "VOLCANO" device
   
   # Or use the included script:
   python3 getMacAddress.py
   ```

2. During setup, choose **"Manual Entry"**
3. Enter MAC address in format: `XX:XX:XX:XX:XX:XX`

## ✅ **Verification**

After installation, verify everything works:

### Check Entities
Go to **Settings** → **Devices & Services** → **Volcano Hybrid**

You should see entities like:
- `climate.volcano_hybrid`
- `fan.volcano_hybrid_fan`
- `sensor.volcano_current_temperature`
- `sensor.volcano_sessions_today`

### Test Connection
1. Try setting a temperature via the climate entity
2. Check that `sensor.volcano_connection_status` shows "Connected"
3. Monitor `sensor.volcano_current_temperature` for updates

### Test Automation
Create a simple test automation:
```yaml
automation:
  - alias: "Test Volcano Connection"
    trigger:
      - platform: numeric_state
        entity_id: sensor.volcano_current_temperature
        above: 100
    action:
      - service: notify.persistent_notification
        data:
          message: "Volcano is heating! Temperature: {{ states('sensor.volcano_current_temperature') }}°C"
```

## 🚨 **Common Installation Issues**

### Integration Not Found
**Problem**: Can't find "Volcano Hybrid" in Add Integration
**Solution**: 
- Verify files are in correct location
- Restart Home Assistant completely
- Check `configuration.yaml` for syntax errors

### Bluetooth Issues
**Problem**: Can't discover or connect to device
**Solution**:
- Check Bluetooth is enabled: **Settings** → **System** → **Hardware**
- Ensure device is powered and discoverable
- Try moving HA host closer to Volcano
- Restart Bluetooth service

### Permission Errors
**Problem**: "Permission denied" when accessing Bluetooth
**Solution**:
- Add HA user to `bluetooth` group (Linux)
- Check Docker has Bluetooth access (Container install)
- Verify USB Bluetooth adapter is recognized

### Already Configured Error
**Problem**: "Device already configured" during setup
**Solution**:
- The integration now handles this gracefully
- If issues persist, remove existing integration first
- Clear `.storage/core.config_entries` (with backup!)

## 🔧 **Advanced Installation**

### Docker/Container Setup
```yaml
# docker-compose.yml additions
services:
  homeassistant:
    devices:
      - /dev/bus/usb:/dev/bus/usb  # For USB Bluetooth
    privileged: true  # Or specific capabilities
    environment:
      - DBUS_SYSTEM_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket
```

### Home Assistant Core
```bash
# Install Bluetooth dependencies
sudo apt-get install bluetooth libbluetooth-dev

# Ensure user permissions
sudo usermod -a -G bluetooth homeassistant

# Install Python dependencies
pip3 install bleak asyncio-mqtt
```

## 📋 **Post-Installation Checklist**

- [ ] Integration appears in **Devices & Services**
- [ ] All expected entities are created
- [ ] `sensor.volcano_connection_status` shows "Connected"
- [ ] Temperature readings are updating
- [ ] Climate entity responds to temperature changes
- [ ] Fan entity can be controlled
- [ ] Session statistics are tracked
- [ ] Events are firing (check **Developer Tools** → **Events**)

## 🎯 **Next Steps**

After successful installation:

1. **Explore entities**: Check [Entities Overview](Entities-Overview)
2. **Build automations**: See [Automation Examples](Automation-Examples)
3. **Configure dashboard**: Add entities to your Lovelace UI
4. **Set up statistics**: Configure [Statistics](Statistics) tracking

---

**Need help?** Check [Troubleshooting](Troubleshooting) or open an [issue](https://github.com/grovesdigital/volcano-hybrid-ha/issues).
