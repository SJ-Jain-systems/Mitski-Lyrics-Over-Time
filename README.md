# Mitski, Over Time

A data-driven reading of Mitski's discography. The project takes a claim from a
short video essay, *"she is literally saying less over time… but it's not that
simple"*, and tests it against the lyrics of all seven studio albums, then keeps
going into the themes the video only gestures at.

**The centerpiece is a thorough written report:**
[`report/mitski_lyrics_over_time.qmd`](report/mitski_lyrics_over_time.qmd).
Render it with Quarto (or run `scripts/make_figures.py` to preview the figures
under `figures/`).

## What it finds

- **She really is saying less.** Lyric density falls across her career
  (words-per-minute vs. release year, r ≈ −0.81), and the songs themselves get
  shorter (about 173 words/song on *Lush* down to about 134 on *The Land Is
  Inhospitable and So Are We*).
- **The less she says, the more each word does.** Sparser albums are *less*
  repetitive and reach for a wider vocabulary. In her mature era (*Puberty 2*
  onward) density and repetition track each other almost perfectly (r ≈ 0.92).
  *The Land* is the extreme on both axes: the fewest words per minute and the
  least repetition she has ever released.
- **What each album is about, in its own words.** A weighted log-odds keyness
  analysis surfaces each record's most distinctive vocabulary, from the underwater
  *dive/diver/pearl* of *Lush* to the *mine/heaven/gone* of *The Land*. Those
  words anchor close readings of real lyric lines and a song-by-song spotlight.
- **Themes shift with the sparseness.** The collective *"we"* and the imagery of
  *death* both rise on exactly the late, low-word records, the ones where, as the
  album covers do, she pulls the camera back.
- **The mood does not follow the words.** Average word-level sentiment (AFINN)
  barely tracks the records: *The Land*, her album about mortality, scores mildly
  *positive*. Mitski keeps her darkest meaning in her plainest words, and the
  report reads that gap rather than papering over it.

## Layout

```
data/
  raw/         mitski_lyrics.json           # original Genius scrape (153 entries)
  processed/   mitski_lyrics_clean.json     # cleaned lyric text
               album_stats.csv, song_stats.csv   # generated analysis tables
  metadata/    albums.json                  # canonical tracklists, dates, durations (curated)
  lexicons/    valence_afinn.txt            # bundled AFINN sentiment lexicon (ODbL)
src/mitski_analysis/
  text.py      tokenizing + lexical/theme metrics (TTR, MATTR, motifs, pronouns,
               distinctive-word keyness, AFINN valence)
  data.py      joins lyrics <-> album metadata into tidy tables
  theme.py     matplotlib theme (validated data-viz palette)
  figures.py   the report's figures
  figures3d.py interactive 3D figures (Plotly): the evolution trajectory,
               the motif terrain, the per-song cloud, the pronoun trajectory
scripts/
  clean_lyrics.py     raw scrape -> cleaned lyrics
  build_dataset.py    -> data/processed/*.csv
  make_figures.py     -> figures/*.png
  make_3d.py          -> figures/3d/*.html  (standalone, interactive)
report/
  mitski_lyrics_over_time.qmd   # the report
tests/         unit + integration tests
```

## Reproduce

```bash
pip install -r requirements.txt
python scripts/clean_lyrics.py            # (already committed; regenerates cleaned lyrics)
python scripts/build_dataset.py           # album + song stats
python scripts/make_figures.py            # preview figures (static PNG)
python scripts/make_3d.py                 # interactive 3D figures -> figures/3d/*.html
python -m pytest tests/                    # tests

# Render the report (needs the Quarto CLI from quarto.org + a Jupyter kernel):
quarto render report/mitski_lyrics_over_time.qmd
```

## Notes on the data

The lyric corpus carries no album, date, or duration fields and mixes canonical
tracks with live versions, demos, translations, and covers. `data/metadata/albums.json`
supplies the studio-album structure (release dates + total runtimes sourced from
Discogs / Apple Music / Wikipedia, with provenance recorded per album), and the
join in `data.py` fails loudly if any canonical track is missing, so album totals
can never silently drop a song. Word-level sentiment uses the AFINN valence
lexicon (Finn Årup Nielsen, 2011), bundled under `data/lexicons/` and released
under the Open Database License. Lyrics are quoted only in short excerpts, for
commentary and criticism. Analysis covers the seven studio albums for which
lyrics are available; see the report's *Limitations* section for the full
caveats.
