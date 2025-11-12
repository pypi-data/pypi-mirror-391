# s2t

Record audio from your microphone, run Whisper to transcribe it, export common formats, and optionally copy the transcript to your clipboard.

## Install
- From local checkout:
  - Editable: `pip install -e .`
  - Standard: `pip install .`

Requirements: Python 3.11–3.12. No mandatory external binaries. ffmpeg is optional (only for MP3 encoding/decoding).

System requirements (Linux)
- Some environments need system libraries for audio I/O:
  - Debian/Ubuntu: `sudo apt-get install libportaudio2 libsndfile1`
  - Fedora/RHEL: `sudo dnf install portaudio libsndfile`
- Optional for MP3: ffmpeg (`sudo apt-get install ffmpeg` or `brew install ffmpeg`).
 - Optional backends:
   - faster-whisper (CTranslate2): `pip install faster-whisper` (GPU via CUDA on NVIDIA; CPU works well with int8).
   - whisper.cpp (Metal/CPU): `pip install whispercpp` (requires local gguf models; experimental GPU on Apple varies by build).

## Usage
- Start interactive recording and transcribe:
  - `s2t`
- Short options:
  - Language: `-l de` (long: `--lang de`)
  - Model: `-m large-v3` (long: `--model large-v3`)
  - Backend: `--backend whisper|faster|whispercpp` (default: `whisper`)
  - Device: `--device auto|cpu|cuda|mps` (default: `auto`)
  - Sample rate: `-r 48000` (long: `--rate 48000`)
  - Channels: `-c 2` (long: `--channels 2`)
  - Output dir: `-o transcripts` (long: `--outdir transcripts`) — default is `transcripts/` if omitted
  - Translate to English: `-t` (long: `--translate`). You may still provide `--lang` as an input-language hint if you want.
  - List available models and exit: `-L` (long: `--list-models`)
  - Recording format: `-f flac|wav|mp3` (long: `--recording-format`), default `flac`. MP3 requires ffmpeg; if absent, it falls back to FLAC with a warning.
  - Note: There is no minimum chunk duration; cuts are chosen at the longest pause within the window.
  - Observation window (for block-based splitting): `-b 20.0` or `--buffer-sec 20.0` (default `20.0`). Cuts at the longest pause within each window.
  - Prompt mode (spoken prompt): `-p` (long: `--prompt`). Speak your prompt first, then press SPACE to use it as prompt and continue with your main content. If you press ENTER instead of SPACE, no prompt is used; the spoken audio is transcribed as normal payload and the session ends.
  - Keep chunk files: `--keep-chunks` — by default, per‑chunk audio and per‑chunk Whisper outputs are deleted after the final merge.
  - Open transcript for editing: `-e` (long: `--edit`) — opens the generated `.txt` in your shell editor (`$VISUAL`/`$EDITOR`).
- Examples:
  - Transcribe in German using large-v3: `s2t -l de -m large-v3`
  - Translate any input to English: `s2t -t`
  - Write outputs under transcripts/: `s2t -o transcripts`
  - List local model names: `s2t -L`

## Interactive Controls
- Key bindings (while recording)
  - ENTER: Split now (manual cut). Ends the current segment immediately.
  - Q (or q): Finish the session and process final outputs.
  - c (lowercase): Copy the recent transcript to the clipboard since the last c or C action. Prints a visible console marker.
  - C (uppercase): Copy the full transcript (since the beginning) to the clipboard. Prints a distinct console marker.
  - SPACE: Reserved for future features (no action for now).
- Prompt mode (`-p/--prompt`)
  - Speak your prompt first, then press ENTER. The app waits until your prompt is transcribed, prints a separator, and then you start speaking your main content.

## Segmentation Behavior
- Windowed splitting (default): The recorder analyzes a sliding window of length `--buffer-sec` (default `20` seconds) and cuts at the longest detected pause.
  - If no suitable pause is found within the window, a hard cut occurs at the window boundary.
  - A small audio overlap (`--overlap-ms`, default `200`) is applied between consecutive segments to avoid trimming syllables at cut points.

Outputs are written into a timestamped folder under the chosen output directory (default is `transcripts/`), e.g. `transcripts/2025-01-31T14-22-05+0200/`, containing:
- Per‑chunk outputs: `chunk_####.flac/.wav` plus `chunk_####.txt/.srt/.vtt/.tsv/.json` (deleted by default unless `--keep-chunks`)
- Final outputs: `recording.flac/.wav` (and `recording.mp3` if requested and ffmpeg available), plus `recording.txt/.srt/.vtt/.tsv/.json`
  - Transcript is written to `.txt`; clipboard copying is optional and disabled by default.

Auto-splitting details
- ENTER splits immediately; Q finishes the recording.
- Windowed: cuts at the longest pause within the selected window (fallback: window boundary).
- There is no fixed minimum duration per chunk.

## Makefile (optional)
- Setup venv + dev deps: `make setup`
- Lint/format/test: `make lint`, `make format`, `make test`; combined gate: `make check`
- Build sdist/wheel: `make build` (runs `check` first)
- Publish to PyPI/TestPyPI: `make publish`, `make publish-test` (run after `build`)
- Run CLI: `make record ARGS='-l de -t -o transcripts'`
- List models: `make list-models`
- Show package version: `make version`

Notes on models
- The local openai-whisper CLI supports models like: `tiny`, `base`, `small`, `medium`, `large-v1`, `large-v2`, `large-v3` and their `.en` variants.
- The name `turbo` refers to OpenAI’s hosted model family and is not provided by the local `whisper` CLI. If you pass `-m turbo`, the command may fail; choose a supported local model instead.

## Development & Release
- For developer setup and contribution guidelines, see `CONTRIBUTING.md`.
- For the release process, see `docs/RELEASING.md`.
