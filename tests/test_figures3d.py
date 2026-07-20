"""Smoke tests for the interactive 3D figures.

These mirror the contract the report and scripts/make_3d.py rely on: every
``fig3d_*`` builder returns a Plotly Figure with at least one trace, built from
the real album/song tables (so a schema drift in data.py fails loudly here).
"""

import sys
from pathlib import Path

import plotly.graph_objects as go
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from mitski_analysis import figures3d as F3
from mitski_analysis.data import build_album_table, build_song_table


@pytest.fixture(scope="module")
def tables():
    return build_album_table(), build_song_table()


def test_trajectory_builds(tables):
    albums, _ = tables
    fig = F3.fig3d_trajectory(albums)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1


def test_motif_terrain_is_a_surface(tables):
    albums, _ = tables
    fig = F3.fig3d_motif_terrain(albums)
    assert isinstance(fig, go.Figure)
    surface = fig.data[0]
    # Rows = 7 albums, cols = 6 motifs.
    assert len(surface.z) == 7
    assert len(surface.z[0]) == 6


def test_song_cloud_has_one_trace_per_album(tables):
    albums, songs = tables
    fig = F3.fig3d_song_cloud(songs, albums)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == len(albums)


def test_pronoun_trajectory_builds(tables):
    albums, _ = tables
    fig = F3.fig3d_pronoun_trajectory(albums)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1
