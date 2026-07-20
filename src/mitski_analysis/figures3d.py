"""Interactive 3D figures for the report, built with Plotly.

Static 3D (a single frozen camera angle) tends to mislead — you cannot read
depth from one projection. These figures are therefore interactive: the reader
rotates, zooms, and reads values off hover, which is where a third spatial axis
actually earns its place. Each ``fig3d_*`` function takes the album (and
sometimes song) table and returns a ``plotly.graph_objects.Figure``, mirroring
the ``figures.py`` contract so a script and the Quarto document render the same
charts.

Colour and chrome follow the same house palette as the 2D figures (see
``theme.py``): the fixed-order categorical set assigned by entity, the single-hue
blue ramp for ordered magnitude, and recessive grey chrome so the marks carry
the ink. Time — the axis the whole project is about — is carried consistently by
the blue sequential ramp, early (light) to late (dark).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from . import theme as TH

# Short album labels, single line (Plotly text has no manual line breaks here).
SHORT = {
    "Lush": "Lush",
    "Retired from Sad, New Career in Business": "Retired from Sad",
    "Bury Me at Makeout Creek": "Bury Me at Makeout Creek",
    "Puberty 2": "Puberty 2",
    "Be the Cowboy": "Be the Cowboy",
    "Laurel Hell": "Laurel Hell",
    "The Land Is Inhospitable and So Are We": "The Land Is Inhospitable…",
}

# Fonts and chrome ported from the matplotlib theme so the 3D figures sit in the
# report as one visual system.
_FONT = dict(family="DejaVu Sans, Segoe UI, Helvetica, Arial", size=13, color=TH.INK)
_AXIS_BG = "rgba(0,0,0,0)"


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _blues_colorscale() -> list[list]:
    """The house blue ramp as a Plotly colorscale (light -> dark)."""
    n = len(TH.SEQUENTIAL)
    return [[i / (n - 1), c] for i, c in enumerate(TH.SEQUENTIAL)]


def _base_layout(title: str, scene: dict, height: int = 640) -> go.Layout:
    return go.Layout(
        title=dict(text=title, font=dict(size=17, color=TH.INK), x=0.02, xanchor="left"),
        font=_FONT,
        paper_bgcolor=TH.SURFACE,
        plot_bgcolor=TH.SURFACE,
        height=height,
        margin=dict(l=0, r=0, t=54, b=0),
        scene=scene,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12, color=TH.INK_2)),
    )


def _axis(title: str, **kw) -> dict:
    return dict(
        title=dict(text=title, font=dict(size=12, color=TH.INK_2)),
        backgroundcolor=_AXIS_BG,
        gridcolor=TH.GRID,
        zerolinecolor=TH.BASELINE,
        showbackground=True,
        tickfont=dict(size=10, color=TH.MUTED),
        **kw,
    )


# --------------------------------------------------------------------------- #
# 1. The evolution trajectory: a rotatable path through "lyric space".
#    X = word density, Y = lexical diversity, Z = repetition, time by colour.
# --------------------------------------------------------------------------- #
def fig3d_trajectory(albums: pd.DataFrame) -> go.Figure:
    order = albums.sort_values("release_date").reset_index(drop=True)
    x = order["words_per_minute"]
    y = order["mattr"]
    z = order["repetition_index"]
    years = order["release_year"]
    names = [SHORT[a] for a in order["album"]]

    hover = (
        "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
        "Words/min: %{x:.1f}<br>"
        "Lexical diversity (MATTR): %{y:.2f}<br>"
        "Repetition index: %{z:.2f}<extra></extra>"
    )
    customdata = np.column_stack([names, years])

    fig = go.Figure()

    # The path itself: an ordered line through time, recessive so the markers
    # (the albums) carry the ink.
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z, mode="lines",
        line=dict(color=TH.MUTED, width=4),
        hoverinfo="skip", showlegend=False,
    ))

    # Album markers, coloured by release year on the house blue ramp so the
    # travel direction (early = light, late = dark) is legible at a glance.
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z, mode="markers+text",
        marker=dict(
            size=9, color=years, colorscale=_blues_colorscale(),
            line=dict(color=TH.SURFACE, width=1.5),
            colorbar=dict(
                title=dict(text="Release<br>year", font=dict(size=11, color=TH.INK_2)),
                tickfont=dict(size=10, color=TH.MUTED),
                len=0.55, thickness=12, x=0.98,
            ),
        ),
        text=names, textposition="top center",
        textfont=dict(size=10, color=TH.INK_2),
        customdata=customdata, hovertemplate=hover, showlegend=False,
    ))

    # Faint drop-lines to the floor give the eye a depth cue without a second
    # camera angle.
    zfloor = float(z.min()) - 0.15
    for xi, yi, zi in zip(x, y, z):
        fig.add_trace(go.Scatter3d(
            x=[xi, xi], y=[yi, yi], z=[zi, zfloor], mode="lines",
            line=dict(color=TH.GRID, width=1.5), hoverinfo="skip", showlegend=False,
        ))

    fig.update_layout(_base_layout(
        "The path through lyric space  ·  drag to rotate",
        scene=dict(
            xaxis=_axis("Words per minute  →  denser"),
            yaxis=_axis("Lexical diversity (MATTR)  →  wider"),
            zaxis=_axis("Repetition index  →  more repetitive"),
            camera=dict(eye=dict(x=1.6, y=1.5, z=0.9)),
            aspectmode="cube",
        ),
    ))
    return fig


# --------------------------------------------------------------------------- #
# 2. Motif terrain: the motif heatmap as a 3D surface.
#    Height = imagery rate per 1,000 words; ridges rise on the late albums.
# --------------------------------------------------------------------------- #
def fig3d_motif_terrain(albums: pd.DataFrame) -> go.Figure:
    motifs = ["body", "water", "fire_light", "home_domestic", "death", "animals"]
    nice = ["Body", "Water", "Fire / light", "Home", "Death", "Animals"]
    order = albums.sort_values("release_date").reset_index(drop=True)
    labels = [SHORT[a] for a in order["album"]]

    # Rows = albums (time), cols = motifs; Z = rate per 1k words.
    Z = np.array([[row[f"motif_{m}_per_1k"] for m in motifs] for _, row in order.iterrows()])

    hover = (
        "<b>%{y}</b><br>%{x}<br>Rate: %{z:.1f} per 1,000 words<extra></extra>"
    )

    fig = go.Figure(data=[go.Surface(
        z=Z, x=nice, y=labels,
        colorscale=_blues_colorscale(),
        colorbar=dict(
            title=dict(text="Per 1,000<br>words", font=dict(size=11, color=TH.INK_2)),
            tickfont=dict(size=10, color=TH.MUTED), len=0.6, thickness=12,
        ),
        contours=dict(z=dict(show=True, usecolormap=True, project_z=True,
                             width=1, color=TH.GRID)),
        hovertemplate=hover,
        lighting=dict(ambient=0.75, diffuse=0.5, roughness=0.9, specular=0.1),
    )])

    fig.update_layout(_base_layout(
        "Recurring imagery as terrain  ·  drag to rotate",
        scene=dict(
            xaxis=_axis("Motif", tickangle=0),
            yaxis=_axis("Album  (early → late)"),
            zaxis=_axis("Rate per 1,000 words"),
            camera=dict(eye=dict(x=1.7, y=-1.5, z=1.0)),
            aspectratio=dict(x=1.1, y=1.4, z=0.7),
        ),
    ))
    return fig


# --------------------------------------------------------------------------- #
# 3. Per-song cloud: 75 songs in density × diversity × word-length space,
#    coloured by album, to show how the spread moves era to era.
# --------------------------------------------------------------------------- #
def fig3d_song_cloud(songs: pd.DataFrame, albums: pd.DataFrame) -> go.Figure:
    order = albums.sort_values("release_date")["album"].tolist()
    color_by_album = {a: TH.CATEGORICAL[i % len(TH.CATEGORICAL)] for i, a in enumerate(order)}

    fig = go.Figure()
    for album in order:
        sub = songs[songs["album"] == album]
        hover = (
            "<b>%{customdata[0]}</b><br>" + SHORT[album] + "<br>"
            "Words: %{x}<br>Diversity (MATTR): %{y:.2f}<br>"
            "Mean word length: %{z:.2f}<extra></extra>"
        )
        fig.add_trace(go.Scatter3d(
            x=sub["word_count"], y=sub["mattr"], z=sub["mean_word_length"],
            mode="markers", name=SHORT[album],
            marker=dict(size=5, color=color_by_album[album],
                        line=dict(color=TH.SURFACE, width=0.5), opacity=0.9),
            customdata=np.column_stack([sub["title"]]),
            hovertemplate=hover,
        ))

    fig.update_layout(_base_layout(
        "Every song in three dimensions  ·  drag to rotate, click a legend album to isolate",
        scene=dict(
            xaxis=_axis("Words per song"),
            yaxis=_axis("Lexical diversity (MATTR)"),
            zaxis=_axis("Mean word length"),
            camera=dict(eye=dict(x=1.6, y=1.6, z=0.8)),
            aspectmode="cube",
        ),
    ))
    return fig


# --------------------------------------------------------------------------- #
# 4. Pronoun trajectory: the compositional I / you / we path over time.
#    The three shares sum to 1, so the points live on a plane; the 3D view
#    keeps that constraint visible while time bends the path.
# --------------------------------------------------------------------------- #
def fig3d_pronoun_trajectory(albums: pd.DataFrame) -> go.Figure:
    order = albums.sort_values("release_date").reset_index(drop=True)
    I = order["pron_first_singular_share"]
    you = order["pron_second_share"]
    we = order["pron_first_plural_share"]
    years = order["release_year"]
    names = [SHORT[a] for a in order["album"]]

    hover = (
        "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
        "I / me / my: %{x:.0%}<br>you / your: %{y:.0%}<br>"
        "we / us / our: %{z:.0%}<extra></extra>"
    )
    customdata = np.column_stack([names, years])

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=I, y=you, z=we, mode="lines",
        line=dict(color=TH.MUTED, width=4), hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Scatter3d(
        x=I, y=you, z=we, mode="markers+text",
        marker=dict(size=9, color=years, colorscale=_blues_colorscale(),
                    line=dict(color=TH.SURFACE, width=1.5),
                    colorbar=dict(
                        title=dict(text="Release<br>year", font=dict(size=11, color=TH.INK_2)),
                        tickfont=dict(size=10, color=TH.MUTED),
                        len=0.55, thickness=12, x=0.98)),
        text=names, textposition="top center",
        textfont=dict(size=10, color=TH.INK_2),
        customdata=customdata, hovertemplate=hover, showlegend=False,
    ))

    fig.update_layout(_base_layout(
        "Who the songs address, over time  ·  drag to rotate",
        scene=dict(
            xaxis=_axis("Share: I / me / my", tickformat=".0%"),
            yaxis=_axis("Share: you / your", tickformat=".0%"),
            zaxis=_axis("Share: we / us / our", tickformat=".0%"),
            camera=dict(eye=dict(x=1.6, y=1.5, z=1.0)),
            aspectmode="cube",
        ),
    ))
    return fig
