# Mitski, Over Time

A data-driven reading of Mitski's discography. The project takes a claim from a
short video essay — *"she is literally saying less over time… but it's not that
simple"* — and tests it against the lyrics of all seven studio albums, then keeps
going into the themes the video only gestures at.

**The centerpiece is a thorough written report:**
[`report/mitski_lyrics_over_time.qmd`](report/mitski_lyrics_over_time.qmd).
Render it with Quarto (or run `scripts/make_figures.py` to preview the figures
under `figures/`).

## What it finds

- **She really is saying less.** Lyric density falls across her career
  (words-per-minute vs. release year, r ≈ −0.81), and the songs themselves get
  shorter (~173 words/song on *Lush* → ~134 on *The Land Is Inhospitable and So
  Are We*).
- **The less she says, the more each word does.** Sparser albums are *less*
  repetitive and reach for a wider vocabulary. In her mature era (*Puberty 2*
  onward) density and repetition track each other almost perfectly (r ≈ 0.92).
  *The Land* is the extreme on both axes: the fewest words per minute and the
  least repetition she has ever released.
- **Themes shift with the sparseness.** The collective *"we"* and the imagery of
  *death* both rise on exactly the late, low-word records — the ones where, as
  the album covers do, she pulls the camera back.

## Layout

```
data/
  raw/         mitski_lyrics.json           # original Genius scrape (153 entries)
  processed/   mitski_lyrics_clean.json     # cleaned lyric text
               album_stats.csv, song_stats.csv   # generated analysis tables
  metadata/    albums.json                  # canonical tracklists, dates, durations (curated)
src/mitski_analysis/
  text.py      tokenizing + lexical/theme metrics (TTR, MATTR, motifs, pronouns)
  data.py      joins lyrics <-> album metadata into tidy tables
  theme.py     matplotlib theme (validated data-viz palette)
  figures.py   the report's figures
scripts/
  clean_lyrics.py     raw scrape -> cleaned lyrics
  build_dataset.py    -> data/processed/*.csv
  make_figures.py     -> figures/*.png
report/
  mitski_lyrics_over_time.qmd   # the report
tests/         unit + integration tests
```

## Reproduce

```bash
pip install -r requirements.txt
python scripts/clean_lyrics.py            # (already committed; regenerates cleaned lyrics)
python scripts/build_dataset.py           # album + song stats
python scripts/make_figures.py            # preview figures
python -m pytest tests/                    # 14 tests

# Render the report (needs the Quarto CLI from quarto.org + a Jupyter kernel):
quarto render report/mitski_lyrics_over_time.qmd
```

## Notes on the data

The lyric corpus carries no album, date, or duration fields and mixes canonical
tracks with live versions, demos, translations, and covers. `data/metadata/albums.json`
supplies the studio-album structure (release dates + total runtimes sourced from
Discogs / Apple Music / Wikipedia, with provenance recorded per album), and the
join in `data.py` fails loudly if any canonical track is missing — so album
totals can never silently drop a song. Analysis covers the seven studio albums
for which lyrics are available; see the report's *Limitations* section for the
full caveats.
