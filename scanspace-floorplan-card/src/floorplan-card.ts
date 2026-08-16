import { LitElement, html, css, TemplateResult } from "lit";
import { HomeAssistant, FloorplanCardConfig, SvgElementData } from "./types";
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
  };

  hass?: HomeAssistant;
  config?: FloorplanCardConfig;

  private renderer?: SvgRenderer;
  private container?: HTMLDivElement;
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
    }
    .container {
      position: relative;
      width: 100%;
      overflow: hidden;
      touch-action: none;
      user-select: none;
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
    }
    .furniture:hover {
      filter: brightness(1.2);
    }
    .tooltip {
      position: absolute;
      background: rgba(0, 0, 0, 0.75);
      color: #fff;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      pointer-events: none;
      display: none;
      z-index: 10;
    }
  `;

  setConfig(config: FloorplanCardConfig) {
    this.config = config;
  }

  connectedCallback() {
    super.connectedCallback();
    this._loadFloorplan();
  }

  updated(changedProps: Map<string, unknown>) {
    if (changedProps.has("hass") && this.hass && this.renderer) {
      this._applyEntityStates();
    }
  }

  private async _loadFloorplan() {
    if (!this.hass || !this.config) return;
    const data = await fetchFloorplan(
      this.hass,
      this.config.house_id,
      this.config.floor_id
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
    const entities = this.config.show_entities ?? [];
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
      const action = this.config.entity_click_action ?? "more-info";
      if (action === "toggle") {
        toggleEntity(this.hass, item.entityId);
      } else {
        moreInfoEntity(this.hass, item.entityId);
      }
    } else if (item.type === "furniture" || item.type === "zone") {
      // TODO: open assign-entity dialog
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

  render(): TemplateResult {
    if (!this.config) {
      return html`<div>No config</div>`;
    }
    if (!this.renderer) {
      return html`
        <div class="container">
          <div style="padding: 16px; color: #999">
            Floorplan not available. Configure ScanSpace integration and ensure MQTT or webhook data is received.
          </div>
        </div>
      `;
    }

    return html`
      <div
        class="container"
        @pointerdown=${this._onPointerDown}
        @pointermove=${this._onPointerMove}
        @pointerup=${this._onPointerUp}
        @pointerleave=${this._onPointerUp}
        @dblclick=${this._onDoubleClick}
        style="height: 100%; min-height: 300px;"
      >
        ${this._renderSvg()}
        <div class="tooltip" id="tooltip"></div>
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
    // Re-attach only once per render
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
    tooltip.textContent = `${item.type}${item.furnitureType ? ` (${item.furnitureType})` : ""}${state ? ` - ${state.state}` : ""}`;
    tooltip.style.display = "block";
  }

  private _hideTooltip() {
    const tooltip = this.shadowRoot?.getElementById("tooltip");
    if (tooltip) tooltip.style.display = "none";
  }

  // --- Pan / Zoom / Touch ---

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
    this.scale = 1;
    this.panX = 0;
    this.panY = 0;
    this._updateTransform();
  }

  private _distance(a: PointerEvent, b: PointerEvent): number {
    const dx = a.clientX - b.clientX;
    const dy = a.clientY - b.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  private _clampZoom(zoom: number): number {
    const min = this.config?.min_zoom ?? 0.5;
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
    return 5;
  }
}

customElements.define("scanspace-floorplan-card", ScanSpaceFloorplanCard);

(window as any).customCards = (window as any).customCards || [];
(window as any).customCards.push({
  type: "custom:scanspace-floorplan",
  name: "ScanSpace Floorplan",
  description: "Interactive floorplan from ScanSpace AR measurements",
  preview: true,
});
