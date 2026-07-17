# Mitski Lyric Scraper

A small Python scraper for collecting Mitski song lyrics using the [Genius API](https://docs.genius.com/) and genius.com song pages.

The scraper looks up an artist on Genius, discovers every song credited to them, visits each song page politely, extracts the lyric text, and writes the results to JSON.

## Requirements

- Python 3.10+
- No third-party Python packages are required
- A free Genius API access token — create one at <https://genius.com/api-clients> (any client name works; you only need the "Client Access Token")

`requirements.txt` is included as a convenience marker for environments that expect one.

## Usage

```bash
export GENIUS_ACCESS_TOKEN=your-token-here
python scraper.py --output mitski_lyrics.json
```

The token can also be passed explicitly instead of via the environment variable:

```bash
python scraper.py --access-token your-token-here --output mitski_lyrics.json
```

Useful options:

```bash
python scraper.py \
  --artist Mitski \
  --output data/mitski_lyrics.json \
  --delay 1.5 \
  --timeout 20 \
  --include-features
```

- `--artist` — artist name to search for on Genius (default: `Mitski`)
- `--include-features` — also include songs where the artist is only a featured artist, not the primary one
- `--limit` — cap the number of songs scraped, useful for a quick test run

The output file contains metadata, a `songs` list, and an `errors` list for pages that could not be scraped. Each song has:

- `title`
- `url`
- `lyrics`

If a Genius song page can't be scraped, the scraper skips that song by default and records the failure in `errors`. Add `--fail-fast` if you would rather stop on the first failed song.

## Notes

Song discovery goes through the official Genius API, but the lyric text itself is still read from each song's public genius.com page (the API doesn't return full lyrics). Use this for personal/educational purposes, keep the default delay or increase it, and respect Genius's terms of service.
