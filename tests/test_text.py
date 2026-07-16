"""Unit tests for the lexical-metric functions.

Run with:  python -m pytest tests/  (or: python tests/test_text.py)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from mitski_analysis import text as T


def test_tokenize_keeps_contractions():
    assert T.tokenize("I don't know, I'm fine") == ["i", "don't", "know", "i'm", "fine"]


def test_tokenize_folds_curly_apostrophe():
    # Curly and straight apostrophes must tokenize identically.
    assert T.tokenize("I don’t") == T.tokenize("I don't") == ["i", "don't"]


def test_ttr_bounds():
    assert T.type_token_ratio([]) == 0.0
    assert T.type_token_ratio(["a", "a", "a"]) == 1 / 3
    assert T.type_token_ratio(["a", "b", "c"]) == 1.0


def test_mattr_falls_back_to_ttr_when_short():
    toks = ["a", "b", "a", "c"]
    assert T.mattr(toks, window=50) == T.type_token_ratio(toks)


def test_mattr_windowed_value():
    # Two windows of ["a","b"] and ["b","c"] over window=2 -> each TTR 1.0.
    toks = ["a", "b", "c"]
    assert T.mattr(toks, window=2) == 1.0
    # A repeated window pulls the average below 1.
    toks2 = ["a", "a", "b"]
    # windows: ["a","a"]=0.5, ["a","b"]=1.0 -> mean 0.75
    assert abs(T.mattr(toks2, window=2) - 0.75) < 1e-9


def test_hapax_ratio():
    # vocab {a,b,c}; a appears twice, b and c once -> 2/3 hapax.
    assert abs(T.hapax_ratio(["a", "a", "b", "c"]) - 2 / 3) < 1e-9


def test_pronoun_counts():
    counts = T.pronoun_counts("I love you and you love us")
    assert counts["first_singular"] == 1     # "I"
    assert counts["second"] == 2             # "you" x2
    assert counts["first_plural"] == 1       # "us"


def test_motif_counts():
    counts = T.motif_counts("blood and bones and water and water")
    assert counts["body"] == 2               # blood, bones
    assert counts["water"] == 2              # water x2


def test_lexical_summary_keys():
    s = T.lexical_summary("a b a b c")
    assert set(s) >= {"tokens", "types", "ttr", "mattr", "guiraud_r",
                      "hapax_ratio", "mean_word_length"}
    assert s["tokens"] == 5 and s["types"] == 3


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
