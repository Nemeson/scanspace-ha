import { FloorplanData, FloorplanCardConfig, HomeAssistant, SvgElementData, HassEntity } from "./types";

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
    const style = config.entity_state_visualization?.[entityId]?.[state];
    if (!style) return;

    for (const item of elements) {
      const el = item.element;
      if (style.fill) {
        if (el instanceof SVGGraphicsElement) {
          el.setAttribute("fill", style.fill);
        }
      }
      if (style.stroke) {
        el.setAttribute("stroke", style.stroke);
      }
      if (style.width) {
        el.setAttribute("stroke-width", String(style.width));
      }
      if (style.icon && item.type === "furniture") {
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
    // Remove existing icon text if any
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

    // Try to center in bbox; if not available, center of group transform
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
  houseId: string,
  floorId?: string
): Promise<FloorplanData | null> {
  try {
    // Try WebSocket API first; fallback to REST if unavailable
    const payload = await hass.callWS({
      type: "scanspace/floorplan",
      house_id: houseId,
      floor_id: floorId ?? "default",
    });
    const data = payload as { svg?: string; house_id?: string; floor_id?: string };
    if (!data.svg) return null;
    return {
      svg: data.svg,
      house_id: data.house_id ?? houseId,
      floor_id: data.floor_id ?? floorId ?? "default",
    };
  } catch {
    // Fallback: load static SVG from integration www folder
    const floor = floorId ?? "default";
    const url = `/local/scanspace/${houseId}_${floor}.svg`;
    const resp = await fetch(url, { headers: { "Accept": "image/svg+xml" } });
    if (!resp.ok) return null;
    const svg = await resp.text();
    return { svg, house_id: houseId, floor_id: floor };
  }
}

export function getEntityState(hass: HomeAssistant, entityId: string): HassEntity | undefined {
  return hass.states[entityId];
}

export function toggleEntity(hass: HomeAssistant, entityId: string): void {
  const domain = entityId.split(".")[0];
  hass.callService(domain, "toggle", { entity_id: entityId });
}

export function moreInfoEntity(hass: HomeAssistant, entityId: string): void {
  // Dispatch standard HA more-info event
  const event = new CustomEvent("hass-more-info", {
    bubbles: true,
    composed: true,
    detail: { entityId },
  });
  document.dispatchEvent(event);
}
