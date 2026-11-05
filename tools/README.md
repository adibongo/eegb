# tools/

| File | What it does |
|---|---|
| `make_data.py` | Generates every dataset in `data/` with fixed seeds (`python tools/make_data.py`). |
| `make_hex.py`, `svg2png.js` | Draw the EEGB hex logos (main + one per part) in `assets/logos/`. |
| `fetch_official_data.py` / `.R` | Download real World Bank and FRED series into `data/official/`. |
| `sessions.json` | Metadata for all 16 sessions (titles, parts, readings, case, data, facilitator). |
| `deck/` | Slide engine (`lib.js`, Lagos Business School template) and per-session content (`content/sNN.js`). Build with `cd tools/deck && npm install && node build.js all`. |
| `site/` | `export_content.js` pulls objectives, concepts, figures, labs, checks and glossary from the deck content; `build_site.py` writes the session pages, home and datasets pages. Then run `quarto render`. |
