export interface FloorplanCardConfig {
  type: "custom:scanspace-floorplan";
  house_id: string;
  floor_id?: string;
  show_entities?: string[];
  entity_click_action?: "toggle" | "more-info" | "navigate";
  entity_state_visualization?: Record<string, Record<string, StateStyle>>;
  show_zones?: boolean;
  show_furniture?: boolean;
  show_dimensions?: boolean;
  background_color?: string;
  wall_color?: string;
  furniture_default_color?: string;
  highlight_color?: string;
  min_zoom?: number;
  max_zoom?: number;
  default_zoom?: "fit" | number;
}

export interface StateStyle {
  fill?: string;
  stroke?: string;
  width?: number;
  icon?: string;
}

export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
}

export interface HomeAssistant {
  callService: (domain: string, service: string, serviceData?: Record<string, unknown>) => void;
  callWS: (msg: Record<string, unknown>) => Promise<unknown>;
  states: Record<string, HassEntity>;
}

export interface FloorplanData {
  svg: string;
  house_id: string;
  floor_id: string;
}

export interface SvgElementData {
  type: string;
  roomId?: string;
  furnitureId?: string;
  furnitureType?: string;
  entityId?: string;
  zoneId?: string;
  connectsTo?: string;
  element: SVGElement;
}
