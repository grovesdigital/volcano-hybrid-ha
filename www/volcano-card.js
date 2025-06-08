/**
 * Volcano Hybrid Custom Lovelace Card
 * 
 * A beautiful, interactive Home Assistant card for the Storz & Bickel Volcano Hybrid
 * Features:
 * - Interactive SVG volcano background
 * - Real-time temperature displays  
 * - Heat and fan control buttons
 * - Temperature preset buttons
 * - Responsive design for all screen sizes
 * 
 * @version 1.1.0
 * @author Volcano Hybrid HA Integration
 */

console.log('🔥 VOLCANO CARD FILE STARTED LOADING');
console.log('Current URL:', window.location.href);
console.log('Document ready state:', document.readyState);

class VolcanoCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    if (!config) {
      throw new Error('Invalid configuration');
    }
    
    this.config = {
      entity: config.entity || 'climate.volcano_hybrid',
      fan_entity: config.fan_entity || 'fan.volcano_hybrid_fan',
      name: config.name || 'Volcano Hybrid',
      show_name: config.show_name !== false,
      show_status: config.show_status !== false,
      ...config
    };

    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.updateCard();
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          font-family: var(--primary-font-family);
        }

        .volcano-container {
          position: relative;
          width: 25rem;
          height: 25rem;
          border-radius: 1.25rem;
          background: var(--card-background-color, white);
          box-shadow: var(--ha-card-box-shadow, 0 0.25rem 1.25rem rgba(0,0,0,0.1));
          margin: 1.25rem auto;
          overflow: hidden;
          border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, transparent);
        }

        .volcano-svg {
          width: 100%;
          height: 100%;
        }

        .temperature-display {
          position: absolute;
          font-family: 'Orbitron', 'Courier New', monospace;
          font-weight: 900;
          cursor: pointer;
          user-select: none;
          text-shadow: 
            0 0 0.3125rem currentColor,
            0 0 0.625rem currentColor,
            0 0 0.9375rem currentColor;
          letter-spacing: 0.125rem;
          background: linear-gradient(90deg, currentColor 0%, transparent 50%, currentColor 100%);
          -webkit-background-clip: text;
          background-clip: text;
          animation: digitalFlicker 3s infinite;
          transition: transform 0.2s ease;
        }

        .temperature-display:hover {
          transform: scale(1.05);
        }

        @keyframes digitalFlicker {
          0%, 98% { opacity: 1; }
          99%, 100% { opacity: 0.95; }
        }

        .current-temp {
          top: 30%;
          left: 42%;
          font-size: 2.5rem;
          color: rgb(255, 107, 53);
          filter: drop-shadow(0 0 0.5rem rgb(255, 107, 53));
        }

        .target-temp {
          top: 40%;
          right: 39%;
          font-size: 2.5rem;
          color: rgb(255, 255, 255);
          filter: drop-shadow(0 0 0.5rem rgb(255, 255, 255));
        }

        .control-button {
          position: absolute;
          background: rgba(255,255,255,0.95);
          border: none;
          border-radius: 0.5rem;
          padding: 0.5rem 0.75rem;
          cursor: pointer;
          box-shadow: 0 0.125rem 0.625rem rgba(0,0,0,0.2);
          font-weight: bold;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .control-button:hover {
          transform: scale(1.1);
          box-shadow: 0 0.25rem 0.9375rem rgba(0,0,0,0.3);
        }

        .control-button:active {
          transform: scale(0.95);
        }

        .control-button.active {
          background: #ff6b35;
          color: white;
        }

        .temp-down {
          bottom: 10%;
          left: 20%;
          width: 10%;
          height: 10%;
          color: rgb(74, 144, 226);
          border-radius: 50%;
          font-size: 1.25rem;
        }

        .temp-up {
          bottom: 10%;
          left: 33%;
          width: 10%;
          height: 10%;
          color: rgb(255, 107, 53);
          border-radius: 50%;
          font-size: 1.25rem;
        }

        .heat-toggle {
          bottom: 10%;
          right: 33%;
          width: 3.75rem;
          height: 2.5rem;
          color: rgb(255, 68, 68);
          font-size: 0.875rem;
        }

        .heat-toggle.active {
          background: rgb(255, 68, 68);
          color: white;
        }

        .fan-toggle {
          bottom: 10%;
          right: 20%;
          width: 3.125rem;
          height: 2.5rem;
          color: rgb(68, 170, 68);
          font-size: 0.875rem;
        }

        .fan-toggle.active {
          background: rgb(68, 170, 68);
          color: white;
        }

        .status-indicator {
          position: absolute;
          top: 5%;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          gap: 0.625rem;
        }

        .status-dot {
          width: 0.75rem;
          height: 0.75rem;
          border-radius: 50%;
          background: #ccc;
          opacity: 0.3;
          transition: all 0.3s ease;
        }

        .status-dot.heat-on {
          background: #ff4444;
          opacity: 1;
          animation: pulse 2s infinite;
        }

        .status-dot.fan-on {
          background: #44aa44;
          opacity: 1;
          animation: spin 1s linear infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .card-header {
          text-align: center;
          padding: 1rem;
          font-size: 1.2rem;
          font-weight: bold;
          color: var(--primary-text-color);
        }

        .unavailable {
          opacity: 0.5;
          pointer-events: none;
        }

        .error-message {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          color: var(--error-color);
          font-weight: bold;
          text-align: center;
        }
      </style>

      <ha-card>
        ${this.config.show_name ? `<div class="card-header">${this.config.name}</div>` : ''}
        
        <div class="volcano-container" id="volcanoContainer">
          <div class="volcano-svg">
            <object data="/local/trace.svg" type="image/svg+xml" style="width: 100%; height: 100%; pointer-events: none;"></object>
          </div>

          <div class="temperature-display current-temp" id="currentTemp">--</div>
          <div class="temperature-display target-temp" id="targetTemp">--</div>

          <button class="control-button temp-down" id="tempDown" title="Decrease Temperature">−</button>
          <button class="control-button temp-up" id="tempUp" title="Increase Temperature">+</button>
          <button class="control-button heat-toggle" id="heatToggle" title="Toggle Heat">HEAT</button>
          <button class="control-button fan-toggle" id="fanToggle" title="Toggle Fan">FAN</button>

          ${this.config.show_status ? `
          <div class="status-indicator">
            <div class="status-dot" id="heatStatus" title="Heat Status"></div>
            <div class="status-dot" id="fanStatus" title="Fan Status"></div>
          </div>
          ` : ''}

          <div class="error-message" id="errorMessage" style="display: none;">
            Device Unavailable
          </div>
        </div>
      </ha-card>
    `;

    this.setupEventListeners();
  }

  setupEventListeners() {
    const tempDown = this.shadowRoot.getElementById('tempDown');
    const tempUp = this.shadowRoot.getElementById('tempUp');
    const heatToggle = this.shadowRoot.getElementById('heatToggle');
    const fanToggle = this.shadowRoot.getElementById('fanToggle');

    tempDown?.addEventListener('click', () => this.adjustTemperature(-1));
    tempUp?.addEventListener('click', () => this.adjustTemperature(1));
    heatToggle?.addEventListener('click', () => this.toggleHeat());
    fanToggle?.addEventListener('click', () => this.toggleFan());
  }

  updateCard() {
    if (!this._hass) return;

    const climateEntity = this._hass.states[this.config.entity];
    const fanEntity = this._hass.states[this.config.fan_entity];
    
    const container = this.shadowRoot.getElementById('volcanoContainer');
    const errorMessage = this.shadowRoot.getElementById('errorMessage');

    if (!climateEntity || !fanEntity) {
      container?.classList.add('unavailable');
      if (errorMessage) errorMessage.style.display = 'block';
      return;
    }

    container?.classList.remove('unavailable');
    if (errorMessage) errorMessage.style.display = 'none';

    // Update temperature displays
    const currentTemp = this.shadowRoot.getElementById('currentTemp');
    const targetTemp = this.shadowRoot.getElementById('targetTemp');
    
    if (currentTemp) {
      const current = climateEntity.attributes.current_temperature;
      currentTemp.textContent = current != null ? `${Math.round(current)}` : '--';
    }
    
    if (targetTemp) {
      const target = climateEntity.attributes.temperature;
      targetTemp.textContent = target != null ? `${Math.round(target)}` : '--';
    }

    // Update heat toggle
    const heatToggle = this.shadowRoot.getElementById('heatToggle');
    const heatStatus = this.shadowRoot.getElementById('heatStatus');
    
    const isHeating = climateEntity.state === 'heat';
    heatToggle?.classList.toggle('active', isHeating);
    heatStatus?.classList.toggle('heat-on', isHeating);

    // Update fan toggle
    const fanToggle = this.shadowRoot.getElementById('fanToggle');
    const fanStatus = this.shadowRoot.getElementById('fanStatus');
    
    const isFanOn = fanEntity.state === 'on';
    fanToggle?.classList.toggle('active', isFanOn);
    fanStatus?.classList.toggle('fan-on', isFanOn);
  }

  async adjustTemperature(delta) {
    const climateEntity = this._hass.states[this.config.entity];
    if (!climateEntity) return;

    const currentTarget = climateEntity.attributes.temperature || 190;
    const newTarget = Math.max(40, Math.min(230, currentTarget + delta));

    await this._hass.callService('climate', 'set_temperature', {
      entity_id: this.config.entity,
      temperature: newTarget
    });
  }

  async toggleHeat() {
    const climateEntity = this._hass.states[this.config.entity];
    if (!climateEntity) return;

    // Check current state - could be 'heat', 'off', 'auto', etc.
    const currentState = climateEntity.state;
    const isCurrentlyHeating = currentState === 'heat';
    
    // Toggle between 'heat' and 'off'
    const newMode = isCurrentlyHeating ? 'off' : 'heat';

    console.log(`🔥 Toggling heat: ${currentState} → ${newMode}`);

    try {
      await this._hass.callService('climate', 'set_hvac_mode', {
        entity_id: this.config.entity,
        hvac_mode: newMode
      });
    } catch (error) {
      console.error('Error toggling heat:', error);
    }
  }

  async toggleFan() {
    const fanEntity = this._hass.states[this.config.fan_entity];
    if (!fanEntity) return;

    // Check current fan state
    const currentState = fanEntity.state;
    const isFanOn = currentState === 'on';
    
    // Choose the right service
    const service = isFanOn ? 'turn_off' : 'turn_on';

    console.log(`💨 Toggling fan: ${currentState} → ${isFanOn ? 'off' : 'on'}`);

    try {
      await this._hass.callService('fan', service, {
        entity_id: this.config.fan_entity
      });
    } catch (error) {
      console.error('Error toggling fan:', error);
    }
  }

  getCardSize() {
    return 5;
  }

  static getConfigElement() {
    return document.createElement('volcano-card-editor');
  }

  static getStubConfig() {
    return {
      type: 'custom:volcano-card',
      entity: 'climate.volcano_hybrid',
      fan_entity: 'fan.volcano_hybrid_fan',
      name: 'Volcano Hybrid',
      show_name: true,
      show_status: true
    };
  }
}

// Register the card
if (!customElements.get('volcano-card')) {
  customElements.define('volcano-card', VolcanoCard);
  console.log('✅ Volcano Card registered successfully');
} else {
  console.log('ℹ️ Volcano Card already registered');
}

// Add to custom card registry
window.customCards = window.customCards || [];
if (!window.customCards.find(card => card.type === 'volcano-card')) {
  window.customCards.push({
    type: 'volcano-card',
    name: 'Volcano Hybrid Card',
    description: 'Interactive volcano-themed climate control card',
    preview: false,
    documentationURL: 'https://github.com/yourusername/volcano-hybrid-ha'
  });
  console.log('✅ Volcano Card added to card picker');
}

console.log('🌋 Volcano Card module loaded completely');