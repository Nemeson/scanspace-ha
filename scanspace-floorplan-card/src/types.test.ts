import { describe, it, expect } from "vitest";
import { getEntityState, toggleEntity } from "./svg-renderer";
import { HomeAssistant } from "./types";

describe("Floorplan Card Helper Functions", () => {
  it("getEntityState returns entity from hass states", () => {
    const mockHass: HomeAssistant = {
      states: {
        "light.living_room": {
          entity_id: "light.living_room",
          state: "on",
          attributes: { brightness: 255 },
        },
      },
      callService: () => {},
      callWS: async () => ({}),
    };

    const state = getEntityState(mockHass, "light.living_room");
    expect(state).toBeDefined();
    expect(state?.state).toBe("on");
    expect(state?.attributes.brightness).toBe(255);
  });

  it("toggleEntity calls callService with correct domain and entity_id", () => {
    let serviceCalledWith: { domain: string; service: string; data?: Record<string, unknown> } | null = null;
    const mockHass: HomeAssistant = {
      states: {},
      callService: (domain, service, data) => {
        serviceCalledWith = { domain, service, data };
      },
      callWS: async () => ({}),
    };

    toggleEntity(mockHass, "light.living_room");
    expect(serviceCalledWith).toEqual({
      domain: "light",
      service: "toggle",
      data: { entity_id: "light.living_room" },
    });
  });
});
