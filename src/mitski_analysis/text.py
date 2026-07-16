"""Text metrics for the Mitski lyrics corpus.

Everything here operates on plain lyric strings (already cleaned of section
tags and scraper noise by ``scripts/clean_lyrics.py``). The functions are
deliberately dependency-free so they are easy to test and reason about.

Key idea: lexical diversity measured as a raw type-token ratio (TTR) is
*length dependent* -- a longer text mechanically repeats more common words and
so scores a lower TTR even if the writing is no less varied. Because Mitski's
albums differ in total word count, we lead with a length-robust measure
(MATTR, the moving-average type-token ratio) and report the raw TTR alongside
it so the video's original definition is still visible.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from typing import Iterable

# Word token: a run of letters, allowing internal straight apostrophes so
# contractions ("don't", "i'm") stay single tokens. Curly apostrophes are
# folded to straight ones in ``normalize`` before this pattern is applied.
_WORD_RE = re.compile(r"[a-z]+(?:'[a-z]+)*")


def normalize(text: str) -> str:
    """Lower-case and fold typographic apostrophes to a plain ASCII quote."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    return text.lower()


def tokenize(text: str) -> list[str]:
    """Return the ordered list of word tokens in ``text``."""
    return _WORD_RE.findall(normalize(text))


def type_token_ratio(tokens: Iterable[str]) -> float:
    """Raw TTR = unique tokens / total tokens (the video's definition,
    inverted so that *higher means more varied*)."""
    tokens = list(tokens)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def mattr(tokens: list[str], window: int = 50) -> float:
    """Moving-average type-token ratio (Covington & McFall, 2010).

    Averages the TTR of every ``window``-length sliding window, which removes
    the length dependence of a single raw TTR. Falls back to a plain TTR when
    the text is shorter than one window.
    """
    n = len(tokens)
    if n == 0:
        return 0.0
    if n <= window:
        return type_token_ratio(tokens)
    ratios = []
    for start in range(0, n - window + 1):
        chunk = tokens[start : start + window]
        ratios.append(len(set(chunk)) / window)
    return sum(ratios) / len(ratios)


def guiraud_r(tokens: list[str]) -> float:
    """Guiraud's root-TTR: types / sqrt(tokens). Less length-sensitive than
    raw TTR; grows with vocabulary richness."""
    n = len(tokens)
    if n == 0:
        return 0.0
    return len(set(tokens)) / math.sqrt(n)


def hapax_ratio(tokens: list[str]) -> float:
    """Fraction of the vocabulary that appears exactly once (hapax legomena).
    A high value signals reaching for many single-use words."""
    if not tokens:
        return 0.0
    counts = Counter(tokens)
    hapax = sum(1 for c in counts.values() if c == 1)
    return hapax / len(counts)


def mean_word_length(tokens: list[str]) -> float:
    if not tokens:
        return 0.0
    return sum(len(t) for t in tokens) / len(tokens)


def lexical_summary(text: str, window: int = 50) -> dict[str, float]:
    """All scalar lexical metrics for one text blob, in one pass."""
    tokens = tokenize(text)
    return {
        "tokens": len(tokens),
        "types": len(set(tokens)),
        "ttr": type_token_ratio(tokens),
        "mattr": mattr(tokens, window=window),
        "guiraud_r": guiraud_r(tokens),
        "hapax_ratio": hapax_ratio(tokens),
        "mean_word_length": mean_word_length(tokens),
    }


# --- Thematic lexicons -----------------------------------------------------
# Small, transparent keyword sets used to trace recurring imagery across the
# discography. These are intentionally hand-curated and conservative; they are
# a lens on the lyrics, not a claim of exhaustive coverage.
MOTIF_LEXICONS: dict[str, set[str]] = {
    "body": {
        "body", "bodies", "blood", "bone", "bones", "skin", "heart", "hearts",
        "hand", "hands", "eye", "eyes", "mouth", "lips", "hair", "chest",
        "knee", "knees", "arms", "arm", "face", "teeth", "veins", "breath",
    },
    "water": {
        "water", "waters", "sea", "ocean", "wave", "waves", "rain", "river",
        "lake", "tears", "tear", "drown", "drowning", "swim", "flood", "wet",
        "creek", "tide", "pool",
    },
    "fire_light": {
        "fire", "flame", "flames", "burn", "burning", "burns", "light",
        "lights", "spark", "sun", "star", "stars", "glow", "lightning",
        "fireworks", "shine", "bright", "smoke", "ember",
    },
    "home_domestic": {
        "home", "house", "room", "door", "kitchen", "bed", "wall", "walls",
        "lamp", "window", "floor", "table", "husband", "wife", "married",
        "marry", "phone", "car",
    },
    "death": {
        "die", "died", "dying", "death", "dead", "grave", "bury", "buried",
        "ghost", "kill", "gone", "goodbye", "funeral", "coffin", "heaven",
    },
    "animals": {
        "dog", "dogs", "horse", "cat", "cats", "bird", "birds", "wolf",
        "coyote", "buffalo", "bug", "angel", "pearl", "cowboy",
    },
}

# First / second / first-plural person pronoun sets. These trace the shift the
# source video highlights: private "I", the addressed "you", and the collective
# "we" that surfaces by *The Land Is Inhospitable and So Are We*.
PRONOUNS: dict[str, set[str]] = {
    "first_singular": {"i", "i'm", "i'll", "i've", "i'd", "me", "my", "mine", "myself"},
    "second": {"you", "you're", "you'll", "you've", "you'd", "your", "yours", "yourself"},
    "first_plural": {"we", "we're", "we'll", "we've", "us", "our", "ours", "ourselves"},
}


def motif_counts(text: str) -> dict[str, int]:
    """Raw hit count for each motif lexicon in ``text``."""
    tokens = tokenize(text)
    counts = Counter(tokens)
    return {
        motif: sum(counts[w] for w in words)
        for motif, words in MOTIF_LEXICONS.items()
    }


def pronoun_counts(text: str) -> dict[str, int]:
    """Raw pronoun-group counts in ``text``."""
    tokens = tokenize(text)
    counts = Counter(tokens)
    return {
        group: sum(counts[w] for w in words)
        for group, words in PRONOUNS.items()
    }
