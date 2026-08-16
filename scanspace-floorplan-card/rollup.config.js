import resolve from "@rollup/plugin-node-resolve";
import typescript from "@rollup/plugin-typescript";

export default {
  input: "src/floorplan-card.ts",
  output: {
    file: "dist/scanspace-floorplan-card.js",
    format: "es",
  },
  plugins: [resolve(), typescript({ tsconfig: "./tsconfig.json" })],
};
