# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog, and the project aims to follow Semantic Versioning.

## [0.2.0] - 2025-11-11

### Added
- Windowed splitting in the Recorder: collect an observation window (default 30 s) and cut at the midpoint of the longest pause within the window.
- New CLI option `--buffer-sec` (default: `30.0`) to configure the observation window length.

### Changed
- Default splitting behavior now uses the windowed approach. If no suitable pause is found in the window, perform a hard cut at the window end.
- Start message clarifies the active mode; there is no minimum chunk duration anymore.

### Preserved
- Manual split with SPACE; ENTER still finishes recording.

### Documentation
- README mentions the new `--buffer-sec` option and the block-based splitting.

## [0.1.x] - 2025-10-xx
- Initial public series with interactive recording, silence-based auto-split, Whisper transcription, and basic outputs.

[0.2.0]: https://github.com/yaccob/transcriber/releases/tag/v0.2.0
## [Unreleased]

### Added
- Windowed splitting is the default segmentation mode; cuts at the longest pause within `--buffer-sec` (default 20s).
- Short option `-b` for `--buffer-sec`.
- Audio overlap between segments via `--overlap-ms` (default 200 ms) to avoid losing syllables at cut points.
- Clipboard hotkeys during recording:
  - `c` (lowercase): copy recent transcript since the last `c` or `C`, with a visible console marker.
  - `C` (uppercase): copy the full transcript from the beginning, with a distinct console marker.
- Live recording indicator: indented console line when the audio stream becomes active (not part of the transcript).

### Changed
- Key bindings: ENTER splits immediately; Q/q finishes the session. SPACE reserved for future use.
- Start banner condensed to one informative line including the analysis window.
- Prompt mode instructions updated to use ENTER.
- README: interactive controls documented; clipboard behavior described as optional (disabled by default).
- CLI output labels: use "Transcript:" and print transcript file name instead of implying clipboard copying by default.

### Removed
- `--min-chunk-sec` option and related logic.
- `--silence-sec` option and related logic.

### Fixed
- Final-chunk recognition: be lenient for the last segment (increase trim pad; do not discard short voiced final audio), preventing dropped last words and spurious ellipses.
- Clipboard recent-copy marker now resets on `C` as well, so a following `c` copies from the last `c` or `C`.

### Internal
- AGENTS.md: enforce English-only policy for public artifacts.
- AGENTS.md: commit discipline guidelines (review staged diff; accurate Conventional Commits).
