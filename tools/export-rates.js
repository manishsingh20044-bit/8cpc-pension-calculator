// Writes assets/rates.json from CONFIG in assets/app.js.
// CONFIG is the single source of truth; rates.json is a public, machine-readable
// copy (not loaded by the pages). Run: node tools/export-rates.js  (build.py runs it)
const fs = require("fs"), path = require("path");
const { CONFIG } = require("../assets/app.js");
const out = { _note: "Generated from CONFIG in /assets/app.js by tools/export-rates.js. Do not edit by hand.", ...CONFIG };
const file = path.join(__dirname, "..", "assets", "rates.json");
fs.writeFileSync(file, JSON.stringify(out, null, 2) + "\n");
console.log("wrote", path.relative(process.cwd(), file));
