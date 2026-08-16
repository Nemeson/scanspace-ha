import { LitElement, TemplateResult } from "lit";
import { HomeAssistant, FloorplanCardConfig } from "./types";
export declare class ScanSpaceFloorplanCardEditor extends LitElement {
    static properties: {
        hass: {
            attribute: boolean;
        };
        _config: {
            state: boolean;
        };
    };
    hass?: HomeAssistant;
    private _config?;
    static styles: import("lit").CSSResult;
    setConfig(config: FloorplanCardConfig): void;
    private _valueChanged;
    render(): TemplateResult;
}
