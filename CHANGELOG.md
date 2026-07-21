# Changelog

All notable changes to this project are documented here. The format loosely
follows [Keep a Changelog](https://keepachangelog.com/).

## [0.2.0] — HTML visualizations converted to pure Python

### Changed
- **The 3D figures are now pure matplotlib instead of Plotly.** They previously
  rendered as an inlined `plotly.js` runtime (JavaScript in the page); they are
  re-implemented with matplotlib's `mplot3d`, so no HTML/JS rendering layer is
  involved. Every `fig3d_*` builder now returns a `matplotlib.figure.Figure`,
  matching the 2D `figures.py` contract.
- **`scripts/make_3d.py` now writes PNG + GIF instead of standalone HTML.** Each
  3D chart is rendered from a chosen camera angle (PNG) and as a 360-degree
  rotation animation (GIF, via `figures3d.spin`), to recover the depth the old
  drag-to-rotate interaction gave. `--no-gif` skips the animations.
- `requirements.txt`: removed `plotly`, added `pillow` (matplotlib's GIF writer).
- The report's "Explore it in three dimensions" section describes static renders
  with optional rotation animations rather than live, draggable plots.

### Added
- **Packaging:** `pyproject.toml` (installable `mitski-analysis` package, ruff +
  pytest config, console scripts `mitski-clean/build/figures/3d`), a `Makefile`,
  and a GitHub Actions CI workflow (lint + tests + a headless pipeline build on
  Python 3.10–3.12).
- **New analyses** in `text.py`: `mtld` and `yules_k` (length-robust diversity
  checks on MATTR), line-level metrics (`line_summary`: line count, mean line
  length, and `refrain_ratio` — the share of repeated lines), and `valence_stats`
  (valence mean/std/range/coverage).
- **`stats.py`**: `bootstrap_r`, a percentile-bootstrap confidence interval for
  the report's Pearson correlations (honest uncertainty on n = 7).
- **`data.py`**: the new metrics are surfaced as album/song columns, plus
  `build_vocab_growth` (a career-long type-accumulation curve).
- **Two figures** in `figures.py`: `fig_refrain_over_time` (repeated-line share
  vs. word repetition) and `fig_vocab_growth` (distinct vs. total words over the
  career), registered in `make_figures.py`.
- **Tests**: rewritten `test_figures3d.py` (matplotlib contract + GIF writing),
  new `test_stats.py`, new `test_figures.py` (smoke tests for every 2D builder),
  and extended `test_text.py` for the new metrics.
- Docs: `CHANGELOG.md`, `CONTRIBUTING.md`, and `data/README.md`.
