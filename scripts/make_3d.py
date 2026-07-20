#!/usr/bin/env python3
"""Render the interactive 3D figures to standalone HTML under figures/3d/.

Each file is fully self-contained (the Plotly runtime is inlined), so it opens
in any browser with no server and no network. The Quarto report imports the same
``figures3d`` functions, so the report and these files render identical charts.

Run from the repo root:  python scripts/make_3d.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from mitski_analysis import figures3d as F3  # noqa: E402
from mitski_analysis.data import build_album_table, build_song_table, repo_root  # noqa: E402

RENDERERS = {
    "01_evolution_trajectory": lambda a, s: F3.fig3d_trajectory(a),
    "02_motif_terrain": lambda a, s: F3.fig3d_motif_terrain(a),
    "03_song_cloud": lambda a, s: F3.fig3d_song_cloud(s, a),
    "04_pronoun_trajectory": lambda a, s: F3.fig3d_pronoun_trajectory(a),
}


def main() -> None:
    root = repo_root()
    out = root / "figures" / "3d"
    out.mkdir(parents=True, exist_ok=True)
    albums = build_album_table(root)
    songs = build_song_table(root)

    for name, fn in RENDERERS.items():
        fig = fn(albums, songs)
        path = out / f"{name}.html"
        fig.write_html(str(path), include_plotlyjs=True, full_html=True,
                       config={"displaylogo": False, "responsive": True})
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
