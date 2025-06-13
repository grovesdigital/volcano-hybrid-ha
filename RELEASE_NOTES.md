# Volcano Hybrid HA Integration v1.1.0 Release Notes

**Release Date:** August 6, 2025

## 🎉 Major New Feature: Custom Lovelace Card

This release introduces a beautiful, interactive Home Assistant card specifically designed for the Volcano Hybrid integration.

### ✨ Card Features

- **Interactive SVG Background**: Beautiful volcano illustration with real-time visual feedback
- **Temperature Displays**: Live current and target temperature readings
- **Control Buttons**: Heat and fan toggle buttons with visual status indicators
- **Preset Controls**: Quick temperature buttons (185°C, 190°C, 195°C, 200°C, Next Session)
- **Responsive Design**: Works perfectly on all screen sizes from mobile to desktop
- **Configuration UI**: Easy setup through Home Assistant's dashboard editor

### 📦 Installation

1. **Copy Files**: Place the `www/` folder in your Home Assistant config directory
2. **Register Resource**: Add `/local/volcano-card.js` as a JavaScript module resource
3. **Add to Dashboard**: Use `type: custom:volcano-card` in your dashboard YAML

### 🛠 Files Included

- `www/volcano-card.js` - Main card implementation (435 lines)
- `www/volcano-card-editor.js` - Configuration UI (144 lines) 
- `www/trace.svg` - Beautiful SVG volcano background
- `test-positioning.html` - Development testing tool

### 📚 Documentation Enhancements

- Complete installation guide with troubleshooting
- Card configuration examples and options
- Development guidelines for frontend contributions
- Comprehensive troubleshooting section

### 🔧 Technical Details

- Built with modern JavaScript (ES6+) 
- Uses LitElement patterns for reactive updates
- Percentage-based positioning for responsiveness
- Mobile-first CSS design approach
- Proper Home Assistant integration patterns

### 🐛 Troubleshooting Covered

- "Custom element doesn't exist" error resolution
- Resource registration verification steps
- Browser cache clearing instructions
- Entity availability checking
- Layout and responsive design tips

## 📊 Version Information

- **Integration Version**: 1.1.0
- **Minimum Home Assistant**: 2024.1.0+
- **Minimum Python**: 3.11+
- **Bluetooth**: BLE support required

## 🚀 Getting Started

1. **Install the Integration** (if not already done)
2. **Copy the www/ folder** to your HA config directory
3. **Register the card resource** in Settings → Dashboards → Resources
4. **Add the card** to your dashboard with your volcano entities
5. **Enjoy the beautiful interface!**

## 🔄 Upgrade Notes

- This is a feature release - no breaking changes
- Existing installations will continue to work unchanged
- The custom card is optional but highly recommended
- All previous functionality remains intact

---

For detailed installation instructions, troubleshooting, and configuration options, see the updated [README.md](README.md).
