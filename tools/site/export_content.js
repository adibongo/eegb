// export_content.js — dumps teaching content from each deck (objectives, figures, lab, recap, glossary)
// into tools/site/content.json so the website and the slides never drift apart.
const path = require("path");
const fs = require("fs");
const sessions = require("../sessions.json");
const ROOT = path.resolve(__dirname, "..", "..");
const strip = (t) => (t || "").replace(/\*\*/g, "").replace(/(^|\W)_(\S[^_]*?)_(?=\W|$)/g, "$1$2");
const out = {};
for (const s of sessions) {
  const f = path.join(__dirname, "..", "deck", "content", `${s.slug}.js`);
  if (!fs.existsSync(f)) continue;
  const fig = (id) => `sessions/${s.slug}/figures/python/${s.slug}_${id}.png`;
  const slides = require(f)({ s, fig, script: () => "" });
  const pick = (t) => slides.filter((x) => x.type === t);
  const o = { objectives: [], figures: [], recap: [], glossary: [], lab: null, hook: null, concepts: [], checks: [] };
  const obj = pick("objectives")[0]; if (obj) o.objectives = obj.items.map((i) => ({ title: i.title, body: strip(i.body) }));
  const hook = pick("hook")[0]; if (hook) o.hook = { title: hook.title, quote: strip(hook.quote) };
  for (const x of pick("figure")) o.figures.push({ img: path.relative(ROOT, x.img).replace(/\\/g, "/"), id: x.fig, title: x.title, kicker: x.kicker, points: (x.points || []).map(strip) });
  for (const x of pick("concept")) o.concepts.push({ title: x.title, plain: strip(x.plain), formula: x.formula ? x.formula.replace(/\n/g, " ") : null, example: strip(x.example), why: strip(x.why) });
  for (const x of pick("check")) o.checks.push({ q: x.q, options: x.options, answer: x.answer, explain: x.explain });
  const lab = pick("lab")[0]; if (lab) o.lab = { title: lab.title, time: lab.time, data: lab.data, r: lab.r, py: lab.py, steps: lab.steps.map(strip), deliver: strip(lab.deliver) };
  const rc = pick("recap")[0]; if (rc) o.recap = { items: rc.items.map(strip), prework: strip(rc.prework), next: rc.next };
  const g = pick("glossary")[0]; if (g) o.glossary = g.terms;
  const cs = pick("caseSlide")[0]; if (cs) o.case = { title: cs.title, context: strip(cs.context), question: strip(cs.question), data: strip(cs.data), decision: strip(cs.decision) };
  out[s.slug] = o;
}
fs.writeFileSync(path.join(__dirname, "content.json"), JSON.stringify(out, null, 1));
console.log("exported", Object.keys(out).length, "sessions");
