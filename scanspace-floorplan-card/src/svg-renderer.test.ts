import { describe, it, expect } from "vitest";
import { SvgRenderer } from "./svg-renderer";
import { FloorplanCardConfig } from "./types";

const SAMPLE_SVG = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 400" width="500" height="400">
  <g id="walls" data-scanspace-type="wall" data-room-id="room_living">
    <line x1="0" y1="0" x2="500" y2="0" stroke="#fff" stroke-width="5"/>
  </g>
  <g id="furniture_couch" data-scanspace-type="furniture" data-room-id="room_living" data-furniture-id="furn_sofa" data-furniture-type="sofa" data-entity-id="light.living_room_corner">
    <rect x="50" y="50" width="100" height="50" fill="#444"/>
  </g>
</svg>
`;

describe("SvgRenderer", () => {
  it("parses valid SVG and wraps children in viewport", () => {
    const renderer = new SvgRenderer(SAMPLE_SVG);
    const svgEl = renderer.getElement();

    expect(svgEl.tagName.toLowerCase()).toBe("svg");
    expect(svgEl.getAttribute("width")).toBe("100%");
    expect(svgEl.getAttribute("height")).toBe("100%");

    const viewport = svgEl.querySelector("g.scanspace-viewport");
    expect(viewport).toBeDefined();
    expect(viewport?.querySelector("#walls")).toBeDefined();
    expect(viewport?.querySelector("#furniture_couch")).toBeDefined();
  });

  it("indexes data-scanspace elements correctly", () => {
    const renderer = new SvgRenderer(SAMPLE_SVG);
    const data = renderer.getSvgData();

    expect(data.length).toBe(2);

    const wallData = data.find((d) => d.type === "wall");
    expect(wallData).toBeDefined();
    expect(wallData?.roomId).toBe("room_living");

    const furnData = renderer.findByFurnitureId("furn_sofa");
    expect(furnData).toBeDefined();
    expect(furnData?.type).toBe("furniture");
    expect(furnData?.furnitureType).toBe("sofa");
    expect(furnData?.entityId).toBe("light.living_room_corner");

    const roomItems = renderer.findByRoomId("room_living");
    expect(roomItems.length).toBe(2);
  });

  it("applies entity state styling dynamically", () => {
    const renderer = new SvgRenderer(SAMPLE_SVG);
    const config: FloorplanCardConfig = {
      type: "custom:scanspace-floorplan",
      house_id: "house_01",
      entity_state_visualization: {
        "light.living_room_corner": {
          on: {
            fill: "#ffcc00",
            stroke: "#ff9900",
            width: 2,
          },
          off: {
            fill: "#222222",
          },
        },
      },
    };

    // Apply 'on' state
    renderer.applyEntityState("light.living_room_corner", "on", config);
    const furnData = renderer.findByFurnitureId("furn_sofa");
    expect(furnData?.element.getAttribute("fill")).toBe("#ffcc00");
    expect(furnData?.element.getAttribute("stroke")).toBe("#ff9900");
    expect(furnData?.element.getAttribute("stroke-width")).toBe("2");

    // Apply 'off' state
    renderer.applyEntityState("light.living_room_corner", "off", config);
    expect(furnData?.element.getAttribute("fill")).toBe("#222222");
  });

  it("throws error for non-svg markup", () => {
    expect(() => new SvgRenderer("<div>Invalid SVG</div>")).toThrow("Invalid SVG");
  });
});
