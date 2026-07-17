"""Load the cleaned lyrics corpus and album metadata, and join them into the
tidy per-song and per-album tables that every figure and the report consume.

The corpus (``data/processed/mitski_lyrics_clean.json``) is a flat list of 153
song entries with no album, date, or duration fields, and it mixes canonical
album tracks with live versions, demos, translations, covers, and non-album
singles. ``data/metadata/albums.json`` supplies the canonical studio-album
tracklists plus release dates and durations. Joining the two is what makes the
words-per-minute-over-time analysis possible.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import pandas as pd

from . import text as T


def repo_root(start: Path | None = None) -> Path:
    """Walk upward from ``start`` (default: this file) until we find the repo
    root, identified by the presence of the ``data`` directory."""
    here = (start or Path(__file__)).resolve()
    for parent in [here, *here.parents]:
        if (parent / "data" / "metadata" / "albums.json").exists():
            return parent
    raise FileNotFoundError("Could not locate repo root (data/metadata/albums.json).")


def _match_key(title: str) -> str:
    """Normalize a song title to a punctuation-insensitive match key so the
    corpus's curly apostrophes / slashes line up with the metadata's ASCII
    spellings. 'First Love / Late Spring' -> 'first love late spring'."""
    title = unicodedata.normalize("NFKC", title)
    title = title.replace("’", "'").replace("‘", "'")
    title = title.lower()
    title = re.sub(r"[^a-z0-9 ]+", " ", title)  # drop apostrophes, slashes, punctuation
    return re.sub(r"\s+", " ", title).strip()


def load_corpus(root: Path | None = None) -> dict:
    root = root or repo_root()
    path = root / "data" / "processed" / "mitski_lyrics_clean.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_album_metadata(root: Path | None = None) -> dict:
    root = root or repo_root()
    path = root / "data" / "metadata" / "albums.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_song_table(root: Path | None = None) -> pd.DataFrame:
    """One row per canonical studio-album track, with lyric text, metrics, and
    its album/date. Raises if a listed canonical track is missing from the
    corpus, so metadata drift can never silently drop a song."""
    root = root or repo_root()
    corpus = load_corpus(root)
    meta = load_album_metadata(root)

    by_key: dict[str, dict] = {}
    for song in corpus["songs"]:
        by_key.setdefault(_match_key(song["title"]), song)

    rows = []
    missing = []
    for album in meta["albums"]:
        for position, track in enumerate(album["tracks"], start=1):
            song = by_key.get(_match_key(track))
            if song is None:
                missing.append(f"{album['album']} :: {track}")
                continue
            lyrics = song["lyrics"]
            summary = T.lexical_summary(lyrics)
            row = {
                "album": album["album"],
                "album_no": album["album_no"],
                "release_date": pd.Timestamp(album["release_date"]),
                "release_year": pd.Timestamp(album["release_date"]).year,
                "track_no": position,
                "title": track,
                "corpus_title": song["title"],
                "word_count": summary["tokens"],
                **{k: v for k, v in summary.items() if k != "tokens"},
            }
            row.update({f"pron_{k}": v for k, v in T.pronoun_counts(lyrics).items()})
            row.update({f"motif_{k}": v for k, v in T.motif_counts(lyrics).items()})
            rows.append(row)

    if missing:
        raise ValueError(
            "Canonical tracks missing from the corpus:\n  " + "\n  ".join(missing)
        )

    return pd.DataFrame(rows)


def build_album_table(root: Path | None = None) -> pd.DataFrame:
    """One row per studio album with aggregate lyric statistics.

    Word counts and lexical metrics are computed on the *concatenation* of the
    album's canonical lyrics (so diversity is measured across the record as a
    whole, matching the video's album-level framing), while durations come from
    the metadata file.
    """
    root = root or repo_root()
    meta = load_album_metadata(root)
    corpus = load_corpus(root)

    by_key: dict[str, dict] = {}
    for song in corpus["songs"]:
        by_key.setdefault(_match_key(song["title"]), song)

    valence_lexicon = T.load_valence_lexicon(root)

    rows = []
    for album in meta["albums"]:
        texts = [by_key[_match_key(t)]["lyrics"] for t in album["tracks"]]
        blob = "\n".join(texts)
        summary = T.lexical_summary(blob)
        duration_min = album["duration_seconds"] / 60.0
        total_words = summary["tokens"]
        pron = T.pronoun_counts(blob)
        motif = T.motif_counts(blob)
        row = {
            "album": album["album"],
            "album_no": album["album_no"],
            "release_date": pd.Timestamp(album["release_date"]),
            "release_year": pd.Timestamp(album["release_date"]).year,
            "n_tracks": len(album["tracks"]),
            "duration_seconds": album["duration_seconds"],
            "duration_minutes": duration_min,
            "duration_display": album["duration_display"],
            "total_words": total_words,
            "unique_words": summary["types"],
            "words_per_minute": total_words / duration_min,
            "words_per_track": total_words / len(album["tracks"]),
            "ttr": summary["ttr"],
            "mattr": summary["mattr"],
            "guiraud_r": summary["guiraud_r"],
            "hapax_ratio": summary["hapax_ratio"],
            "mean_word_length": summary["mean_word_length"],
            # Video's literal definition: total / unique (mean repetition of a word).
            "repetition_index": total_words / summary["types"],
            # Mean emotional valence of the album's words (AFINN, -5..+5).
            "mean_valence": T.mean_valence(blob, valence_lexicon),
        }
        total_pron = sum(pron.values()) or 1
        for k, v in pron.items():
            row[f"pron_{k}"] = v
            row[f"pron_{k}_share"] = v / total_pron
        for k, v in motif.items():
            row[f"motif_{k}"] = v
            row[f"motif_{k}_per_1k"] = 1000 * v / total_words
        rows.append(row)

    df = pd.DataFrame(rows).sort_values("release_date").reset_index(drop=True)
    return df


def build_distinctive_table(root: Path | None = None, n: int = 8) -> pd.DataFrame:
    """One row per studio album listing the ``n`` words most distinctive of that
    album relative to the pooled rest of the discography.

    Each album's lyrics are scored against every other album's lyrics combined,
    using ``text.distinctive_words`` (weighted log-odds with a Dirichlet prior),
    so the result surfaces what each record is *about* rather than which words
    are simply frequent. The ``words`` column is a ready-to-print comma-joined
    string; ``scored`` keeps the underlying (word, score) pairs.
    """
    root = root or repo_root()
    meta = load_album_metadata(root)
    corpus = load_corpus(root)

    by_key: dict[str, dict] = {}
    for song in corpus["songs"]:
        by_key.setdefault(_match_key(song["title"]), song)

    # Per-album token frequency maps, in release order.
    albums_meta = sorted(meta["albums"], key=lambda a: a["release_date"])
    counts_by_album: list[tuple[dict, "object"]] = []
    for album in albums_meta:
        blob = "\n".join(by_key[_match_key(t)]["lyrics"] for t in album["tracks"])
        counts_by_album.append((album, T.word_counts(blob)))

    rows = []
    for i, (album, target) in enumerate(counts_by_album):
        background = Counter()
        for j, (_, other) in enumerate(counts_by_album):
            if j != i:
                background.update(other)
        scored = T.distinctive_words(target, background, n=n)
        rows.append({
            "album": album["album"],
            "album_no": album["album_no"],
            "release_year": pd.Timestamp(album["release_date"]).year,
            "words": ", ".join(w for w, _ in scored),
            "scored": scored,
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":  # quick smoke check
    albums = build_album_table()
    cols = ["album", "release_year", "total_words", "duration_minutes",
            "words_per_minute", "mattr", "repetition_index"]
    print(albums[cols].to_string(index=False))
