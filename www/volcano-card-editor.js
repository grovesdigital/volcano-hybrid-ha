/**
 * Volcano Hybrid Card Configuration Editor
 * 
 * Provides a user-friendly configuration interface for the Volcano Hybrid card
 * in the Home Assistant dashboard editor.
 * 
 * @version 1.1.0
 * @author Volcano Hybrid HA Integration
 */

class VolcanoCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this.render();
  }

  get _entity() {
    return this._config?.entity || '';
  }

  get _fan_entity() {
    return this._config?.fan_entity || '';
  }

  get _name() {
    return this._config?.name || '';
  }

  get _show_name() {
    return this._config?.show_name !== false;
  }

  get _show_status() {
    return this._config?.show_status !== false;
  }

  render() {
    this.innerHTML = `
      <div class="card-config">
        <div class="option">
          <label for="entity">Climate Entity:</label>
          <input type="text" id="entity" value="${this._entity}" placeholder="climate.volcano_hybrid">
        </div>
        
        <div class="option">
          <label for="fan_entity">Fan Entity:</label>
          <input type="text" id="fan_entity" value="${this._fan_entity}" placeholder="fan.volcano_hybrid_fan">
        </div>
        
        <div class="option">
          <label for="name">Name:</label>
          <input type="text" id="name" value="${this._name}" placeholder="Volcano Hybrid">
        </div>
        
        <div class="option">
          <label for="show_name">Show Name:</label>
          <input type="checkbox" id="show_name" ${this._show_name ? 'checked' : ''}>
        </div>
        
        <div class="option">
          <label for="show_status">Show Status Dots:</label>
          <input type="checkbox" id="show_status" ${this._show_status ? 'checked' : ''}>
        </div>
      </div>
      
      <style>
        .card-config {
          padding: 1rem;
        }
        
        .option {
          margin-bottom: 1rem;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        
        label {
          font-weight: bold;
        }
        
        input[type="text"] {
          width: 200px;
          padding: 0.5rem;
          border: 1px solid #ccc;
          border-radius: 0.25rem;
        }
        
        input[type="checkbox"] {
          transform: scale(1.2);
        }
      </style>
    `;

    this.setupEventListeners();
  }

  setupEventListeners() {
    const inputs = this.querySelectorAll('input');
    inputs.forEach(input => {
      input.addEventListener('input', this.configChanged.bind(this));
    });
  }

  configChanged() {
    const config = {
      entity: this.querySelector('#entity').value,
      fan_entity: this.querySelector('#fan_entity').value,
      name: this.querySelector('#name').value,
      show_name: this.querySelector('#show_name').checked,
      show_status: this.querySelector('#show_status').checked
    };

    this.dispatchEvent(new CustomEvent('config-changed', {
      detail: { config },
      bubbles: true,
      composed: true
    }));
  }
}

customElements.define('volcano-card-editor', VolcanoCardEditor);

// Enhanced registration for the main card
if (!customElements.get('volcano-card')) {
  customElements.define('volcano-card', VolcanoCard);
  console.log('✅ Volcano Card registered successfully');
} else {
  console.log('ℹ️ Volcano Card already registered');
}

// Better customCards registration
window.customCards = window.customCards || [];
if (!window.customCards.find(card => card.type === 'volcano-card')) {
  window.customCards.push({
    type: 'volcano-card',
    name: 'Volcano Hybrid Card',
    description: 'Interactive volcano-themed climate control card',
    preview: false, // Changed to false to avoid preview issues
    documentationURL: 'https://github.com/yourusername/volcano-hybrid-ha'
  });
  console.log('✅ Volcano Card added to card picker');
}

console.log('🌋 Volcano Card module loaded completely');