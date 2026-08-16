import { FloorplanData, FloorplanCardConfig, HomeAssistant, SvgElementData, HassEntity, StateStyle } from "./types";

const SVG_NS = "http://www.w3.org/2000/svg";

export class SvgRenderer {
  private svg: SVGSVGElement;
  private data: SvgElementData[] = [];

  constructor(svgString: string) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(svgString, "image/svg+xml");
    const imported = doc.documentElement;
    if (!(imported instanceof SVGSVGElement)) {
      throw new Error("Invalid SVG: root element is not SVG");
    }
    this.svg = imported;
    this.svg.setAttribute("width", "100%");
    this.svg.setAttribute("height", "100%");
    this.svg.style.display = "block";
    this.svg.style.touchAction = "none";
    this._wrapInViewport();
    this._indexElements();
  }

  private _wrapInViewport(): void {
    const viewport = document.createElementNS(SVG_NS, "g");
    viewport.setAttribute("class", "scanspace-viewport");
    // Move all direct children except defs/metadata into viewport
    const children = Array.from(this.svg.childNodes);
    for (const child of children) {
      if (child.nodeType === Node.ELEMENT_NODE && child !== viewport) {
        this.svg.removeChild(child);
        viewport.appendChild(child);
      }
    }
    this.svg.appendChild(viewport);
  }

  getElement(): SVGSVGElement {
    return this.svg;
  }

  getSvgData(): SvgElementData[] {
    return this.data;
  }

  applyEntityState(entityId: string, state: string, config: FloorplanCardConfig): void {
    const elements = this.data.filter((d) => d.entityId === entityId);
    const styleMap = config.entity_styles ?? config.entity_state_visualization;
    const rawStyle = styleMap?.[entityId]?.[state] ?? styleMap?.[entityId];
    if (!rawStyle || typeof rawStyle !== "object") return;
    const style = rawStyle as StateStyle;

    for (const item of elements) {
      const el = item.element;
      if (typeof style.fill === "string") {
        if (el instanceof SVGGraphicsElement) {
          el.setAttribute("fill", style.fill);
        }
      }
      if (typeof style.stroke === "string") {
        el.setAttribute("stroke", style.stroke);
      }
      if (style.width !== undefined) {
        el.setAttribute("stroke-width", String(style.width));
      }
      if (style.opacity !== undefined) {
        el.setAttribute("opacity", String(style.opacity));
      }
      if (style.pulse || (state === "on" && entityId.startsWith("binary_sensor."))) {
        el.classList.add("scanspace-pulse");
      } else {
        el.classList.remove("scanspace-pulse");
      }
      if (typeof style.icon === "string" && item.type === "furniture") {
        this._setIcon(el, style.icon);
      }
    }
  }

  findByFurnitureId(furnitureId: string): SvgElementData | undefined {
    return this.data.find((d) => d.furnitureId === furnitureId);
  }

  findByRoomId(roomId: string): SvgElementData[] {
    return this.data.filter((d) => d.roomId === roomId);
  }

  private _indexElements(): void {
    const all = this.svg.querySelectorAll("*");
    for (const el of Array.from(all)) {
      const type = el.getAttribute("data-scanspace-type");
      if (!type) continue;

      this.data.push({
        type,
        roomId: el.getAttribute("data-room-id") ?? undefined,
        furnitureId: el.getAttribute("data-furniture-id") ?? undefined,
        furnitureType: el.getAttribute("data-furniture-type") ?? undefined,
        entityId: el.getAttribute("data-entity-id") ?? undefined,
        zoneId: el.getAttribute("data-zone-id") ?? undefined,
        connectsTo: el.getAttribute("data-connects-to") ?? undefined,
        element: el as SVGElement,
      });
    }
  }

  private _setIcon(el: SVGElement, iconName: string): void {
    const existing = el.querySelector("text.scanspace-icon");
    if (existing) existing.remove();

    const text = document.createElementNS(SVG_NS, "text");
    text.setAttribute("class", "scanspace-icon");
    text.textContent = iconName;
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("dominant-baseline", "middle");
    text.setAttribute("font-family", "sans-serif");
    text.setAttribute("font-size", "16");
    text.setAttribute("fill", "#fff");

    try {
      const bbox = (el as SVGGraphicsElement).getBBox();
      text.setAttribute("x", String(bbox.x + bbox.width / 2));
      text.setAttribute("y", String(bbox.y + bbox.height / 2));
    } catch {
      text.setAttribute("x", "0");
      text.setAttribute("y", "0");
    }
    el.appendChild(text);
  }
}

export async function fetchFloorplan(
  hass: HomeAssistant,
  houseId?: string,
  floorId?: string,
  svgUrl?: string
): Promise<FloorplanData | null> {
  if (svgUrl) {
    try {
      const resp = await fetch(svgUrl, { headers: { "Accept": "image/svg+xml" } });
      if (resp.ok) {
        const svg = await resp.text();
        return { svg, house_id: houseId ?? "default", floor_id: floorId ?? "default" };
      }
    } catch {
      // Fallback
    }
  }

  const hId = houseId ?? "default";
  const fId = floorId ?? "default";

  try {
    const payload = await hass.callWS({
      type: "scanspace/floorplan",
      house_id: hId,
      floor_id: fId,
    });
    const data = payload as { svg?: string; house_id?: string; floor_id?: string };
    if (data && data.svg) {
      return {
        svg: data.svg,
        house_id: data.house_id ?? hId,
        floor_id: data.floor_id ?? fId,
      };
    }
  } catch {
    const url = `/local/scanspace/${hId}_${fId}.svg`;
    try {
      const resp = await fetch(url, { headers: { "Accept": "image/svg+xml" } });
      if (resp.ok) {
        const svg = await resp.text();
        return { svg, house_id: hId, floor_id: fId };
      }
    } catch {
      // ignore
    }
  }

  return null;
}

export function getEntityState(hass: HomeAssistant, entityId: string): HassEntity | undefined {
  return hass.states[entityId];
}

export function toggleEntity(hass: HomeAssistant, entityId: string): void {
  const domain = entityId.split(".")[0];
  hass.callService(domain, "toggle", { entity_id: entityId });
}

export function moreInfoEntity(hass: HomeAssistant, entityId: string): void {
  const event = new CustomEvent("hass-more-info", {
    bubbles: true,
    composed: true,
    detail: { entityId },
  });
  document.dispatchEvent(event);
}
