// build.js — node tools/deck/build.js 1 2 3   (or "all")
// Builds sessions/sNN/slides/EEGB_SNN_<Title>.pptx from tools/deck/content/sNN.js
const path = require("path");
const fs = require("fs");
const { Deck, ROOT } = require("./lib");
const sessions = require("../sessions.json");

function fileName(s) {
  const t = s.title.replace(/[—–\-&:,]/g, " ").replace(/[^A-Za-z0-9 ]/g, "").trim().replace(/\s+/g, "_");
  return `EEGB_S${String(s.num).padStart(2, "0")}_${t}.pptx`;
}
async function build(num) {
  const s = sessions.find(x => x.num === num);
  const contentFile = path.join(__dirname, "content", `${s.slug}.js`);
  if (!fs.existsSync(contentFile)) { console.log("no content for", s.slug); return; }
  delete require.cache[require.resolve(contentFile)];
  const fig = (id) => path.join(ROOT, "sessions", s.slug, "figures", "python", `${s.slug}_${id}.png`);
  const script = (id) => `sessions/${s.slug}/R|python/${s.slug}_figures  (${id})`;
  const slides = require(contentFile)({ s, fig, script });
  const deck = new Deck({ ...s, notes: slides.titleNotes });
  await deck.run(slides);
  await deck.save(path.join(ROOT, "sessions", s.slug, "slides", fileName(s)));
}
(async () => {
  const args = process.argv.slice(2);
  const nums = args[0] === "all" ? sessions.map(s => s.num) : args.map(Number);
  for (const n of nums) await build(n);
})().catch(e => { console.error(e); process.exit(1); });
module.exports = { fileName };
