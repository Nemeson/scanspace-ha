import { LitElement, html, css, TemplateResult } from "lit";
import { HomeAssistant, FloorplanCardConfig, SvgElementData, FloorConfig } from "./types";
import {
  SvgRenderer,
  fetchFloorplan,
  getEntityState,
  toggleEntity,
  moreInfoEntity,
} from "./svg-renderer";

class ScanSpaceFloorplanCard extends LitElement {
  static properties = {
    hass: { attribute: false },
    config: { attribute: false },
    activeFloorId: { state: true },
  };

  hass?: HomeAssistant;
  config?: FloorplanCardConfig;
  activeFloorId?: string;

  private renderer?: SvgRenderer;
  private scale = 1;
  private panX = 0;
  private panY = 0;
  private isDragging = false;
  private lastPointerX = 0;
  private lastPointerY = 0;
  private pointers = new Map<number, PointerEvent>();
  private initialPinchDistance = 0;
  private initialScale = 1;

  static styles = css`
    :host {
      display: block;
      width: 100%;
      background: var(--ha-card-background, var(--card-background-color, #1e1e1e));
      border-radius: var(--ha-card-border-radius, 12px);
      box-shadow: var(--ha-card-box-shadow, 0 2px 10px rgba(0, 0, 0, 0.2));
      overflow: hidden;
      font-family: var(--paper-font-body1_-_font-family, system-ui, -apple-system, sans-serif);
      color: var(--primary-text-color, #ffffff);
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      font-size: 16px;
      font-weight: 600;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .floor-selector {
      display: flex;
      gap: 8px;
      padding: 8px 12px;
      background: rgba(0, 0, 0, 0.2);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      overflow-x: auto;
    }
    .floor-pill {
      padding: 6px 14px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.08);
      color: rgba(255, 255, 255, 0.7);
      font-size: 12px;
      font-weight: 600;
      border: 1px solid transparent;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .floor-pill:hover {
      background: rgba(255, 255, 255, 0.15);
      color: #fff;
    }
    .floor-pill.active {
      background: var(--primary-color, #0288d1);
      color: #fff;
      border-color: rgba(255, 255, 255, 0.3);
      box-shadow: 0 2px 8px rgba(2, 136, 209, 0.4);
    }
    .viewport-container {
      position: relative;
      width: 100%;
      min-height: 320px;
      overflow: hidden;
      touch-action: none;
      user-select: none;
      background: var(--scanspace-card-bg, #141414);
    }
    svg {
      display: block;
      width: 100%;
      height: 100%;
      cursor: grab;
    }
    svg:active {
      cursor: grabbing;
    }
    .furniture {
      cursor: pointer;
      transition: fill 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                  stroke 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                  opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                  filter 0.2s ease;
    }
    .furniture:hover {
      filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.6)) brightness(1.15);
    }
    .scanspace-pulse {
      animation: scanspace-presence-pulse 2s infinite ease-in-out;
    }
    @keyframes scanspace-presence-pulse {
      0% {
        opacity: 0.35;
        filter: drop-shadow(0 0 2px #00e676);
      }
      50% {
        opacity: 1;
        filter: drop-shadow(0 0 10px #00e676);
      }
      100% {
        opacity: 0.35;
        filter: drop-shadow(0 0 2px #00e676);
      }
    }
    .toolbar {
      position: absolute;
      bottom: 12px;
      right: 12px;
      display: flex;
      gap: 6px;
      background: rgba(20, 20, 20, 0.8);
      backdrop-filter: blur(8px);
      padding: 4px;
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, 0.12);
      z-index: 10;
    }
    .toolbar-btn {
      background: transparent;
      border: none;
      color: rgba(255, 255, 255, 0.85);
      width: 32px;
      height: 32px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 15px;
      font-weight: bold;
      transition: background 0.2s, color 0.2s;
    }
    .toolbar-btn:hover {
      background: rgba(255, 255, 255, 0.18);
      color: #fff;
    }
    .tooltip {
      position: absolute;
      background: rgba(15, 15, 15, 0.9);
      backdrop-filter: blur(4px);
      color: #fff;
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      pointer-events: none;
      display: none;
      z-index: 20;
      border: 1px solid rgba(255, 255, 255, 0.15);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }
  `;

  setConfig(config: FloorplanCardConfig) {
    this.config = config;
    if (!this.activeFloorId) {
      this.activeFloorId = config.floor_id ?? config.floors?.[0]?.id ?? "floor_eg";
    }
  }

  connectedCallback() {
    super.connectedCallback();
    this._loadFloorplan();
  }

  updated(changedProps: Map<string, unknown>) {
    if (changedProps.has("hass") && this.hass && this.renderer) {
      this._applyEntityStates();
    }
    if (changedProps.has("activeFloorId")) {
      this._loadFloorplan();
    }
  }

  private async _loadFloorplan() {
    if (!this.hass || !this.config) return;
    
    // Find matching floor config if available
    const activeFloor = this.config.floors?.find((f) => f.id === this.activeFloorId);
    const svgUrl = activeFloor?.svg_url ?? this.config.svg_url;

    const data = await fetchFloorplan(
      this.hass,
      this.config.house_id,
      this.activeFloorId,
      svgUrl
    );
    if (!data) {
      this.renderer = undefined;
      this.requestUpdate();
      return;
    }
    this.renderer = new SvgRenderer(data.svg);
    this._applyEntityStates();
    this.requestUpdate();
  }

  private _applyEntityStates() {
    if (!this.renderer || !this.hass || !this.config) return;
    const entities = this.config.show_entities ?? Object.keys(this.config.entity_styles ?? {});
    for (const entityId of entities) {
      const state = getEntityState(this.hass, entityId);
      if (state) {
        this.renderer.applyEntityState(entityId, state.state, this.config);
      }
    }
  }

  private _onElementClick(item: SvgElementData) {
    if (!this.hass || !this.config) return;
    if (item.entityId) {
      const tapConfig = this.config.tap_actions?.[item.furnitureId ?? ""] ?? this.config.tap_actions?.[item.entityId];
      if (tapConfig?.action === "call-service" && tapConfig.service) {
        const [domain, service] = tapConfig.service.split(".");
        this.hass.callService(domain, service, tapConfig.target ?? { entity_id: item.entityId });
        return;
      }

      const action = this.config.entity_click_action ?? "toggle";
      if (action === "toggle") {
        toggleEntity(this.hass, item.entityId);
      } else {
        moreInfoEntity(this.hass, item.entityId);
      }
    } else if (item.type === "furniture" || item.type === "zone") {
      this._showAssignEntityDialog(item);
    }
  }

  private _showAssignEntityDialog(item: SvgElementData) {
    const event = new CustomEvent("scanspace-assign-entity", {
      bubbles: true,
      composed: true,
      detail: { furnitureId: item.furnitureId, roomId: item.roomId },
    });
    this.dispatchEvent(event);
  }

  private _selectFloor(floorId: string) {
    if (this.activeFloorId === floorId) return;
    this.activeFloorId = floorId;
    this.scale = 1;
    this.panX = 0;
    this.panY = 0;
  }

  private _zoomIn() {
    this.scale = this._clampZoom(this.scale * 1.25);
    this._updateTransform();
  }

  private _zoomOut() {
    this.scale = this._clampZoom(this.scale * 0.8);
    this._updateTransform();
  }

  private _resetZoom() {
    this.scale = 1;
    this.panX = 0;
    this.panY = 0;
    this._updateTransform();
  }

  render(): TemplateResult {
    if (!this.config) {
      return html`<div>No config</div>`;
    }

    const title = this.config.title;
    const floors = this.config.floors ?? [];

    return html`
      ${title ? html`<div class="header">${title}</div>` : ""}
      ${floors.length > 1 ? this._renderFloorSelector(floors) : ""}
      <div
        class="viewport-container"
        @pointerdown=${this._onPointerDown}
        @pointermove=${this._onPointerMove}
        @pointerup=${this._onPointerUp}
        @pointerleave=${this._onPointerUp}
        @dblclick=${this._onDoubleClick}
      >
        ${this.renderer
          ? this._renderSvg()
          : html`
              <div style="padding: 24px; text-align: center; color: rgba(255,255,255,0.6);">
                Kein Grundriss verfügbar. Bitte ScanSpace Integration und SVG-Konfiguration prüfen.
              </div>
            `}
        <div class="tooltip" id="tooltip"></div>
        ${this.config.show_toolbar !== false
          ? html`
              <div class="toolbar">
                <button class="toolbar-btn" @click=${this._zoomIn} title="Zoom In">+</button>
                <button class="toolbar-btn" @click=${this._zoomOut} title="Zoom Out">-</button>
                <button class="toolbar-btn" @click=${this._resetZoom} title="Reset View">🎯</button>
              </div>
            `
          : ""}
      </div>
    `;
  }

  private _renderFloorSelector(floors: FloorConfig[]) {
    return html`
      <div class="floor-selector">
        ${floors.map(
          (floor) => html`
            <button
              class="floor-pill ${this.activeFloorId === floor.id ? "active" : ""}"
              @click=${() => this._selectFloor(floor.id)}
            >
              ${floor.name}
            </button>
          `
        )}
      </div>
    `;
  }

  private _renderSvg() {
    if (!this.renderer) return;
    const svg = this.renderer.getElement();
    this._attachEventListeners(svg);
    return html`${svg}`;
  }

  private _attachEventListeners(svg: SVGSVGElement) {
    if ((svg as any).__scanspaceAttached) return;
    (svg as any).__scanspaceAttached = true;

    for (const item of this.renderer!.getSvgData()) {
      const el = item.element;
      el.addEventListener("click", (e) => {
        e.stopPropagation();
        this._onElementClick(item);
      });
      el.addEventListener("mouseenter", () => this._showTooltip(item));
      el.addEventListener("mouseleave", () => this._hideTooltip());
    }
  }

  private _showTooltip(item: SvgElementData) {
    const tooltip = this.shadowRoot?.getElementById("tooltip");
    if (!tooltip || !this.hass) return;
    const state = item.entityId ? getEntityState(this.hass, item.entityId) : undefined;
    tooltip.textContent = `${item.type}${item.furnitureType ? ` (${item.furnitureType})` : ""}${
      state ? ` · ${state.state}` : ""
    }`;
    tooltip.style.display = "block";
  }

  private _hideTooltip() {
    const tooltip = this.shadowRoot?.getElementById("tooltip");
    if (tooltip) tooltip.style.display = "none";
  }

  // --- Pan / Zoom / Touch Gestures ---

  private _onPointerDown(e: PointerEvent) {
    this.pointers.set(e.pointerId, e);
    this.isDragging = this.pointers.size === 1;
    this.lastPointerX = e.clientX;
    this.lastPointerY = e.clientY;
    (e.target as Element).setPointerCapture?.(e.pointerId);
  }

  private _onPointerMove(e: PointerEvent) {
    if (!this.pointers.has(e.pointerId)) return;
    this.pointers.set(e.pointerId, e);

    if (this.pointers.size === 1 && this.isDragging) {
      const dx = e.clientX - this.lastPointerX;
      const dy = e.clientY - this.lastPointerY;
      this.panX += dx;
      this.panY += dy;
      this.lastPointerX = e.clientX;
      this.lastPointerY = e.clientY;
      this._updateTransform();
    } else if (this.pointers.size === 2) {
      const pts = Array.from(this.pointers.values());
      const dist = this._distance(pts[0], pts[1]);
      if (this.initialPinchDistance > 0) {
        const newScale = this.initialScale * (dist / this.initialPinchDistance);
        this.scale = this._clampZoom(newScale);
        this._updateTransform();
      }
    }
  }

  private _onPointerUp(e: PointerEvent) {
    this.pointers.delete(e.pointerId);
    if (this.pointers.size === 0) {
      this.isDragging = false;
    } else if (this.pointers.size === 1) {
      const remaining = Array.from(this.pointers.values())[0];
      this.lastPointerX = remaining.clientX;
      this.lastPointerY = remaining.clientY;
      this.isDragging = true;
    }
    if (this.pointers.size < 2) {
      this.initialPinchDistance = 0;
      this.initialScale = this.scale;
    }
  }

  private _onDoubleClick() {
    this._resetZoom();
  }

  private _distance(a: PointerEvent, b: PointerEvent): number {
    const dx = a.clientX - b.clientX;
    const dy = a.clientY - b.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  private _clampZoom(zoom: number): number {
    const min = this.config?.min_zoom ?? 0.4;
    const max = this.config?.max_zoom ?? 5.0;
    return Math.max(min, Math.min(max, zoom));
  }

  private _updateTransform() {
    if (!this.renderer) return;
    const svg = this.renderer.getElement();
    const g = svg.querySelector("g.scanspace-viewport") as SVGGElement | null;
    if (!g) return;
    g.setAttribute("transform", `translate(${this.panX},${this.panY}) scale(${this.scale})`);
  }

  getCardSize(): number {
    return 6;
  }
}

customElements.define("scanspace-floorplan-card", ScanSpaceFloorplanCard);

(window as any).customCards = (window as any).customCards || [];
(window as any).customCards.push({
  type: "custom:scanspace-floorplan",
  name: "ScanSpace Floorplan",
  description: "Interactive multi-floor floorplan card from ScanSpace AR measurements",
  preview: true,
});
