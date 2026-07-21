# Convenience targets for the Mitski-lyrics-over-time project.
# Everything runs through pure Python (+ Quarto only for the final report).

PYTHON ?= python

.PHONY: help install data figures viz3d report test lint format all clean

help:
	@echo "Targets:"
	@echo "  install   pip install -e .[dev]  (editable + dev tools)"
	@echo "  data      build data/processed/*.csv from the lyrics + metadata"
	@echo "  figures   render the 2D figures to figures/*.png"
	@echo "  viz3d     render the 3D figures to figures/3d/*.png and *.gif"
	@echo "  report    quarto render the report (needs the Quarto CLI)"
	@echo "  test      run the pytest suite"
	@echo "  lint      ruff check"
	@echo "  format    ruff format"
	@echo "  all       data + figures + viz3d + test"
	@echo "  clean     remove generated figures/ and processed CSVs"

install:
	$(PYTHON) -m pip install -e .[dev]

data:
	$(PYTHON) scripts/build_dataset.py

figures:
	$(PYTHON) scripts/make_figures.py

viz3d:
	$(PYTHON) scripts/make_3d.py

# The report is the one step that still needs the external Quarto CLI + a Jupyter
# kernel (see requirements.txt). Everything it renders is pure-Python matplotlib.
report:
	quarto render report/mitski_lyrics_over_time.qmd

test:
	$(PYTHON) -m pytest tests/

lint:
	ruff check .

format:
	ruff format .

all: data figures viz3d test

clean:
	rm -rf figures/
	rm -f data/processed/album_stats.csv data/processed/song_stats.csv
