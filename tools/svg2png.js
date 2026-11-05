// svg2png.js — node tools/svg2png.js in.svg out.png [width]
// Rasterises an SVG with sharp (librsvg). Used by tools/make_hex.py.
let sharp;
try { sharp = require("sharp"); } catch (e) { sharp = require(require("path").join(__dirname, "deck", "node_modules", "sharp")); }
const [, , inp, out, w] = process.argv;
sharp(require("fs").readFileSync(inp), { density: 300 })
  .resize(parseInt(w || "1024", 10))
  .png()
  .toFile(out)
  .catch((e) => { console.error(e); process.exit(1); });
