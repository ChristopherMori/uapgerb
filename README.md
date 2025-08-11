**TLDR**
You pulled every UAP Gerb video’s audio with `yt‑dlp`, transcribed locally using Whisper on your GPU, and saved research‑friendly artifacts (.txt, .srt, .vtt, optional word‑level JSON) alongside a metadata catalog (CSV/JSON) and an HTML report of the whole channel. This README documents the why, what, and how so anyone can reproduce or audit the pipeline end‑to‑end. The collection currently contains **43 videos** and a structured record for each (title, URL, video\_id, embed, etc.).   The JSON/CSV schema mirrors those fields for programmatic work.&#x20;

---

# UAP Gerb Transcripts – Methods, Provenance, and Files

## Scope & Purpose

This repository preserves and makes searchable the UAP Gerb YouTube channel’s content for archival and research use. It explains the exact pipeline used to pull video metadata, extract audio, transcribe with a local GPU (Whisper), and publish transcripts in open formats with timestamps and reproducible metadata.

---

## What’s in this collection

* **Channel coverage:** 43 unique videos captured as of Aug 11, 2025.&#x20;
* **Per‑video metadata fields:** `title`, `url`, `video_id`, `embed_url`, `html_embed`, and transcript status.&#x20;
* **Research artifacts (per video):**

  * `transcripts/<video_id>.txt` – plain text transcript
  * `subtitles/<video_id>.srt` – subtitle with timestamps
  * `subtitles/<video_id>.vtt` – WebVTT with timestamps
  * `json/<video_id>.json` – optional word/segment‑level JSON (start/end/text, confidence)
* **Catalog files for programmatic work:**

  * `uap_gerb_complete_results.json` – machine‑readable catalog (all videos)&#x20;
  * `uap_gerb_results.csv` – spreadsheet‑friendly slice of the same catalog
* **Human‑readable report:**

  * `uap_gerb_report.html` – browsable cards with links and ready‑to‑paste embed codes.&#x20;
* **Guide:**

  * `transcript_extraction_guide.md` – alternative methods and batch recipes (YouTube captions API, `yt‑dlp`, etc.).

> The HTML report explicitly lists all videos, their IDs, and embed codes; it reflects the 43‑video count and provides a quick way to verify coverage.&#x20;

---

## Methodology – End‑to‑End Pipeline

### 1) Catalog the channel

We first built a canonical list of videos and structured metadata for each entry.

* **Input:** UAP Gerb channel handle `@UAPGerb`.
* **Process:** Resolve the channel, enumerate uploads, and capture key fields: title, URL, `video_id`, embed URL, example embed HTML, plus a transcript flag. The repository’s JSON shows this schema and representative entries.&#x20;
* **Outputs:**

  * `uap_gerb_complete_results.json` – authoritative per‑video records (programmatic source of truth).&#x20;
  * `uap_gerb_results.csv` – Excel/Sheets‑ready view.
  * `uap_gerb_report.html` – human‑friendly browse & embed page.&#x20;

### 2) Retrieve audio for transcription

We extracted only audio (not full video) to speed up transcription and minimize storage.

* **Tooling:** `yt‑dlp` + `ffmpeg`
* **Typical command:**

  ```bash
  yt-dlp -f bestaudio[ext=m4a]/bestaudio \
         -o "audio/%(id)s.%(ext)s" \
         "https://www.youtube.com/watch?v=<VIDEO_ID>"
  ```
* **Notes:**

  * M4A (AAC) offers a good balance of fidelity and speed.
  * File is named by `video_id` to maintain one‑to‑one mapping with catalog entries.

### 3) GPU transcription with Whisper

You used Whisper locally on your GPU to transcribe each audio file offline.

* **Why local (Whisper) and not the YouTube captions endpoint?**

  * Consistency: some videos lack official/auto captions or delay their availability.
  * Control: reproducible settings, higher‑accuracy models, offline processing, and full privacy.
  * Speed: GPU acceleration drastically reduces wall‑time for longform audio.

* **Two common, compatible ways to run Whisper on GPU:**

  **A. openai/whisper CLI**

  ```bash
  # examples: base | small | medium | large-v2
  whisper audio/<VIDEO_ID>.m4a \
    --model large-v2 --device cuda --fp16 True \
    --language en \
    --task transcribe \
    --output_dir outputs \
    --verbose False \
    --srt --vtt
  ```

  Produces: `.txt`, `.srt`, `.vtt`, and a segment TSV/JSON (depending on version/flags).

  **B. faster‑whisper (CTranslate2) – typically faster on GPU**

  ```bash
  pip install faster-whisper

  # single file
  faster-whisper-transcribe \
    --model large-v2 \
    --device cuda --compute_type float16 \
    --vad_filter True \
    --language en \
    --output_dir outputs \
    audio/<VIDEO_ID>.m4a
  ```

  Produces: `.txt`, `.srt`, `.vtt`; can also emit JSON depending on the wrapper used.

* **Settings used (recommended defaults for this corpus):**

  * **Model:** `medium` or `large-v2` (trade accuracy vs. VRAM/time)
  * **Device:** `cuda` with `--fp16` or `--compute_type float16` to use tensor cores
  * **VAD:** Enable voice‑activity detection to avoid transcribing long silences
  * **Language:** `--language en` to bypass auto‑detection
  * **Segments:** Export `.srt`/`.vtt` for timestamped alignment; optionally export segment JSON for research

### 4) Normalization, filenames, and alignment

* **Naming convention:**

  ```
  transcripts/<VIDEO_ID>.txt
  subtitles/<VIDEO_ID>.srt
  subtitles/<VIDEO_ID>.vtt
  json/<VIDEO_ID>.json    # optional, if you ask Whisper/FW to export JSON
  ```
* **Why `video_id` first?**

  * It’s stable and unique; titles can change.
  * Directly joinable with the catalog files (CSV/JSON), the HTML report, and any downstream database.&#x20;

### 5) Integrity checks & reproducibility

* **Hashing:** We recommend computing SHA‑256 for each transcript and storing alongside the metadata catalog to detect accidental edits.
* **Version capture:** Record Whisper/faster‑whisper versions, CUDA version, GPU model, and command‑line flags in a small `RUNLOG.md` per batch for auditability.
* **Determinism:** Re‑running Whisper can yield slight differences due to decoding randomness; fix a `--temperature`/`--beam_size` if you need stricter reproducibility.

---

## Data you can review right now

* **Channel‑wide HTML report** – an at‑a‑glance index with embed codes and direct links; confirms **43 videos** captured.&#x20;
* **Complete JSON catalog** – one object per video with the schema shown below; mirrors the fields demonstrated in our sample entries.&#x20;

  ```json
  {
    "title": "The 1948 Aztec, New Mexico UFO Crash Retrieval",
    "url": "https://www.youtube.com/watch?v=QJxbyu-9Tj0",
    "video_id": "QJxbyu-9Tj0",
    "embed_url": "https://www.youtube.com/embed/QJxbyu-9Tj0",
    "html_embed": "<iframe ... allowfullscreen></iframe>"
  }
  ```
* **CSV slice** – same info as the JSON, flat columns for quick filtering/sorting.
* **Per‑video transcripts** – `.txt` for reading, `.srt`/`.vtt` for time‑synchronized analysis, optional `.json` for segment research.

> The HTML and sample JSON/CSV validate the catalog structure (IDs, URLs, embed fields) this transcript set keys off of.

---

## Accuracy, limitations, and quality notes

* **Audio quality variation:** Whisper accuracy depends heavily on recording clarity, music/FX, and speaker pace.
* **Model choice:** `large-v2` is most accurate but VRAM‑hungry; `medium` is often a sweet spot for RTX‑class GPUs.
* **Timestamps:** `.srt`/`.vtt` give segment‑level alignment; word‑level timestamps require extra processing or JSON exports from certain wrappers.
* **Edge cases:** If a video lacks speech for long periods, VAD helps avoid hallucinated text.
* **Comparisons to YouTube captions:** Whisper can outperform auto‑captions; however, official uploaded captions (if present) may be cleaner for acronyms/terms of art.

---

## Reproducing the pipeline yourself

### Prereqs

* **GPU:** NVIDIA GPU with recent CUDA drivers
* **Tools:** `ffmpeg`, `yt-dlp`, Whisper or faster‑whisper
* **Python env:** any 3.9+ virtualenv/conda

### Minimal batch script (Bash)

```bash
# 1) Download audio for all video IDs listed in uap_gerb_complete_results.json
jq -r '.[].video_id' uap_gerb_complete_results.json | while read VID; do
  yt-dlp -f bestaudio[ext=m4a]/bestaudio -o "audio/${VID}.%(ext)s" "https://www.youtube.com/watch?v=${VID}"
done

# 2) Transcribe on GPU (faster-whisper example)
for A in audio/*.m4a; do
  VID=$(basename "$A" .m4a)
  faster-whisper-transcribe \
    --model large-v2 --device cuda --compute_type float16 \
    --vad_filter True --language en \
    --output_dir outputs "$A"
  mv outputs/${VID}.txt      transcripts/${VID}.txt
  mv outputs/${VID}.srt      subtitles/${VID}.srt
  mv outputs/${VID}.vtt      subtitles/${VID}.vtt
done
```

### Minimal batch (PowerShell)

```powershell
# 1) Download audio
(Get-Content uap_gerb_complete_results.json | ConvertFrom-Json).video_id | ForEach-Object {
  yt-dlp -f "bestaudio[ext=m4a]/bestaudio" `
    -o ("audio/{0}.%(ext)s" -f $_) `
    ("https://www.youtube.com/watch?v={0}" -f $_)
}

# 2) Transcribe (openai/whisper example)
Get-ChildItem audio\*.m4a | ForEach-Object {
  $vid = $_.BaseName
  whisper $_.FullName --model large-v2 --device cuda --fp16 True --language en --srt --vtt --output_dir outputs
  Move-Item outputs\$vid.txt transcripts\$vid.txt
  Move-Item outputs\$vid.srt subtitles\$vid.srt
  Move-Item outputs\$vid.vtt subtitles\$vid.vtt
}
```

---

## File tree (suggested layout)

```
.
├─ audio/                         # intermediate downloads (not committed)
├─ transcripts/                   # .txt per video_id
├─ subtitles/                     # .srt/.vtt per video_id
├─ json/                          # optional detailed per-segment exports
├─ uap_gerb_complete_results.json # full catalog for programmatic use  ⟵ :contentReference[oaicite:14]{index=14}
├─ uap_gerb_results.csv           # spreadsheet-friendly catalog
└─ uap_gerb_report.html           # human-readable channel index       ⟵ :contentReference[oaicite:15]{index=15}
```

---

## Provenance and auditability

* **Provenance chain:** YouTube video → `yt‑dlp` audio dump → GPU Whisper transcription → normalized transcripts → catalog cross‑reference (by `video_id`).
* **Verifying coverage:** Compare the set of `video_id` values in the JSON/CSV against filenames in `transcripts/` and `subtitles/`. Every `video_id` should have a matching `.txt` and `.srt/.vtt`. The HTML report can be used to spot‑check any missing title/ID.

---

## Ethics & usage

* **Intended use:** scholarship, research, indexing, and personal study.
* **Attribution:** Link back to the original YouTube videos and channel.
* **Fair use:** Long‑form transcripts may raise rights questions if redistributed wholesale. When publishing excerpts, cite the source and keep context.

---

## Known limitations & future improvements

* **Proper nouns/technical terms:** consider a custom glossary pass to correct recurring terms (batch find‑replace with a curated lexicon).
* **Word‑level timestamps:** export JSON with per‑token timing for deeper analysis.
* **Automation:** tie this repo to a GitHub Actions workflow that checks for new uploads hourly and runs the same Whisper steps on fresh audio.
* **Search:** index `.txt` content with Lunr/FlexSearch for zero‑cost full‑text search in a static site.

---

## Citation of source lists

* **Channel‑wide HTML report** (43 items, embed codes): used to confirm video count and provide human‑readable linking.&#x20;
* **Complete JSON catalog** (schema and fields): used as the programmatic map for `video_id`‑to‑file mapping and downstream joins.&#x20;

---

If you want, I can drop this into a `README.md` with a tidy file tree and add a tiny script to verify that every `video_id` in the catalog has a matching transcript and subtitle.
