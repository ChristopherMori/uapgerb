# UAPGerb Wiki

This repository automatically mirrors videos from the [UAPGerb](https://www.youtube.com/@UAPGerb) YouTube channel.
Transcripts are fetched with `yt-dlp` and `youtube-transcript-api` and published as a static site built by [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

## Usage

Sync the default UAPGerb channel into `docs/transcripts`:

```bash
python scripts/sync.py
```

Specify a different channel or output directory:

```bash
python scripts/sync.py --channel https://www.youtube.com/@OtherChannel --output-dir docs/other
```

Limit the number of videos processed:

```bash
python scripts/sync.py --max-videos 5
```
