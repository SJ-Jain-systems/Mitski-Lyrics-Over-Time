# Data

The analysis reads three committed inputs and derives everything else. The
generated tables under `processed/` are git-ignored build artifacts — rebuild
them with `python scripts/build_dataset.py`.

## Inputs (committed)

| Path                                  | What it is                                                                 |
| ------------------------------------- | -------------------------------------------------------------------------- |
| `raw/mitski_lyrics.json`              | Original Genius scrape, 153 entries (with scraper header noise).           |
| `processed/mitski_lyrics_clean.json`  | Cleaned lyric text, same shape, produced by `scripts/clean_lyrics.py`.     |
| `metadata/albums.json`                | Curated: 7 studio albums with `album_no`, `release_date`, `duration_seconds`, `duration_display`, `duration_source`, and canonical `tracks[]`. |
| `lexicons/valence_afinn.txt`          | Bundled AFINN valence lexicon (`word<TAB>score`, −5..+5), ODbL.            |

## Derived tables

Built by `src/mitski_analysis/data.py`. All metrics are defined and unit-tested
in `src/mitski_analysis/text.py`.

### `build_album_table()` — one row per studio album
Identity: `album`, `album_no`, `release_date`, `release_year`, `n_tracks`,
`duration_seconds`, `duration_minutes`, `duration_display`.

Density: `total_words`, `unique_words`, `words_per_minute`, `words_per_track`,
`repetition_index` (= total ÷ unique, the source video's definition).

Diversity (length-robust): `ttr`, `mattr`, `guiraud_r`, `mtld`, `yules_k`,
`hapax_ratio`, `mean_word_length`.

Structure / compression: `line_count`, `lines_per_song`, `mean_line_length`,
`refrain_ratio` (share of lines that repeat an earlier line).

Sentiment (AFINN): `mean_valence`, `valence_std`, `valence_range`,
`valence_coverage` (share of tokens the lexicon scored).

Pronouns: `pron_{first_singular,second,first_plural}` and their `_share`.

Motifs: `motif_{body,water,fire_light,home_domestic,death,animals}` and their
`_per_1k` (rate per 1,000 words).

### `build_song_table()` — one row per canonical track
The same lexical / structure / pronoun / motif metrics computed per song, plus
`track_no`, `title`, `corpus_title`, `word_count`, `types`. Raises if any
canonical track from the metadata is missing from the corpus, so album totals
can never silently drop a song.

### `build_vocab_growth()` — one row per track, in release order
`album`, `album_no`, `release_year`, `title`, `cumulative_words`,
`cumulative_types` (the career-long type-accumulation curve).

## Notes

Word-level sentiment uses the AFINN valence lexicon (Finn Årup Nielsen, 2011),
released under the Open Database License. Album runtimes were compiled from
Discogs, Apple Music, and Wikipedia, with the source recorded per album in
`metadata/albums.json`.
