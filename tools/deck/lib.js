// lib.js — EEGB deck engine (adapted from the DA-1 engine). Reproduces the Lagos Business School Session 1 look
// (navy title slides, teal kickers, Cambria headings, soft card grids) from a
// plain content spec, so all 16 decks share one consistent design.
// pptxgenjs writes one <a:pPr> per text run, so a bullet paragraph containing
// bold/italic runs loses its bullet. We load the library with a one-line patch
// that emits paragraph properties only for the first run of each paragraph.
const Module = require("module");
const pptxgen = (() => {
  let file; try { file = require.resolve("pptxgenjs"); } catch (e) { file = require.resolve("/opt/cowork-node-tools/node_modules/pptxgenjs"); }
  let src = require("fs").readFileSync(file, "utf8");
  const target = "paragraphPropXml = genXmlParagraphProperties(textObj, false);";
  src = src.replace(target, "paragraphPropXml = idx === 0 ? genXmlParagraphProperties(textObj, false) : '';");
  const m = new Module(file, module); m.filename = file; m.paths = Module._nodeModulePaths(require("path").dirname(file));
  m._compile(src, file);
  return m.exports.default || m.exports;
})();
let sharp;
try { sharp = require("sharp"); } catch (e) { sharp = require("/opt/cowork-node-tools/node_modules/sharp"); }
const path = require("path");
const fs = require("fs");

const C = {
  navy: "122867", teal: "0A6AA1", teal2: "0088C7", gold: "D99A2B", cyan: "00AEEF", lbs: "2E3A6E", deep: "0E1A45", ink: "1A2233", muted: "5C6B7A",
  card: "F3F6F9", border: "E1E7EE", rust: "B5541A", pale: "AAB9CC", pale2: "C7D3E3", white: "FFFFFF",
  circ1: "2C2C4E", circ2: "17305C", code: "0F1535", green: "2E7D5B",
};
const HEAD = "Cambria", BODY = "Calibri", MONO = "Courier New";
const W = 13.333, H = 7.5, MX = 0.7;
const ROOT = path.resolve(__dirname, "..", "..");
const LOGO = path.join(ROOT, "assets", "logos");
const LBS = path.join(ROOT, "assets", "lbs");
const COURSE = { code: "EEGB", cohort: "MEMBA 14", name: "ECONOMIC ENVIRONMENT OF GLOBAL BUSINESS",
  tagline: "From markets, to macro, to decisions that matter — in Nigeria and the world.",
  book: "Economic Environment of Global Business  ·  Lagos Business School  ·  Prof. Bongo Adi, Kelechi Nnamdi, Elvis Ozegbe" };
const PART_NAMES = { 1: "PART I", 2: "PART II", 3: "PART III", 4: "PART IV" };

// ---------- icons ----------
// Icons are drawn as glyphs (no React dependency). Content files keep Font-Awesome-style names;
// each name maps to a symbol below, and unknown names fall back to a dot.
const GLYPH = {
  FaChartLine: "↗", FaChartBar: "▥", FaChartPie: "◔", FaChartArea: "◭", FaArrowUp: "↑", FaArrowDown: "↓",
  FaArrowRight: "→", FaArrowsAltH: "↔", FaExchangeAlt: "⇄", FaSync: "↻", FaRedo: "↻", FaBalanceScale: "⚖",
  FaGavel: "⚖", FaCog: "⚙", FaCogs: "⚙", FaTools: "⚙", FaSlidersH: "☰", FaList: "☰", FaListOl: "☰",
  FaCheck: "✓", FaCheckCircle: "✓", FaTimes: "✗", FaTimesCircle: "✗", FaExclamationTriangle: "⚠", FaBolt: "⚡",
  FaSun: "☀", FaLeaf: "❦", FaSeedling: "❦", FaGlobe: "◍", FaGlobeAfrica: "◍", FaShip: "⚓", FaAnchor: "⚓",
  FaPlane: "✈", FaTruck: "⛟", FaIndustry: "⌂", FaBuilding: "⌂", FaHome: "⌂", FaUniversity: "⌂", FaLandmark: "⌂",
  FaStar: "★", FaFlag: "⚑", FaBullseye: "◎", FaCrosshairs: "◎", FaSearch: "⌕", FaQuestion: "?", FaQuestionCircle: "?",
  FaLightbulb: "✦", FaBrain: "✦", FaMagic: "✦", FaRobot: "⚙", FaUsers: "☺", FaUser: "☺", FaUserTie: "☺",
  FaHandshake: "✋", FaHandHoldingUsd: "$", FaDollarSign: "$", FaMoneyBillWave: "$", FaCoins: "¢", FaPiggyBank: "$",
  FaPercent: "%", FaPercentage: "%", FaCalculator: "±", FaSquareRootAlt: "√", FaInfinity: "∞", FaSigma: "Σ",
  FaClock: "◷", FaHourglassHalf: "⧗", FaCalendarAlt: "▦", FaCalendar: "▦", FaTable: "▦", FaDatabase: "⛁",
  FaFileAlt: "✎", FaPen: "✎", FaPencilAlt: "✎", FaEdit: "✎", FaBook: "❐", FaBookOpen: "❐", FaNewspaper: "❐",
  FaComments: "❝", FaComment: "❝", FaBullhorn: "❢", FaLock: "⚿", FaShieldAlt: "⛨", FaUmbrella: "☂",
  FaFire: "♨", FaThermometerHalf: "♨", FaWater: "≈", FaWind: "≋", FaOilCan: "⛽", FaGasPump: "⛽", FaCar: "⛐",
  FaLayerGroup: "≡", FaSitemap: "⋔", FaProjectDiagram: "⋔", FaNetworkWired: "⋔", FaLink: "∞", FaRoute: "⤳",
  FaMobileAlt: "▯", FaLaptopCode: "⌨", FaLaptop: "⌨", FaCode: "⌨", FaRProject: "R", FaPython: "Py",
  FaShoppingCart: "⊕", FaStore: "⌂", FaBox: "▣", FaBoxes: "▣", FaCube: "▣", FaWarehouse: "⌂",
  FaDice: "⚄", FaRandom: "⤨", FaFilter: "⏚", FaMicroscope: "⌕", FaEye: "◉", FaSignal: "▂", FaTachometerAlt: "◔",
  FaHeartbeat: "♥", FaMedkit: "+", FaPlus: "+", FaMinus: "−", FaEquals: "=", FaNotEqual: "≠", FaGem: "◆",
  FaRulerHorizontal: "⟷", FaRuler: "⟷", FaCompass: "✵", FaMap: "▤", FaMapMarkerAlt: "⌖", FaTrophy: "♛",
  FaGraduationCap: "♔", FaChalkboardTeacher: "♔", FaClipboardList: "☷", FaClipboardCheck: "☑", FaTasks: "☑",
  FaHighlighter: "✎", FaPalette: "✿", FaKey: "⚷", FaCut: "✂", FaFlask: "⚗", FaVial: "⚗", FaBug: "✱",
  FaUnlink: "⊘", FaBan: "⊘", FaStop: "■", FaPlay: "▶", FaForward: "»", FaStepForward: "»", FaLevelUpAlt: "⤴",
  FaLevelDownAlt: "⤵", FaArrowCircleUp: "↑", FaArrowCircleDown: "↓", FaCompressArrowsAlt: "⤡",
  FaExpandArrowsAlt: "⤢", FaCircle: "●", FaBriefcase: "▣",
};
const iconCache = {};
let FA = {};
try { FA = require("@fortawesome/free-solid-svg-icons"); } catch (e) { }
const FA_ALIAS = { FaRProject: null, FaPython: null, FaBriefcase: "faBriefcase" };
async function icon(name, color = "FFFFFF") {
  const key = name + color;
  if (iconCache[key]) return iconCache[key];
  const faName = FA_ALIAS[name] !== undefined ? FA_ALIAS[name] : "fa" + name.slice(2);
  const def = faName && FA[faName];
  if (def) {
    const [w, h, , , d] = def.icon; const pth = Array.isArray(d) ? d.join(" ") : d;
    const sz = Math.max(w, h); const ox = (sz - w) / 2, oy = (sz - h) / 2;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="${-ox} ${-oy} ${sz} ${sz}"><path fill="#${color}" d="${pth}"/></svg>`;
    const buf = await sharp(Buffer.from(svg)).png().toBuffer();
    iconCache[key] = "image/png;base64," + buf.toString("base64");
    return iconCache[key];
  }
  const g = GLYPH[name] || "●";
  const fsz = g.length > 1 ? 130 : 200;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">` +
    `<text x="128" y="128" dominant-baseline="central" text-anchor="middle" font-family="DejaVu Sans, Segoe UI Symbol, Arial" ` +
    `font-weight="700" font-size="${fsz}" fill="#${color}">${g.replace("&", "&amp;").replace("<", "&lt;")}</text></svg>`;
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  iconCache[key] = "image/png;base64," + buf.toString("base64");
  return iconCache[key];
}
async function iconCircle(slide, name, x, y, d, fill = C.teal) {
  slide.addShape("ellipse", { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
  const pad = d * 0.25;
  slide.addImage({ data: await icon(name), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad });
}

// ---------- shared text helpers ----------
function T(slide, text, o) {
  slide.addText(text, Object.assign({ isTextBox: true, fontFace: BODY, color: C.ink, margin: 0, valign: "top" }, o));
}
function card(slide, x, y, w, h, fill = C.card) {
  slide.addShape("roundRect", { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: C.border, width: 0.75 },
    shadow: { type: "outer", color: "000000", opacity: 0.08, blur: 6, offset: 2, angle: 90 } });
}
function rich(str, base = {}) {
  // **bold** and _italic_ inline markup -> text runs
  const parts = []; const re = /(\*\*[^*]+\*\*|(?<![A-Za-z0-9])_[^_]+_(?![A-Za-z0-9]))/g; let last = 0, m;
  while ((m = re.exec(str))) {
    if (m.index > last) parts.push({ text: str.slice(last, m.index), options: { ...base } });
    const t = m[0];
    if (t.startsWith("**")) parts.push({ text: t.slice(2, -2), options: { ...base, bold: true } });
    else parts.push({ text: t.slice(1, -1), options: { ...base, italic: true } });
    last = m.index + t.length;
  }
  if (last < str.length) parts.push({ text: str.slice(last), options: { ...base } });
  return parts.length ? parts : [{ text: str, options: base }];
}
function bullets(items, o = {}) {
  const out = [];
  items.forEach((it, i) => {
    const runs = rich(it, { fontSize: o.fontSize || 14, color: o.color || C.ink });
    runs[0].options = { ...runs[0].options, bullet: o.bullet === false ? false : { indent: 14 }, paraSpaceAfter: o.space || 6 };
    runs[runs.length - 1].options.breakLine = i < items.length - 1;
    out.push(...runs);
  });
  return out;
}

class Deck {
  constructor(meta) {
    this.m = meta;               // {num, title, short, module, source, chapters}
    this.p = new pptxgen();
    this.p.layout = "LAYOUT_WIDE";
    this.p.author = "Prof. Bongo Adi, Kelechi Nnamdi, Elvis Ozegbe — Lagos Business School";
    this.p.company = "Lagos Business School, Pan-Atlantic University";
    this.p.title = `EEGB Session ${meta.num}: ${meta.title}`;
    this.n = 0;
  }
  footerText() { return `SESSION ${this.m.num}  ·  ${(this.m.short || this.m.title).toUpperCase()}`; }

  frame(spec) {
    const s = this.p.addSlide(); this.n++;
    s.background = { color: C.white };
    // LBS brand: logo top-right, navy footer band with cyan rule
    s.addImage({ path: path.join(LBS, "lbs_logo_navy.png"), x: 11.42, y: 0.32, w: 1.45, h: 0.495 });
    s.addShape("rect", { x: 0, y: 7.08, w: W, h: 0.04, fill: { color: C.cyan }, line: { color: C.cyan } });
    s.addShape("rect", { x: 0, y: 7.12, w: W, h: 0.38, fill: { color: C.navy }, line: { color: C.navy } });
    T(s, `LAGOS BUSINESS SCHOOL  ·  EEGB  ·  ${this.footerText()}`, { x: MX, y: 7.12, w: 9.5, h: 0.38, fontSize: 8.5, color: C.white, charSpacing: 2, valign: "middle" });
    T(s, String(this.n), { x: 11.9, y: 7.12, w: 0.5, h: 0.38, fontSize: 9, bold: true, color: C.white, align: "right", valign: "middle" });
    s.addImage({ path: path.join(LOGO, "eegb_hex_256.png"), x: 12.6, y: 7.14, w: 0.34, h: 0.34 });
    if (spec.kicker) {
      s.addShape("rect", { x: MX, y: 0.47, w: 0.06, h: 0.24, fill: { color: C.cyan }, line: { color: C.cyan } });
      T(s, spec.kicker.toUpperCase(), { x: MX + 0.16, y: 0.45, w: 9.8, h: 0.3, fontSize: 11.5, bold: true, color: C.teal2, charSpacing: 3 });
    }
    let bx = 9.75;
    if (spec.study) {
      s.addShape("roundRect", { x: bx, y: 0.44, w: 1.45, h: 0.3, rectRadius: 0.15, fill: { color: C.gold }, line: { color: C.gold } });
      T(s, "SELF-STUDY", { x: bx, y: 0.44, w: 1.45, h: 0.3, fontSize: 9, bold: true, color: C.white, align: "center", valign: "middle", charSpacing: 2 });
      bx -= 1.6;
    }
    if (spec.illus) {
      s.addShape("roundRect", { x: bx, y: 0.44, w: 1.45, h: 0.3, rectRadius: 0.15, fill: { color: C.white }, line: { color: C.rust, width: 1 } });
      T(s, "ILLUSTRATIVE", { x: bx, y: 0.44, w: 1.45, h: 0.3, fontSize: 9, bold: true, color: C.rust, align: "center", valign: "middle", charSpacing: 2 });
    }
    if (spec.title) T(s, spec.title, { x: MX, y: 0.74, w: spec.titleW || 10.5, h: 0.7, fontFace: HEAD, fontSize: spec.titleSize || 28, bold: true, color: C.navy, valign: "middle", fit: "shrink" });
    if (spec.sub) T(s, spec.sub, { x: MX, y: 1.44, w: 11.9, h: 0.35, fontSize: 13, italic: true, color: C.muted });
    if (spec.notes) s.addNotes(spec.notes);
    return s;
  }
  dark(spec, img = "campus_dark.jpg") {
    const s = this.p.addSlide(); this.n++;
    s.background = { color: C.deep };
    s.addImage({ path: path.join(LBS, img), x: 0, y: 0, w: W, h: H });
    s.addShape("rect", { x: 0, y: 7.2, w: W, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });
    s.addImage({ path: path.join(LBS, "lbs_logo_white.png"), x: 11.15, y: 0.35, w: 1.75, h: 0.6 });
    if (spec.notes) s.addNotes(spec.notes);
    return s;
  }

  // ---------------- slide types ----------------
  async title() {
    const s = this.dark({ notes: this.m.notes || "" }, "campus_dark.jpg");
    const mod = this.m.part ? `  ·  ${PART_NAMES[this.m.part]}` : "";
    T(s, `${COURSE.name}  ·  ${COURSE.cohort}${mod}`, { x: 0.9, y: 1.15, w: 9.8, h: 0.35, fontSize: 12.5, bold: true, color: C.gold, charSpacing: 3 });
    s.addShape("rect", { x: 0.9, y: 1.62, w: 1.2, h: 0.05, fill: { color: C.cyan }, line: { color: C.cyan } });
    T(s, `SESSION ${this.m.num}`, { x: 0.9, y: 1.85, w: 6, h: 0.55, fontFace: HEAD, fontSize: 26, bold: true, color: C.pale2 });
    T(s, this.m.titleLines || this.m.title, { x: 0.9, y: 2.45, w: 8.6, h: 1.9, fontFace: HEAD, fontSize: 40, bold: true, color: C.white, valign: "middle", fit: "shrink" });
    T(s, this.m.tagline || COURSE.tagline, { x: 0.9, y: 4.5, w: 8.4, h: 0.45, fontSize: 16, italic: true, color: C.pale2 });
    await iconCircle(s, "FaBookOpen", 0.85, 5.3, 0.55, C.teal2);
    T(s, `Reading: ${this.m.source}${this.m.facilitator ? "   ·   Facilitator: " + this.m.facilitator : ""}`, { x: 1.6, y: 5.38, w: 7.8, h: 0.4, fontSize: 12.5, color: C.white, valign: "middle" });
    T(s, "Lagos Business School  ·  Pan-Atlantic University  ·  MEMBA 14  ·  Prof. Bongo Adi, Kelechi Nnamdi, Elvis Ozegbe, Sumendra Dash", { x: 0.9, y: 6.55, w: 11, h: 0.3, fontSize: 10.5, color: C.pale });
    const hex = this.m.part ? `eegb_hex_p${this.m.part}.png` : "eegb_hex.png";
    s.addImage({ path: path.join(LOGO, hex), x: 9.85, y: 2.0, w: 2.9, h: 2.9 });
  }

  section(spec) {
    const s = this.dark(spec, "campus_darker.jpg");
    T(s, spec.label || "PART", { x: 0.9, y: 2.0, w: 6, h: 0.35, fontSize: 13, bold: true, color: C.gold, charSpacing: 4 });
    T(s, spec.num ? String(spec.num).padStart(2, "0") : "", { x: 0.9, y: 2.35, w: 3, h: 1.2, fontFace: HEAD, fontSize: 72, bold: true, color: C.cyan });
    T(s, spec.title, { x: 0.9, y: 3.6, w: 9.5, h: 1.0, fontFace: HEAD, fontSize: 36, bold: true, color: C.white, valign: "middle" });
    if (spec.sub) T(s, spec.sub, { x: 0.9, y: 4.65, w: 9, h: 0.8, fontSize: 16, italic: true, color: C.pale2 });
    if (spec.question) {
      s.addShape("roundRect", { x: 0.9, y: 5.55, w: 9.2, h: 0.95, rectRadius: 0.08, fill: { color: C.deep, transparency: 20 }, line: { color: C.cyan, width: 1 } });
      T(s, rich("**The question this part answers:** " + spec.question, { fontSize: 14, color: C.white }), { x: 1.15, y: 5.55, w: 8.8, h: 0.95, valign: "middle" });
    }
    s.addImage({ path: path.join(LOGO, this.m.part ? `eegb_hex_p${this.m.part}.png` : "eegb_hex.png"), x: 10.4, y: 2.4, w: 2.3, h: 2.3 });
  }

  async hook(spec) {
    const s = this.dark(spec);
    T(s, (spec.kicker || "THE HOOK").toUpperCase(), { x: 0.9, y: 0.55, w: 8, h: 0.3, fontSize: 11.5, bold: true, color: C.gold, charSpacing: 3 });
    T(s, spec.title, { x: 0.9, y: 0.85, w: 11, h: 0.7, fontFace: HEAD, fontSize: 28, bold: true, color: C.white });
    await iconCircle(s, spec.icon || "FaLightbulb", 0.9, 1.95, 0.75, C.gold);
    T(s, spec.quote, { x: 1.9, y: 1.85, w: 10.2, h: 1.1, fontFace: HEAD, fontSize: 20, italic: true, color: C.white, valign: "middle" });
    if (spec.intro) T(s, spec.intro, { x: 0.9, y: 3.25, w: 11.4, h: 0.5, fontSize: 15, color: C.pale2 });
    const pts = spec.points || []; const cw = 11.6 / pts.length;
    for (let i = 0; i < pts.length; i++) {
      const x = 0.9 + i * cw;
      await iconCircle(s, pts[i].icon || "FaCheck", x, 4.05, 0.5, C.teal2);
      T(s, pts[i].title, { x: x + 0.65, y: 4.08, w: cw - 0.8, h: 0.45, fontSize: 16, bold: true, color: C.white, valign: "middle" });
      T(s, pts[i].body, { x: x, y: 4.75, w: cw - 0.35, h: 1.6, fontSize: 13.5, color: C.pale2 });
    }
  }

  async agenda(spec) {
    const s = this.frame({ kicker: "TODAY'S PLAN", title: spec.title || `Session ${this.m.num} at a Glance — 75 Minutes`, sub: spec.sub, notes: spec.notes });
    const total = spec.blocks.reduce((a, b) => a + b.min, 0); let x = MX; const tw = 11.9;
    const cols = [C.teal, C.teal2, C.gold, C.teal, C.teal2, C.navy];
    spec.blocks.forEach((b, i) => {
      const w = tw * b.min / total;
      s.addShape("rect", { x, y: 2.05, w: w - 0.04, h: 0.42, fill: { color: cols[i % cols.length] }, line: { color: C.white } });
      T(s, `${b.min}'`, { x, y: 2.05, w: w - 0.04, h: 0.42, fontSize: 12, bold: true, color: C.white, align: "center", valign: "middle" });
      x += w;
    });
    const n = spec.blocks.length, gap = 0.22, cw = (11.9 - gap * (n - 1)) / n;
    for (let i = 0; i < n; i++) {
      const b = spec.blocks[i], cx = MX + i * (cw + gap);
      card(s, cx, 2.8, cw, 3.7);
      await iconCircle(s, b.icon || "FaClock", cx + cw / 2 - 0.35, 3.05, 0.7, i === 2 ? C.gold : C.teal);
      T(s, b.label, { x: cx + 0.15, y: 3.95, w: cw - 0.3, h: 0.6, fontFace: HEAD, fontSize: 14.5, bold: true, color: C.navy, align: "center", valign: "middle" });
      T(s, b.desc, { x: cx + 0.2, y: 4.6, w: cw - 0.4, h: 1.8, fontSize: 12, color: C.muted, align: "center" });
    }
  }

  async objectives(spec) {
    const s = this.frame({ kicker: "BY THE END OF TODAY", title: spec.title || `Session ${this.m.num} Learning Objectives`, sub: "You will be able to:", notes: spec.notes });
    const n = spec.items.length, gap = 0.3, cw = (11.9 - gap * (n - 1)) / n;
    for (let i = 0; i < n; i++) {
      const it = spec.items[i], x = MX + i * (cw + gap);
      card(s, x, 2.1, cw, 4.3);
      T(s, String(i + 1).padStart(2, "0"), { x: x + 0.3, y: 2.35, w: 1.2, h: 0.6, fontFace: HEAD, fontSize: 30, bold: true, color: C.pale2 });
      await iconCircle(s, it.icon || "FaBullseye", x + cw - 0.95, 2.35, 0.62, C.teal);
      T(s, it.title, { x: x + 0.3, y: 3.25, w: cw - 0.6, h: 0.75, fontFace: HEAD, fontSize: 17, bold: true, color: C.navy, valign: "middle" });
      T(s, it.body, { x: x + 0.3, y: 4.1, w: cw - 0.6, h: 2.1, fontSize: 13.5, color: C.muted });
    }
  }

  async cards(spec) {
    const s = this.frame(spec);
    const cs = spec.cards, n = cs.length;
    const perRow = spec.perRow || (n <= 4 ? n : Math.ceil(n / 2)); const rows = Math.ceil(n / perRow);
    const gap = 0.25, top = spec.sub ? 2.05 : 1.85, bottom = spec.note ? 5.95 : 6.7;
    const cw = (11.9 - gap * (perRow - 1)) / perRow;
    let ch = (bottom - top - gap * (rows - 1)) / rows;
    const compact = rows > 1;
    if (!compact) ch = Math.min(ch, spec.maxH || 3.9);
    for (let i = 0; i < n; i++) {
      const c = cs[i], r = Math.floor(i / perRow), k = i % perRow;
      const x = MX + k * (cw + gap), y = top + r * (ch + gap);
      card(s, x, y, cw, ch, c.fill || C.card);
      const d = compact ? 0.5 : 0.68;
      let ty;
      if (compact) {
        await iconCircle(s, c.icon || "FaCircle", x + 0.25, y + 0.22, d, c.accent ? C.gold : C.teal);
        T(s, c.title, { x: x + 0.9, y: y + 0.2, w: cw - 1.05, h: 0.55, fontFace: HEAD, fontSize: 15, bold: true, color: C.navy, valign: "middle" });
        ty = y + 0.85;
      } else {
        await iconCircle(s, c.icon || "FaCircle", x + cw / 2 - d / 2, y + 0.28, d, c.accent ? C.gold : C.teal);
        T(s, c.title, { x: x + 0.2, y: y + 1.1, w: cw - 0.4, h: 0.6, fontFace: HEAD, fontSize: 16, bold: true, color: C.navy, align: "center", valign: "middle" });
        ty = y + 1.75;
      }
      if (c.tag) { T(s, c.tag, { x: x + 0.2, y: ty - 0.05, w: cw - 0.4, h: 0.35, fontSize: 12.5, italic: true, color: C.gold, align: compact ? "left" : "center" }); ty += 0.38; }
      const footH = c.foot ? 0.55 : 0;
      T(s, rich(c.body, { fontSize: spec.bodySize || (compact ? 12.5 : 13), color: C.ink }), { x: x + 0.25, y: ty, w: cw - 0.5, h: y + ch - ty - 0.15 - footH, align: compact ? "left" : "center" });
      if (c.foot) T(s, c.foot, { x: x + 0.25, y: y + ch - 0.6, w: cw - 0.5, h: 0.45, fontSize: 11, italic: true, color: C.muted, align: compact ? "left" : "center" });
    }
    if (spec.note) this.noteBar(s, spec.note, compact ? 6.15 : Math.min(6.15, top + ch + 0.3));
  }

  noteBar(s, text, y = 6.15, h = 0.6) {
    s.addShape("roundRect", { x: MX, y, w: 11.9, h, rectRadius: 0.06, fill: { color: C.card }, line: { color: C.border, width: 0.75 } });
    T(s, rich(text, { fontSize: 13, color: C.navy, italic: true }), { x: MX + 0.25, y, w: 11.4, h, valign: "middle" });
  }

  async rows(spec) {
    const s = this.frame(spec);
    const rs = spec.rows, n = rs.length, top = spec.sub ? 2.0 : 1.8, bottom = spec.note ? 6.0 : 6.75;
    const rh = (bottom - top) / n, d = Math.min(0.7, rh - 0.18);
    const lw = spec.labelW || 2.6;
    for (let i = 0; i < n; i++) {
      const r = rs[i], y = top + i * rh;
      await iconCircle(s, r.icon || "FaCircle", MX, y + (rh - d) / 2, d, r.accent ? C.gold : C.teal);
      T(s, r.label, { x: MX + d + 0.25, y, w: lw, h: rh, fontFace: HEAD, fontSize: 16, bold: true, color: C.navy, valign: "middle" });
      const bx = MX + d + 0.35 + lw;
      s.addShape("roundRect", { x: bx, y: y + 0.07, w: 12.6 - bx, h: rh - 0.14, rectRadius: 0.06, fill: { color: C.card }, line: { color: C.border, width: 0.75 } });
      T(s, rich(r.text, { fontSize: spec.textSize || 13.5, color: C.ink }), { x: bx + 0.3, y: y + 0.07, w: 12.6 - bx - 0.5, h: rh - 0.14, valign: "middle" });
    }
    if (spec.note) this.noteBar(s, spec.note, 6.15);
  }

  async chain(spec) {
    const s = this.frame(spec);
    const st = spec.steps, n = st.length, sw = 11.9 / n;
    for (let i = 0; i < n; i++) {
      const x = MX + i * sw, d = 0.95;
      await iconCircle(s, st[i].icon || "FaCircle", x + sw / 2 - d / 2, 2.35, d, st[i].accent ? C.gold : C.teal);
      if (i < n - 1) T(s, "›", { x: x + sw - 0.3, y: 2.45, w: 0.6, h: 0.7, fontSize: 34, color: C.pale, align: "center", valign: "middle" });
      T(s, st[i].label, { x: x + 0.1, y: 3.45, w: sw - 0.2, h: 0.5, fontFace: HEAD, fontSize: 16, bold: true, color: C.navy, align: "center" });
      T(s, st[i].desc, { x: x + 0.15, y: 4.0, w: sw - 0.3, h: 1.6, fontSize: 12.5, color: C.muted, align: "center" });
    }
    if (spec.note) this.noteBar(s, spec.note, 5.85, 0.75);
  }

  async concept(spec) {
    const s = this.frame(spec);
    const top = spec.sub ? 2.05 : 1.85;
    // left: plain English
    card(s, MX, top, 6.1, 6.7 - top);
    await iconCircle(s, spec.icon || "FaComments", MX + 0.3, top + 0.28, 0.55, C.teal);
    T(s, "IN PLAIN ENGLISH", { x: MX + 1.0, y: top + 0.3, w: 4.5, h: 0.5, fontSize: 12, bold: true, color: C.teal2, charSpacing: 3, valign: "middle" });
    T(s, rich(spec.plain, { fontSize: 15, color: C.ink }), { x: MX + 0.35, y: top + 1.0, w: 5.4, h: 2.3 });
    if (spec.example) {
      T(s, "EXAMPLE", { x: MX + 0.35, y: top + 3.35, w: 4, h: 0.3, fontSize: 11, bold: true, color: C.gold, charSpacing: 3 });
      T(s, rich(spec.example, { fontSize: 13, color: C.muted }), { x: MX + 0.35, y: top + 3.7, w: 5.4, h: 6.6 - top - 3.85 });
    }
    // right: formula + why
    const rx = 7.05, rw = 5.55;
    if (spec.formula) {
      s.addShape("roundRect", { x: rx, y: top, w: rw, h: 2.0, rectRadius: 0.08, fill: { color: C.navy }, line: { color: C.navy } });
      T(s, "THE FORMULA", { x: rx + 0.3, y: top + 0.18, w: 3, h: 0.3, fontSize: 11, bold: true, color: C.gold, charSpacing: 3 });
      T(s, spec.formula, { x: rx + 0.3, y: top + 0.5, w: rw - 0.6, h: 0.85, fontFace: HEAD, fontSize: spec.formulaSize || 24, color: C.white, align: "center", valign: "middle" });
      if (spec.formulaNote) T(s, spec.formulaNote, { x: rx + 0.3, y: top + 1.38, w: rw - 0.6, h: 0.55, fontSize: 11.5, italic: true, color: C.pale2, align: "center" });
    }
    const wy = spec.formula ? top + 2.25 : top;
    card(s, rx, wy, rw, 6.7 - wy);
    await iconCircle(s, "FaBriefcase", rx + 0.3, wy + 0.25, 0.5, C.gold);
    T(s, "WHY A MANAGER CARES", { x: rx + 0.95, y: wy + 0.27, w: 4, h: 0.45, fontSize: 12, bold: true, color: C.teal2, charSpacing: 3, valign: "middle" });
    T(s, rich(spec.why, { fontSize: 13.5, color: C.ink }), { x: rx + 0.3, y: wy + 0.9, w: rw - 0.6, h: 6.7 - wy - 1.05 });
  }

  async figure(spec) {
    const s = this.frame(spec);
    const top = spec.sub ? 1.95 : 1.75;
    const img = spec.img; const iw = spec.points ? 7.9 : 11.9;
    const maxH = 6.75 - top - 0.3;
    let w = iw, h = iw * 0.56;
    try {
      const meta = await sharp(img).metadata(); const ar = meta.height / meta.width;
      h = w * ar; if (h > maxH) { h = maxH; w = h / ar; }
    } catch (e) { }
    const ix = MX + (iw - w) / 2;
    s.addImage({ path: img, x: ix, y: top, w, h });
    if (spec.fig) T(s, `Fig ${spec.fig}  ·  replicate: ${spec.script || ""}`, { x: MX, y: top + h + 0.05, w: iw, h: 0.25, fontSize: 9, italic: true, color: C.muted, align: "center" });
    if (spec.points) {
      const px = 8.85, pw = 3.75;
      card(s, px, top, pw, 6.7 - top);
      T(s, spec.panelTitle || "WHAT TO SEE", { x: px + 0.3, y: top + 0.25, w: pw - 0.6, h: 0.3, fontSize: 11.5, bold: true, color: C.teal2, charSpacing: 3 });
      T(s, bullets(spec.points, { fontSize: spec.pointSize || 13, space: 9 }), { x: px + 0.25, y: top + 0.7, w: pw - 0.5, h: 6.7 - top - 0.9 });
    }
  }

  async worked(spec) {
    const s = this.frame(spec);
    const top = spec.sub ? 2.05 : 1.85;
    const tw = spec.tableW || 5.6;
    const head = spec.table.head.map(h => ({ text: h, options: { bold: true, color: C.white, fill: { color: C.navy }, fontFace: BODY, fontSize: 12.5, align: "center" } }));
    const rows = spec.table.rows.map((r, i) => r.map((c, j) => ({ text: String(c), options: { fontSize: spec.tableSize || 12.5, fontFace: BODY, color: C.ink, align: j === 0 ? "left" : "center", fill: { color: i % 2 ? "FFFFFF" : C.card } } })));
    if (spec.table.total) rows.push(spec.table.total.map(c => ({ text: String(c), options: { bold: true, fontSize: 12.5, color: C.navy, align: "center", fill: { color: "E8EEF5" } } })));
    const rowH = Math.min(0.42, (6.7 - top) / (rows.length + 1));
    s.addTable([head, ...rows], { x: MX, y: top, w: tw, colW: spec.colW, rowH, border: { type: "solid", color: C.border, pt: 0.75 }, valign: "middle", margin: 0.06 });
    if (spec.aside) {
      const ay = spec.asideY || (top + rowH * (rows.length + 1) + 0.55);
      card(s, MX, ay, tw, 6.7 - ay, "FFF8EA");
      T(s, (spec.asideTitle || "THINK ABOUT IT").toUpperCase(), { x: MX + 0.25, y: ay + 0.18, w: tw - 0.5, h: 0.3, fontSize: 11, bold: true, color: C.gold, charSpacing: 3 });
      T(s, rich(spec.aside, { fontSize: 12.5, color: C.ink }), { x: MX + 0.25, y: ay + 0.55, w: tw - 0.5, h: 6.7 - ay - 0.7 });
    }
    const sx = MX + tw + 0.4, sw = 12.6 - sx;
    T(s, "STEP BY STEP", { x: sx, y: top, w: sw, h: 0.3, fontSize: 11.5, bold: true, color: C.teal2, charSpacing: 3 });
    const st = spec.steps; const sh = (spec.result ? 5.6 : 6.6) - top - 0.45; const each = sh / st.length;
    for (let i = 0; i < st.length; i++) {
      const y = top + 0.45 + i * each;
      s.addShape("ellipse", { x: sx, y: y + 0.03, w: 0.38, h: 0.38, fill: { color: C.teal }, line: { color: C.teal } });
      T(s, String(i + 1), { x: sx, y: y + 0.03, w: 0.38, h: 0.38, fontSize: 12, bold: true, color: C.white, align: "center", valign: "middle" });
      T(s, rich(st[i], { fontSize: 13, color: C.ink }), { x: sx + 0.55, y, w: sw - 0.55, h: each - 0.05 });
    }
    if (spec.result) {
      s.addShape("roundRect", { x: sx, y: 5.75, w: sw, h: 0.95, rectRadius: 0.06, fill: { color: C.navy }, line: { color: C.navy } });
      T(s, rich(spec.result, { fontSize: 14, color: C.white }), { x: sx + 0.25, y: 5.75, w: sw - 0.5, h: 0.95, valign: "middle" });
    }
  }

  async table(spec) {
    const s = this.frame(spec);
    const top = spec.sub ? 2.05 : 1.85;
    const fs = spec.fontSize || 13;
    const head = spec.head.map(h => ({ text: h, options: { bold: true, color: C.white, fill: { color: C.navy }, fontSize: fs, fontFace: BODY } }));
    const rows = spec.rows.map((r, i) => r.map((c, j) => ({ text: rich(String(c), { fontSize: fs, fontFace: BODY, color: j === 0 ? C.navy : C.ink, bold: j === 0 }), options: { fill: { color: i % 2 ? "FFFFFF" : C.card } } })));
    const avail = (spec.note ? 5.95 : 6.7) - top;
    s.addTable([head, ...rows], { x: MX, y: top, w: 11.9, colW: spec.colW, rowH: Math.min(spec.rowH || (rows.length <= 4 ? 0.8 : 0.5), avail / (rows.length + 1)), border: { type: "solid", color: C.border, pt: 0.75 }, valign: "middle", margin: 0.08 });
    if (spec.note) this.noteBar(s, spec.note, 6.15);
  }

  async compare(spec) {
    const s = this.frame(spec);
    const top = spec.sub ? 2.05 : 1.85, bottom = spec.note ? 5.95 : 6.7;
    const sides = [spec.left, spec.right];
    for (let i = 0; i < 2; i++) {
      const c = sides[i], x = MX + i * 6.1, w = 5.8;
      card(s, x, top, w, bottom - top);
      await iconCircle(s, c.icon || "FaCircle", x + 0.3, top + 0.28, 0.65, i ? C.gold : C.teal);
      T(s, c.title, { x: x + 1.15, y: top + 0.25, w: w - 1.4, h: 0.45, fontFace: HEAD, fontSize: 18, bold: true, color: C.navy });
      if (c.tag) T(s, c.tag, { x: x + 1.15, y: top + 0.68, w: w - 1.4, h: 0.35, fontSize: 12.5, italic: true, color: C.muted });
      T(s, bullets(c.items, { fontSize: spec.fontSize || 13.5, space: 8 }), { x: x + 0.35, y: top + 1.25, w: w - 0.7, h: bottom - top - 1.4 });
    }
    if (spec.note) this.noteBar(s, spec.note, 6.15);
  }

  async code(spec) {
    const s = this.frame(spec);
    const top = spec.sub ? 2.05 : 1.85, bottom = spec.note ? 5.95 : 6.75;
    const panes = [["R", spec.r, C.teal], ["Python", spec.py, C.gold]];
    const lines = Math.max(spec.r.split("\n").length, spec.py.split("\n").length);
    const fs = spec.fontSize || Math.max(9, Math.min(12.5, ((bottom - top - 0.55) * 72) / (lines * 1.25)));
    panes.forEach(([lab, code, col], i) => {
      const x = MX + i * 6.05, w = 5.85;
      s.addShape("roundRect", { x, y: top, w, h: bottom - top, rectRadius: 0.06, fill: { color: C.code }, line: { color: C.code } });
      s.addShape("roundRect", { x: x + 0.2, y: top + 0.15, w: 1.1, h: 0.32, rectRadius: 0.05, fill: { color: col }, line: { color: col } });
      T(s, lab, { x: x + 0.2, y: top + 0.15, w: 1.1, h: 0.32, fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle" });
      T(s, code, { x: x + 0.25, y: top + 0.6, w: w - 0.45, h: bottom - top - 0.7, fontFace: MONO, fontSize: fs, color: "E6EDF5" });
    });
    if (spec.note) this.noteBar(s, spec.note, 6.15);
  }

  async output(spec) {
    const s = this.frame(spec);
    const top = spec.sub ? 2.05 : 1.85;
    const ow = spec.outW || 6.6;
    s.addShape("roundRect", { x: MX, y: top, w: ow, h: 6.75 - top, rectRadius: 0.06, fill: { color: C.code }, line: { color: C.code } });
    T(s, spec.lang ? spec.lang + " OUTPUT" : "OUTPUT", { x: MX + 0.25, y: top + 0.15, w: 3, h: 0.3, fontSize: 10.5, bold: true, color: C.gold, charSpacing: 3 });
    T(s, spec.out, { x: MX + 0.25, y: top + 0.5, w: ow - 0.45, h: 6.75 - top - 0.6, fontFace: MONO, fontSize: spec.outSize || 11, color: "E6EDF5" });
    const ax = MX + ow + 0.3, aw = 12.6 - ax; const n = spec.reads.length; const each = (6.75 - top) / n;
    for (let i = 0; i < n; i++) {
      const y = top + i * each;
      card(s, ax, y, aw, each - 0.12);
      s.addShape("ellipse", { x: ax + 0.2, y: y + 0.18, w: 0.4, h: 0.4, fill: { color: C.gold }, line: { color: C.gold } });
      T(s, String(i + 1), { x: ax + 0.2, y: y + 0.18, w: 0.4, h: 0.4, fontSize: 12, bold: true, color: C.white, align: "center", valign: "middle" });
      T(s, spec.reads[i].label, { x: ax + 0.75, y: y + 0.13, w: aw - 0.9, h: 0.5, fontSize: 13.5, bold: true, color: C.navy, valign: "middle" });
      T(s, rich(spec.reads[i].text, { fontSize: 12.5, color: C.ink }), { x: ax + 0.25, y: y + 0.65, w: aw - 0.45, h: each - 0.85 });
    }
  }

  async check(spec) {
    const s = this.frame({ kicker: spec.kicker || "CONCEPT CHECK", title: spec.title || "Quick Check: What Would You Say?", study: spec.study, illus: spec.illus, notes: `ANSWER: ${"ABCDE"[spec.answer]}. ${spec.explain}\n\n${spec.notes || ""}` });
    await iconCircle(s, "FaQuestion", MX, 1.95, 0.7, C.gold);
    T(s, rich(spec.q, { fontSize: 19, color: C.navy }), { x: MX + 0.95, y: 1.85, w: 10.9, h: 1.2, fontFace: HEAD, valign: "middle" });
    const n = spec.options.length, oh = Math.min(0.8, (5.9 - 3.3) / n);
    spec.options.forEach((o, i) => {
      const y = 3.3 + i * (oh + 0.12);
      s.addShape("roundRect", { x: MX + 0.95, y, w: 10.9, h: oh, rectRadius: 0.06, fill: { color: C.card }, line: { color: C.border, width: 0.75 } });
      s.addShape("ellipse", { x: MX + 1.15, y: y + (oh - 0.42) / 2, w: 0.42, h: 0.42, fill: { color: C.teal }, line: { color: C.teal } });
      T(s, "ABCDE"[i], { x: MX + 1.15, y: y + (oh - 0.42) / 2, w: 0.42, h: 0.42, fontSize: 13, bold: true, color: C.white, align: "center", valign: "middle" });
      T(s, rich(o, { fontSize: 14.5, color: C.ink }), { x: MX + 1.8, y, w: 9.9, h: oh, valign: "middle" });
    });
    T(s, "Discuss with your neighbour for 60 seconds — answer and reasoning in the speaker notes.", { x: MX + 0.95, y: 6.45, w: 10.9, h: 0.3, fontSize: 11, italic: true, color: C.muted });
  }

  async mistakes(spec) {
    const s = this.frame({ kicker: spec.kicker || "WHERE MANAGERS GO WRONG", title: spec.title, sub: spec.sub, study: spec.study, illus: spec.illus, notes: spec.notes });
    const top = spec.sub ? 2.05 : 1.85, n = spec.items.length, rh = (6.7 - top - 0.45) / n;
    T(s, "THE TRAP", { x: MX + 0.6, y: top, w: 5, h: 0.3, fontSize: 11.5, bold: true, color: C.rust, charSpacing: 3 });
    T(s, "THE BETTER HABIT", { x: 7.0, y: top, w: 5, h: 0.3, fontSize: 11.5, bold: true, color: C.green, charSpacing: 3 });
    for (let i = 0; i < n; i++) {
      const y = top + 0.4 + i * rh;
      s.addShape("roundRect", { x: MX, y, w: 5.95, h: rh - 0.12, rectRadius: 0.06, fill: { color: "FBF1EC" }, line: { color: "F0D9CC", width: 0.75 } });
      s.addImage({ data: await icon("FaTimesCircle", C.rust), x: MX + 0.2, y: y + (rh - 0.12) / 2 - 0.17, w: 0.34, h: 0.34 });
      T(s, rich(spec.items[i].bad, { fontSize: 13, color: C.ink }), { x: MX + 0.7, y, w: 5.1, h: rh - 0.12, valign: "middle" });
      s.addShape("roundRect", { x: 6.85, y, w: 5.75, h: rh - 0.12, rectRadius: 0.06, fill: { color: "EEF6F1" }, line: { color: "D2E7DA", width: 0.75 } });
      s.addImage({ data: await icon("FaCheckCircle", C.green), x: 7.05, y: y + (rh - 0.12) / 2 - 0.17, w: 0.34, h: 0.34 });
      T(s, rich(spec.items[i].good, { fontSize: 13, color: C.ink }), { x: 7.55, y, w: 4.9, h: rh - 0.12, valign: "middle" });
    }
  }

  async stats(spec) {
    const s = this.frame(spec);
    const top = spec.sub ? 2.15 : 1.95, n = spec.stats.length, gap = 0.3, cw = (11.9 - gap * (n - 1)) / n;
    const bottom = spec.note ? 5.9 : 6.6;
    spec.stats.forEach((st, i) => {
      const x = MX + i * (cw + gap);
      card(s, x, top, cw, bottom - top);
      T(s, st.value, { x: x + 0.2, y: top + 0.35, w: cw - 0.4, h: 1.1, fontFace: HEAD, fontSize: st.size || 44, bold: true, color: i % 2 ? C.gold : C.teal, align: "center", valign: "middle" });
      T(s, st.label, { x: x + 0.2, y: top + 1.55, w: cw - 0.4, h: 0.55, fontSize: 15, bold: true, color: C.navy, align: "center", valign: "middle" });
      T(s, rich(st.desc || "", { fontSize: 12.5, color: C.muted }), { x: x + 0.3, y: top + 2.15, w: cw - 0.6, h: bottom - top - 2.3, align: "center" });
    });
    if (spec.note) this.noteBar(s, spec.note, 6.1);
  }

  async caseSlide(spec) {
    const s = this.frame({ kicker: spec.kicker || "NIGERIAN BUSINESS CASE", title: spec.title, sub: spec.sub, study: spec.study, illus: spec.illus, notes: spec.notes });
    const top = spec.sub ? 2.05 : 1.85;
    const blocks = [["FaBuilding", "The situation", spec.context], ["FaQuestionCircle", "The decision question", spec.question],
                    ["FaDatabase", "The data we have", spec.data], ["FaBullseye", "What a good answer looks like", spec.decision]];
    const cw = 5.8, chh = (6.7 - top - 0.25) / 2;
    for (let i = 0; i < 4; i++) {
      const x = MX + (i % 2) * 6.1, y = top + Math.floor(i / 2) * (chh + 0.25);
      card(s, x, y, cw, chh);
      await iconCircle(s, blocks[i][0], x + 0.25, y + 0.22, 0.5, i === 1 ? C.gold : C.teal);
      T(s, blocks[i][1], { x: x + 0.9, y: y + 0.22, w: cw - 1.1, h: 0.5, fontFace: HEAD, fontSize: 15.5, bold: true, color: C.navy, valign: "middle" });
      T(s, rich(blocks[i][2], { fontSize: 13, color: C.ink }), { x: x + 0.3, y: y + 0.85, w: cw - 0.6, h: chh - 1.0 });
    }
  }

  async lab(spec) {
    const s = this.frame({ kicker: spec.kicker || "HANDS-ON LAB", title: spec.title, sub: spec.sub, study: spec.study, illus: spec.illus, notes: spec.notes });
    const top = spec.sub ? 2.05 : 1.85;
    // left: files panel
    s.addShape("roundRect", { x: MX, y: top, w: 4.1, h: 6.7 - top, rectRadius: 0.08, fill: { color: C.navy }, line: { color: C.navy } });
    T(s, "YOU WILL NEED", { x: MX + 0.3, y: top + 0.25, w: 3.5, h: 0.3, fontSize: 11, bold: true, color: C.gold, charSpacing: 3 });
    const files = [["FaTable", "Data", spec.data], ["FaRProject", "R script", spec.r], ["FaPython", "Python script", spec.py]];
    for (let i = 0; i < files.length; i++) {
      const y = top + 0.75 + i * 1.15;
      s.addImage({ data: await icon(files[i][0], C.gold), x: MX + 0.3, y: y + 0.05, w: 0.4, h: 0.4 });
      T(s, files[i][1], { x: MX + 0.85, y, w: 3, h: 0.3, fontSize: 12, bold: true, color: C.white });
      T(s, files[i][2], { x: MX + 0.85, y: y + 0.32, w: 3.1, h: 0.7, fontFace: MONO, fontSize: 10.5, color: C.pale2 });
    }
    if (spec.time) T(s, `⏱  ${spec.time}`, { x: MX + 0.3, y: 6.15, w: 3.5, h: 0.35, fontSize: 13, bold: true, color: C.white });
    // right: steps
    const sx = MX + 4.4, sw = 12.6 - sx, n = spec.steps.length, each = (6.7 - top - (spec.deliver ? 0.85 : 0)) / n;
    for (let i = 0; i < n; i++) {
      const y = top + i * each;
      s.addShape("ellipse", { x: sx, y: y + 0.05, w: 0.42, h: 0.42, fill: { color: C.teal }, line: { color: C.teal } });
      T(s, String(i + 1), { x: sx, y: y + 0.05, w: 0.42, h: 0.42, fontSize: 13, bold: true, color: C.white, align: "center", valign: "middle" });
      T(s, rich(spec.steps[i], { fontSize: 13.5, color: C.ink }), { x: sx + 0.6, y, w: sw - 0.6, h: each - 0.05 });
    }
    if (spec.deliver) {
      s.addShape("roundRect", { x: sx, y: 5.9, w: sw, h: 0.8, rectRadius: 0.06, fill: { color: C.card }, line: { color: C.gold, width: 1 } });
      T(s, rich("**Deliverable:** " + spec.deliver, { fontSize: 13, color: C.navy }), { x: sx + 0.25, y: 5.9, w: sw - 0.5, h: 0.8, valign: "middle" });
    }
  }

  async glossary(spec) {
    const s = this.frame({ kicker: "WORDS TO OWN", title: spec.title || "Today's Vocabulary in Plain English", study: spec.study, illus: spec.illus, notes: spec.notes });
    const t = spec.terms, half = Math.ceil(t.length / 2), top = 1.85, rh = (6.7 - top) / half;
    for (let i = 0; i < t.length; i++) {
      const col = i < half ? 0 : 1, r = i % half, x = MX + col * 6.05, y = top + r * rh;
      s.addShape("roundRect", { x, y: y + 0.04, w: 5.85, h: rh - 0.1, rectRadius: 0.05, fill: { color: C.card }, line: { color: C.border, width: 0.75 } });
      T(s, t[i].term, { x: x + 0.2, y: y + 0.04, w: 1.75, h: rh - 0.1, fontFace: HEAD, fontSize: 13, bold: true, color: C.navy, valign: "middle" });
      T(s, rich(t[i].def, { fontSize: 11.5, color: C.ink }), { x: x + 2.0, y: y + 0.04, w: 3.7, h: rh - 0.1, valign: "middle" });
    }
  }

  async recap(spec) {
    const s = this.dark(spec);
    T(s, "KEY TAKEAWAYS", { x: 0.9, y: 0.6, w: 8, h: 0.3, fontSize: 12, bold: true, color: C.gold, charSpacing: 4 });
    T(s, spec.title || `Session ${this.m.num} in ${spec.items.length} Ideas`, { x: 0.9, y: 0.9, w: 9, h: 0.7, fontFace: HEAD, fontSize: 30, bold: true, color: C.white });
    const n = spec.items.length, top = 1.85, rh = Math.min(0.9, 3.55 / n);
    for (let i = 0; i < n; i++) {
      const y = top + i * rh;
      T(s, String(i + 1).padStart(2, "0"), { x: 0.9, y, w: 0.8, h: rh, fontFace: HEAD, fontSize: 22, bold: true, color: C.gold, valign: "middle" });
      T(s, rich(spec.items[i], { fontSize: 15, color: C.white }), { x: 1.75, y, w: 8.0, h: rh, valign: "middle" });
    }
    const by = top + n * rh + 0.2;
    if (spec.prework) {
      s.addShape("roundRect", { x: 0.9, y: Math.max(by, 5.55), w: 8.85, h: 1.15, rectRadius: 0.08, fill: { color: C.circ2 }, line: { color: C.teal2, width: 1 } });
      T(s, rich(`**${spec.preworkLabel || "Before next session"}:** ${spec.prework}`, { fontSize: 13, color: C.pale2 }), { x: 1.15, y: Math.max(by, 5.55), w: 8.4, h: 1.15, valign: "middle" });
    }
    s.addImage({ path: path.join(LOGO, this.m.part ? `eegb_hex_p${this.m.part}.png` : "eegb_hex.png"), x: 10.2, y: 2.3, w: 2.5, h: 2.5 });
    if (spec.next) T(s, `NEXT  ›  ${spec.next}`, { x: 9.9, y: 5.0, w: 3.1, h: 0.9, fontSize: 12.5, bold: true, color: C.gold, align: "center", valign: "middle" });
  }

  async roadmap(spec = {}) {
    const s = this.frame({ kicker: "WHERE WE ARE", title: "Course Roadmap — 16 Sessions, 4 Parts", sub: "Pre-module and intra-module online sessions, sixteen on-campus sessions, and a closed-book final exam.", notes: spec.notes, study: spec.study });
    const parts = [
      ["Part I", "Sessions 1–5", "Micro & markets", "Data literacy, demand and elasticity, forecasting, market structure and platforms, market failures"],
      ["Part II", "Sessions 6–10", "Macro, policy & risk", "AD–AS and inflation, national accounts, monetary policy, fiscal policy and debt, financial stability"],
      ["Part III", "Sessions 11–12", "Open economy", "Exchange rates, capital flows and the trilemma; trade, supply chains, industrial policy and AfCFTA"],
      ["Part IV", "Sessions 13–16", "Strategic frontiers", "Climate economics, country risk and scenarios, hedging and resilience, capstone memos"]];
    const cur = this.m.num <= 5 ? 0 : this.m.num <= 10 ? 1 : this.m.num <= 12 ? 2 : 3;
    for (let i = 0; i < 4; i++) {
      const x = MX + i * 3.05, on = i === cur;
      s.addShape("roundRect", { x, y: 2.35, w: 2.85, h: 4.2, rectRadius: 0.08, fill: { color: on ? C.teal : C.card }, line: { color: on ? C.teal : C.border, width: 0.75 } });
      if (on) { s.addShape("roundRect", { x: x + 0.55, y: 2.17, w: 1.75, h: 0.36, rectRadius: 0.18, fill: { color: C.gold }, line: { color: C.gold } });
        T(s, "YOU ARE HERE", { x: x + 0.55, y: 2.17, w: 1.75, h: 0.36, fontSize: 10, bold: true, color: C.white, align: "center", valign: "middle", charSpacing: 2 }); }
      s.addImage({ path: path.join(LOGO, `eegb_hex_p${i + 1}_256.png`), x: x + 2.0, y: 2.62, w: 0.65, h: 0.65 });
      T(s, parts[i][0], { x: x + 0.25, y: 2.7, w: 1.8, h: 0.45, fontFace: HEAD, fontSize: 19, bold: true, color: on ? C.white : C.navy });
      T(s, parts[i][1], { x: x + 0.25, y: 3.15, w: 2.4, h: 0.3, fontSize: 12.5, bold: true, color: on ? "FFE3A8" : C.gold });
      T(s, parts[i][2], { x: x + 0.25, y: 3.45, w: 2.4, h: 0.3, fontSize: 11.5, color: on ? C.pale2 : C.muted });
      T(s, parts[i][3], { x: x + 0.25, y: 4.0, w: 2.4, h: 2.4, fontSize: 12, color: on ? C.white : C.ink });
    }
  }

  // ---------- richer tutorial slide types ----------
  async lead(spec) {
    // a claim on the left, the reasoning (numbered) on the right
    const s = this.frame(spec);
    const top = spec.sub ? 2.05 : 1.85, bot = spec.note ? 5.95 : 6.75;
    const lw = spec.leadW || 4.3;
    s.addShape("roundRect", { x: MX, y: top, w: lw, h: bot - top, rectRadius: 0.08, fill: { color: C.navy }, line: { color: C.navy } });
    s.addShape("rect", { x: MX, y: top + 0.35, w: 0.08, h: 0.9, fill: { color: C.cyan }, line: { color: C.cyan } });
    if (spec.leadLabel) T(s, spec.leadLabel.toUpperCase(), { x: MX + 0.35, y: top + 0.3, w: lw - 0.6, h: 0.3, fontSize: 10.5, bold: true, color: C.gold, charSpacing: 3 });
    T(s, rich(spec.lead, { fontSize: spec.leadSize || 19, color: C.white }), { x: MX + 0.35, y: top + (spec.leadLabel ? 0.7 : 0.35), w: lw - 0.65, h: bot - top - 1.0, fontFace: HEAD, valign: "top" });
    if (spec.leadFoot) T(s, rich(spec.leadFoot, { fontSize: 11.5, color: C.pale2, italic: true }), { x: MX + 0.35, y: bot - 0.95, w: lw - 0.65, h: 0.8, valign: "bottom" });
    const rx = MX + lw + 0.35, rw = 12.6 - rx, pts = spec.points, n = pts.length, each = (bot - top) / n;
    for (let i = 0; i < n; i++) {
      const y = top + i * each, p = pts[i];
      s.addShape("ellipse", { x: rx, y: y + 0.06, w: 0.42, h: 0.42, fill: { color: p.accent ? C.gold : C.teal }, line: { color: p.accent ? C.gold : C.teal } });
      T(s, String(i + 1), { x: rx, y: y + 0.06, w: 0.42, h: 0.42, fontSize: 12.5, bold: true, color: C.white, align: "center", valign: "middle" });
      T(s, p.h, { x: rx + 0.6, y: y, w: rw - 0.6, h: 0.5, fontFace: HEAD, fontSize: spec.hSize || 15.5, bold: true, color: C.navy, valign: "middle" });
      T(s, rich(p.t, { fontSize: spec.textSize || 12.5, color: C.ink }), { x: rx + 0.6, y: y + 0.5, w: rw - 0.6, h: each - 0.55 });
      if (i < n - 1) s.addShape("line", { x: rx + 0.6, y: y + each - 0.04, w: rw - 0.6, h: 0, line: { color: C.border, width: 0.75 } });
    }
    if (spec.note) this.noteBar(s, spec.note, 6.12);
  }

  async quote(spec) {
    const s = this.dark(spec, "campus_darker.jpg");
    T(s, (spec.kicker || "FROM THE READINGS").toUpperCase(), { x: 0.9, y: 0.7, w: 9, h: 0.3, fontSize: 11.5, bold: true, color: C.gold, charSpacing: 3 });
    T(s, "\u201C", { x: 0.75, y: 1.15, w: 1, h: 1.2, fontFace: HEAD, fontSize: 96, bold: true, color: C.cyan });
    T(s, spec.quote, { x: 1.6, y: 1.5, w: 10.2, h: 1.6, fontFace: HEAD, fontSize: spec.quoteSize || 28, italic: true, color: C.white, valign: "middle" });
    T(s, "\u2014 " + spec.who, { x: 1.6, y: 3.15, w: 10.2, h: 0.4, fontSize: 14, color: C.pale2 });
    if (spec.points) {
      const n = spec.points.length, cw = (11.4 - 0.3 * (n - 1)) / n;
      spec.points.forEach((p, i) => {
        const x = 0.9 + i * (cw + 0.3);
        s.addShape("roundRect", { x, y: 4.05, w: cw, h: 2.75, rectRadius: 0.08, fill: { color: C.deep, transparency: 15 }, line: { color: C.teal2, width: 0.75 } });
        T(s, p.h, { x: x + 0.25, y: 4.2, w: cw - 0.5, h: 0.5, fontFace: HEAD, fontSize: 15.5, bold: true, color: C.gold, valign: "middle" });
        T(s, rich(p.t, { fontSize: 12.5, color: C.white }), { x: x + 0.25, y: 4.75, w: cw - 0.5, h: 1.95 });
      });
    }
  }

  async timeline(spec) {
    const s = this.frame(spec);
    const ev = spec.events, n = ev.length, top = spec.sub ? 2.05 : 1.85;
    const x0 = MX + 0.2, x1 = 12.4, ly = top + 0.95, step = (x1 - x0) / n;
    s.addShape("line", { x: x0, y: ly, w: x1 - x0, h: 0, line: { color: C.navy, width: 2.5 } });
    for (let i = 0; i < n; i++) {
      const e = ev[i], cx = x0 + step * i + step / 2, col = e.accent ? C.gold : (e.color || C.teal);
      T(s, e.date, { x: cx - step / 2, y: top, w: step, h: 0.55, fontFace: HEAD, fontSize: 14, bold: true, color: col, align: "center", valign: "bottom" });
      s.addShape("ellipse", { x: cx - 0.15, y: ly - 0.15, w: 0.3, h: 0.3, fill: { color: col }, line: { color: C.white, width: 2 } });
      card(s, cx - step / 2 + 0.05, ly + 0.35, step - 0.1, (spec.note ? 5.95 : 6.75) - ly - 0.4, e.accent ? "FFF6E6" : C.card);
      T(s, e.label, { x: cx - step / 2 + 0.15, y: ly + 0.45, w: step - 0.3, h: 0.75, fontSize: 12.5, bold: true, color: C.navy, valign: "top" });
      T(s, rich(e.desc, { fontSize: spec.descSize || 11, color: C.ink }), { x: cx - step / 2 + 0.15, y: ly + 1.2, w: step - 0.3, h: (spec.note ? 5.95 : 6.75) - ly - 1.35 });
    }
    if (spec.note) this.noteBar(s, spec.note, 6.12);
  }

  async flow(spec) {
    // Mankiw's circular-flow diagram, drawn natively
    const s = this.frame(spec);
    const box = (x, y, w, h, label, fill, fc = C.white, sz = 15) => {
      s.addShape("roundRect", { x, y, w, h, rectRadius: 0.1, fill: { color: fill }, line: { color: fill } });
      T(s, label, { x, y, w, h, fontFace: HEAD, fontSize: sz, bold: true, color: fc, align: "center", valign: "middle" });
    };
    const ell = (x, y, w, h, label) => {
      s.addShape("ellipse", { x, y, w, h, fill: { color: "FFF1D6" }, line: { color: C.gold, width: 1.5 } });
      T(s, label, { x, y, w, h, fontSize: 13, bold: true, color: C.navy, align: "center", valign: "middle" });
    };
    const arr = (x, y, w, h, color, flipH, flipV) => s.addShape("line", { x, y, w, h, flipH: !!flipH, flipV: !!flipV, line: { color, width: 2.25, endArrowType: "triangle" } });
    const lab = (x, y, w, t, color, al = "center") => T(s, t, { x, y, w, h: 0.3, fontSize: 10.5, bold: true, color, align: al });
    const L = 0.9, R = 6.6, top = 2.1, mid = 4.15, bot = 6.0;
    box(L, mid - 0.4, 1.6, 0.8, "FIRMS", C.teal);
    box(R, mid - 0.4, 1.6, 0.8, "HOUSEHOLDS", C.navy, C.white, 13.5);
    ell(3.2, top - 0.25, 2.6, 1.0, "Markets for\ngoods & services");
    ell(3.2, bot - 0.75, 2.6, 1.0, "Markets for\nfactors of production");
    const blue = C.teal2, gold = C.gold;
    // money flows (outer, gold): households spend -> goods market -> firms revenue; firms pay -> factor market -> households income
    arr(R + 0.8, top + 0.25, 0, mid - 0.4 - top - 0.25, gold, false, true);   // up from households (spending)
    arr(5.8, top + 0.25, R + 0.8 - 5.8, 0, gold, true, false);                 // left into goods market
    arr(L + 0.8, top + 0.25, 3.2 - L - 0.8, 0, gold, true, false);            // goods market -> firms (left)
    arr(L + 0.8, top + 0.25, 0, mid - 0.4 - top - 0.25, gold);                // down into firms
    arr(L + 0.8, mid + 0.4, 0, bot - mid - 0.4 - 0.25, gold);                 // firms down (wages)
    arr(L + 0.8, bot - 0.25, 3.2 - L - 0.8, 0, gold);                         // -> factor market
    arr(5.8, bot - 0.25, R + 0.8 - 5.8, 0, gold);                             // -> households
    arr(R + 0.8, mid + 0.4, 0, bot - mid - 0.4 - 0.25, gold, false, true);    // up into households
    // real flows (inner, blue): diagonals linking boxes and markets
    const dg = (x1, y1, x2, y2) => s.addShape("line", { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipH: x2 < x1, flipV: y2 < y1, line: { color: blue, width: 2.25, endArrowType: "triangle" } });
    dg(2.3, mid - 0.4, 3.55, top + 0.65); dg(5.45, top + 0.65, 6.8, mid - 0.4);
    dg(6.8, mid + 0.4, 5.45, bot - 0.65); dg(3.55, bot - 0.65, 2.3, mid + 0.4);
    lab(R - 0.4, top - 0.15, 2.6, "Spending (= GDP)", gold);
    lab(L - 0.2, top - 0.15, 2.4, "Revenue (= GDP)", gold);
    lab(L - 0.2, bot - 0.15, 2.4, "Wages, rent, profit", gold);
    lab(R - 0.4, bot - 0.15, 2.6, "Income (= GDP)", gold);
    lab(3.0, mid - 0.75, 1.9, "Goods & services sold", blue, "left");
    lab(4.75, mid - 0.75, 1.75, "G & S bought", blue, "right");
    lab(4.75, mid + 0.45, 1.75, "Labour, land, capital", blue, "right");
    lab(3.0, mid + 0.45, 1.9, "Factors hired", blue, "left");
    T(s, "Gold = flows of naira    ·    Blue = flows of goods, services and factors", { x: 0.9, y: 6.4, w: 7.2, h: 0.3, fontSize: 10.5, italic: true, color: C.muted, align: "center" });
    const px = 8.75, pw = 3.85;
    card(s, px, 1.85, pw, 4.85);
    T(s, spec.panelTitle || "HOW TO READ IT", { x: px + 0.3, y: 2.05, w: pw - 0.6, h: 0.3, fontSize: 11.5, bold: true, color: C.teal2, charSpacing: 3 });
    T(s, bullets(spec.points, { fontSize: 12.5, space: 8 }), { x: px + 0.25, y: 2.45, w: pw - 0.5, h: 4.15 });
  }

  async exercise(spec) {
    const s = this.frame(spec);
    const top = spec.sub ? 2.05 : 1.85, cols = spec.cols || ["Positive", "Normative"];
    const head = [{ text: "#", options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center" } },
      { text: spec.stmtHead || "Statement", options: { bold: true, color: C.white, fill: { color: C.navy } } },
      ...cols.map(c => ({ text: c, options: { bold: true, color: C.white, fill: { color: C.navy }, align: "center" } }))];
    const rows = spec.items.map((it, i) => [
      { text: String(i + 1), options: { bold: true, color: C.navy, align: "center", fill: { color: i % 2 ? "FFFFFF" : C.card } } },
      { text: it, options: { color: C.ink, fill: { color: i % 2 ? "FFFFFF" : C.card } } },
      ...cols.map(() => ({ text: "\u2610", options: { color: C.muted, align: "center", fontSize: 18, fill: { color: i % 2 ? "FFFFFF" : C.card } } }))]);
    const cw = 1.5 * cols.length;
    const avail = (spec.note ? 5.95 : 6.7) - top;
    s.addTable([head, ...rows], { x: MX, y: top, w: 11.9, colW: [0.55, 11.9 - 0.55 - cw, ...cols.map(() => 1.5)], fontFace: BODY, fontSize: spec.fontSize || 13.5,
      rowH: Math.min(0.62, avail / (rows.length + 1)), border: { type: "solid", color: C.border, pt: 0.75 }, valign: "middle", margin: 0.08 });
    if (spec.note) this.noteBar(s, spec.note, 6.12);
  }

  async chart(spec) {
    const s = this.frame(spec);
    const top = spec.sub ? 2.0 : 1.8, cw = spec.points ? 7.9 : 11.9;
    const types = { bar: this.p.charts.BAR, line: this.p.charts.LINE };
    s.addChart(types[spec.chartType || "bar"], spec.data, Object.assign({
      x: MX, y: top, w: cw, h: 6.55 - top, barDir: spec.barDir || "bar", chartColors: spec.colors || [C.teal, C.gold, C.navy],
      showValue: spec.showValue !== false, dataLabelFormatCode: spec.fmt || '0.0"%"', dataLabelFontSize: 12, dataLabelColor: C.ink,
      catAxisLabelFontSize: 12, catAxisLabelColor: C.ink, valAxisHidden: !!spec.hideVal, valGridLine: { style: "none" },
      valAxisLabelFontSize: 10, catAxisLabelFontFace: BODY, showLegend: (spec.data.length > 1), legendPos: "b", legendFontSize: 11,
      barGapWidthPct: 60, showTitle: !!spec.chartTitle, title: spec.chartTitle, titleFontSize: 13, titleColor: C.navy }, spec.opts || {}));
    if (spec.source) T(s, spec.source, { x: MX, y: 6.5, w: cw, h: 0.3, fontSize: 9, italic: true, color: C.muted, align: "center" });
    if (spec.points) {
      const px = 8.85, pw = 3.75;
      card(s, px, top, pw, 6.7 - top);
      T(s, spec.panelTitle || "WHAT TO SEE", { x: px + 0.3, y: top + 0.25, w: pw - 0.6, h: 0.3, fontSize: 11.5, bold: true, color: C.teal2, charSpacing: 3 });
      T(s, bullets(spec.points, { fontSize: spec.pointSize || 12.5, space: 8 }), { x: px + 0.25, y: top + 0.7, w: pw - 0.5, h: 6.7 - top - 0.9 });
    }
  }

  async readings(spec) {
    const s = this.frame({ kicker: "GO DEEPER", title: spec.title || "Readings Behind This Session", study: spec.study, illus: spec.illus, notes: spec.notes });
    const it = spec.items, n = it.length, top = 1.85, rh = (6.75 - top) / n;
    for (let i = 0; i < n; i++) {
      const y = top + i * rh, r = it[i];
      s.addShape("rect", { x: MX, y: y + 0.06, w: 0.1, h: rh - 0.16, fill: { color: r.core ? C.gold : C.teal }, line: { color: r.core ? C.gold : C.teal } });
      T(s, r.ref, { x: MX + 0.3, y: y + 0.02, w: 4.4, h: rh - 0.08, fontFace: HEAD, fontSize: 13, bold: true, color: C.navy, valign: "middle" });
      T(s, rich(r.why, { fontSize: 12, color: C.ink }), { x: MX + 4.85, y: y + 0.02, w: 7.05, h: rh - 0.08, valign: "middle" });
      if (i < n - 1) s.addShape("line", { x: MX + 0.3, y: y + rh - 0.02, w: 11.6, h: 0, line: { color: C.border, width: 0.75 } });
    }
  }

  async plan(spec) {
    // agenda strip on top, three objective cards below
    const s = this.frame({ kicker: spec.kicker || "TODAY", title: spec.title, sub: spec.sub, notes: spec.notes });
    const total = spec.blocks.reduce((a, b) => a + b.min, 0); let x = MX; const tw = 11.9;
    const cols = [C.navy, C.teal, C.teal2, C.gold];
    spec.blocks.forEach((b, i) => {
      const w = tw * b.min / total;
      s.addShape("rect", { x, y: 1.95, w: w - 0.04, h: 0.75, fill: { color: cols[i % cols.length] }, line: { color: C.white } });
      T(s, [{ text: `${b.min} min`, options: { fontSize: 10, bold: true, color: "FFE3A8", breakLine: true } }, { text: b.label, options: { fontSize: 12, bold: true, color: C.white } }],
        { x: x + 0.12, y: 1.95, w: w - 0.25, h: 0.75, valign: "middle" });
      x += w;
    });
    T(s, "BY THE END OF TODAY YOU WILL BE ABLE TO", { x: MX, y: 2.98, w: 9, h: 0.3, fontSize: 11, bold: true, color: C.teal2, charSpacing: 3 });
    const n = spec.items.length, gap = 0.3, cw = (11.9 - gap * (n - 1)) / n;
    for (let i = 0; i < n; i++) {
      const it = spec.items[i], cx = MX + i * (cw + gap);
      card(s, cx, 3.38, cw, 3.3);
      await iconCircle(s, it.icon || "FaBullseye", cx + 0.3, 3.6, 0.6, C.teal);
      T(s, it.title, { x: cx + 1.05, y: 3.58, w: cw - 1.25, h: 0.65, fontFace: HEAD, fontSize: 16, bold: true, color: C.navy, valign: "middle" });
      T(s, rich(it.body, { fontSize: 13, color: C.ink }), { x: cx + 0.3, y: 4.4, w: cw - 0.6, h: 2.15 });
    }
  }

  async pnlmap(spec) {
    const s = this.frame(spec);
    const top = spec.sub ? 2.0 : 1.8;
    const heat = { 3: "F6C9A9", 2: "FBE3CF", 1: "F3F6F9", 0: "FFFFFF" };
    const head = [{ text: spec.corner || "When this moves…", options: { bold: true, color: C.gold, fill: { color: C.navy }, fontSize: 11.5, italic: true } },
      ...spec.cols.map(c => ({ text: c, options: { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 12, align: "center" } }))];
    const rows = spec.rows.map(r => [
      { text: r.driver, options: { bold: true, color: C.white, fill: { color: C.teal }, fontSize: 12.5, fontFace: HEAD } },
      ...r.cells.map(([lvl, t]) => ({ text: t, options: { fontSize: spec.cellSize || 10.5, color: C.ink, fill: { color: heat[lvl] }, align: "left" } }))]);
    const avail = (spec.note ? 5.85 : 6.7) - top;
    s.addTable([head, ...rows], { x: MX, y: top, w: 11.9, colW: [2.15, ...spec.cols.map(() => (11.9 - 2.15) / spec.cols.length)], rowH: avail / (rows.length + 1),
      border: { type: "solid", color: C.white, pt: 1.5 }, valign: "middle", margin: 0.06, fontFace: BODY });
    const ly = (spec.note ? 5.85 : 6.7) + 0.02;
    [["Large effect", heat[3]], ["Moderate", heat[2]], ["Small", heat[1]]].forEach(([l, c], i) => {
      s.addShape("rect", { x: MX + 7.4 + i * 1.55, y: ly + 0.06, w: 0.22, h: 0.16, fill: { color: c }, line: { color: C.border } });
      T(s, l, { x: MX + 7.68 + i * 1.55, y: ly, w: 1.3, h: 0.28, fontSize: 9.5, color: C.muted, valign: "middle" });
    });
    if (spec.note) this.noteBar(s, spec.note, 6.12, 0.55);
  }

  async run(slides) {
    await this.title();
    for (const sp of slides) {
      const fn = { caseSlide: "caseSlide", case: "caseSlide" }[sp.type] || sp.type;
      if (!this[fn]) throw new Error("Unknown slide type: " + sp.type);
      await this[fn](sp);
    }
  }
  async save(file) {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    await this.p.writeFile({ fileName: file });
    console.log("wrote", file, this.n, "slides");
  }
}
module.exports = { Deck, C, ROOT };
