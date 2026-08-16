import { FloorplanData, FloorplanCardConfig, HomeAssistant, SvgElementData, HassEntity } from "./types";
export declare class SvgRenderer {
    private svg;
    private data;
    constructor(svgString: string);
    private _wrapInViewport;
    getElement(): SVGSVGElement;
    getSvgData(): SvgElementData[];
    applyEntityState(entityId: string, state: string, config: FloorplanCardConfig): void;
    findByFurnitureId(furnitureId: string): SvgElementData | undefined;
    findByRoomId(roomId: string): SvgElementData[];
    private _indexElements;
    private _setIcon;
}
export declare function fetchFloorplan(hass: HomeAssistant, houseId: string, floorId?: string): Promise<FloorplanData | null>;
export declare function getEntityState(hass: HomeAssistant, entityId: string): HassEntity | undefined;
export declare function toggleEntity(hass: HomeAssistant, entityId: string): void;
export declare function moreInfoEntity(hass: HomeAssistant, entityId: string): void;
