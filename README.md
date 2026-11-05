<img src="assets/logos/eegb_hex.png" align="right" width="170" alt="EEGB hex logo"/>

# Economic Environment of Global Business · MEMBA 14 · Lagos Business School

**How micro- and macroeconomic forces shape firm strategy, risk and performance — in Nigeria and the world.**

Course website: **https://markanalytics.online/eegb/**

This repository holds everything for the 16-session EEGB course: teaching slide decks (Lagos Business School format), stylised Nigerian macro datasets, and **R and Python scripts that regenerate every chart** in the decks. It is written for MBA executives who are new to economics. It follows the structure of the [Data Analytics I](https://markanalytics.online/da1-mmba11/) course site.

Facilitators: Prof. Bongo Adi (badi@lbs.edu.ng), Kelechi Nnamdi, Elvis Ozegbe, Sumendra Dash (guest).

## Quick start

1. Install R, RStudio and (optionally) Python. See the [Setup page](https://markanalytics.online/eegb/setup.html).
2. Download this repo (**Code → Download ZIP**) and open `eegb.Rproj` in RStudio.
3. Install packages: `source("install_packages.R")` (R) and/or `pip install -r requirements.txt` (Python).
4. Run any script from the project root, e.g. `source("sessions/s11/R/s11_figures.R")` or `python sessions/s11/python/s11_figures.py`.

## Sessions

Plus a [pre-module](https://markanalytics.online/eegb/pre-module.html) and [intra-module online sessions](https://markanalytics.online/eegb/intra-module.html).

| # | Session | Part | Facilitator |
|---|---|---|---|
| 1 | [Course Overview & Data Literacy for Managers](https://markanalytics.online/eegb/sessions/s01/) | Part I | Bongo Adi |
| 2 | [Demand, Supply & Elasticity with Behavioural Insights](https://markanalytics.online/eegb/sessions/s02/) | Part I | Bongo Adi |
| 3 | [Demand Forecasting & Market Sizing](https://markanalytics.online/eegb/sessions/s03/) | Part I | Kelechi Nnamdi |
| 4 | [Market Structure, Platforms & Competition Policy](https://markanalytics.online/eegb/sessions/s04/) | Part I | Kelechi Nnamdi |
| 5 | [Market Failures & Government Intervention](https://markanalytics.online/eegb/sessions/s05/) | Part I | Kelechi Nnamdi |
| 6 | [AD-AS in a Shock-Prone World](https://markanalytics.online/eegb/sessions/s06/) | Part II | Bongo Adi |
| 7 | [National Accounts, Productivity & Welfare](https://markanalytics.online/eegb/sessions/s07/) | Part II | Bongo Adi |
| 8 | [Monetary Policy from QE to QT](https://markanalytics.online/eegb/sessions/s08/) | Part II | Elvis Ozegbe |
| 9 | [Fiscal Policy, Debt & Sovereign Risk](https://markanalytics.online/eegb/sessions/s09/) | Part II | Elvis Ozegbe |
| 10 | [Financial Stability & Corporate Finance Conditions](https://markanalytics.online/eegb/sessions/s10/) | Part II | Elvis Ozegbe |
| 11 | [Exchange Rates, Capital Flows & the Impossible Trinity](https://markanalytics.online/eegb/sessions/s11/) | Part III | Elvis Ozegbe |
| 12 | [Trade, Supply Chains & Industrial Policy](https://markanalytics.online/eegb/sessions/s12/) | Part III | Bongo Adi & Kelechi Nnamdi |
| 13 | [Climate & Energy-Transition Economics](https://markanalytics.online/eegb/sessions/s13/) | Part IV | Bongo Adi & Kelechi Nnamdi |
| 14 | [Country Risk & Scenario Planning](https://markanalytics.online/eegb/sessions/s14/) | Part IV | Sumendra Dash |
| 15 | [Corporate Macro Strategy: Hedging & Resilience](https://markanalytics.online/eegb/sessions/s15/) | Part IV | Sumendra Dash |
| 16 | [Capstone & Integrative Review](https://markanalytics.online/eegb/sessions/s16/) | Part IV | Bongo Adi, Kelechi Nnamdi & Elvis Ozegbe |

Each `sessions/sNN/` folder contains:

- `slides/`: the teaching deck (`.pptx` and `.pdf`)
- `R/` and `python/`: `sNN_figures` (regenerates every chart, with IDs matching the slides, e.g. `S11-F06`) and `sNN_lab` (a commented, beginner-friendly lab with a *Your turn* section). Session 16 has a capstone starter instead of a lab.
- `figures/python/` and `figures/r/`: the charts those scripts produce

## Rebuilding everything

```bash
python tools/make_data.py                 # regenerate all datasets (fixed seeds)
python tools/make_hex.py                  # redraw the hex logos (needs Node + sharp)
python run_all.py                         # every Python chart, lab and starter
Rscript run_all.R                         # every R chart, lab and starter
cd tools/deck && npm install && node build.js all && cd ../..    # rebuild all 16 slide decks
node tools/site/export_content.js && python tools/site/build_site.py && quarto render   # rebuild the website into docs/
```

To make PDFs of the decks: open each `.pptx` in PowerPoint and *Save as PDF*, or run `soffice --headless --convert-to pdf sessions/*/slides/*.pptx`.

## Deploying the website

`quarto render` writes the static site to `docs/` (not committed, to keep the repo small). Upload the **contents** of `docs/` to `public_html/eegb/` on the markanalytics.online host (Hostinger File Manager or FTP). The site will then be live at https://markanalytics.online/eegb/.

## Notes

- All datasets are **stylised teaching data**: they follow the broad path of the Nigerian and global economy but are generated, not official. Use `tools/fetch_official_data.py` (or `.R`) for real World Bank and FRED series.
- Python figures are rendered and committed. R figures appear on the site once you run `Rscript run_all.R` and rebuild.
- Licence: course materials CC BY 4.0; code MIT. See `LICENSE`.

Prof. Bongo Adi · Lagos Business School
