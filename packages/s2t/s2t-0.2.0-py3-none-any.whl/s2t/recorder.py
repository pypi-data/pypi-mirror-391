from __future__ import annotations

import os
import queue
import select
import sys
import threading
import time
from pathlib import Path
from typing import Any, Protocol, cast, runtime_checkable

import numpy as np

from .utils import debug_log


class Recorder:
    def __init__(
        self,
        session_dir: Path,
        samplerate: int,
        channels: int,
        ext: str,
        debounce_ms: int = 0,
        verbose: bool = False,
        pause_after_first_chunk: bool = False,
        resume_event: threading.Event | None = None,
        silence_sec: float = 1.0,
        min_chunk_sec: float = 5.0,
        buffer_sec: float = 30.0,
    ) -> None:
        self.session_dir = session_dir
        self.samplerate = samplerate
        self.channels = channels
        self.ext = ext
        self.debounce_ms = max(0, int(debounce_ms))
        self.verbose = verbose
        self.pause_after_first_chunk = pause_after_first_chunk
        self.resume_event = resume_event
        self._paused = False
        # Auto-split config
        self.silence_sec = max(0.0, float(silence_sec))
        self.min_chunk_sec = max(0.0, float(min_chunk_sec))
        # Observation window for future block-based splitting (longest pause within window)
        self.buffer_sec = max(0.0, float(buffer_sec))

    def run(
        self,
        tx_queue: queue.Queue[tuple[int, Path, int, float, str]],
    ) -> tuple[list[Path], list[int], list[float]]:
        import platform
        import termios
        import tty

        try:
            import sounddevice as sd
            import soundfile as sf
        except Exception as e:
            raise RuntimeError("sounddevice/soundfile required for recording.") from e

        evt_q: queue.Queue[str] = queue.Queue()
        # Control queue is separate from audio frames to avoid control backpressure.
        ctrl_q: queue.Queue[str] = queue.Queue()
        stop_evt = threading.Event()

        def key_reader() -> None:
            try:
                if platform.system() == "Windows":
                    import msvcrt

                    @runtime_checkable
                    class _MSVCRT(Protocol):
                        def kbhit(self) -> int: ...
                        def getwch(self) -> str: ...

                    ms = cast(_MSVCRT, msvcrt)

                    last_space = 0.0
                    debug_log(self.verbose, "recorder", "Key input: using msvcrt (Windows)")
                    while not stop_evt.is_set():
                        if ms.kbhit():
                            ch = ms.getwch()
                            if ch in ("\r", "\n"):
                                debug_log(self.verbose, "recorder", "Key input: ENTER")
                                evt_q.put("ENTER")
                                break
                            if ch == " ":
                                now = time.perf_counter()
                                if self.debounce_ms and (now - last_space) < (
                                    self.debounce_ms / 1000.0
                                ):
                                    continue
                                last_space = now
                                debug_log(self.verbose, "recorder", "Key input: SPACE")
                                evt_q.put("SPACE")
                        time.sleep(0.01)
                else:
                    # Prefer sys.stdin when it's a TTY (original, proven path). If not a TTY, try /dev/tty, else fallback to stdin line reads.
                    try:
                        if sys.stdin.isatty():
                            fd = sys.stdin.fileno()
                            debug_log(
                                self.verbose, "recorder", "Key input: using sys.stdin (TTY fd read)"
                            )
                            old = termios.tcgetattr(fd)
                            tty.setcbreak(fd)
                            last_space = 0.0
                            try:
                                while not stop_evt.is_set():
                                    r, _, _ = select.select([fd], [], [], 0.05)
                                    if r:
                                        try:
                                            ch_b = os.read(fd, 1)
                                        except BlockingIOError:
                                            continue
                                        if not ch_b:
                                            continue
                                        ch = ch_b.decode(errors="ignore")
                                        if ch in ("\n", "\r"):
                                            debug_log(self.verbose, "recorder", "Key input: ENTER")
                                            evt_q.put("ENTER")
                                            break
                                        if ch == " ":
                                            now = time.perf_counter()
                                            if self.debounce_ms and (now - last_space) < (
                                                self.debounce_ms / 1000.0
                                            ):
                                                continue
                                            last_space = now
                                            debug_log(self.verbose, "recorder", "Key input: SPACE")
                                            evt_q.put("SPACE")
                            finally:
                                termios.tcsetattr(fd, termios.TCSADRAIN, old)
                        else:
                            # Try /dev/tty when stdin is not a TTY
                            using_devtty = False
                            fd = None
                            try:
                                fd = os.open("/dev/tty", os.O_RDONLY)
                                using_devtty = True
                                debug_log(
                                    self.verbose,
                                    "recorder",
                                    "Key input: using /dev/tty (stdin not TTY)",
                                )
                                old = termios.tcgetattr(fd)
                                tty.setcbreak(fd)
                                last_space = 0.0
                                try:
                                    while not stop_evt.is_set():
                                        r, _, _ = select.select([fd], [], [], 0.05)
                                        if r:
                                            ch_b = os.read(fd, 1)
                                            if not ch_b:
                                                continue
                                            ch = ch_b.decode(errors="ignore")
                                            if ch in ("\n", "\r"):
                                                debug_log(
                                                    self.verbose, "recorder", "Key input: ENTER"
                                                )
                                                evt_q.put("ENTER")
                                                break
                                            if ch == " ":
                                                now = time.perf_counter()
                                                if self.debounce_ms and (now - last_space) < (
                                                    self.debounce_ms / 1000.0
                                                ):
                                                    continue
                                                last_space = now
                                                debug_log(
                                                    self.verbose, "recorder", "Key input: SPACE"
                                                )
                                                evt_q.put("SPACE")
                                finally:
                                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
                            except Exception:
                                if using_devtty and fd is not None:
                                    try:
                                        os.close(fd)
                                    except Exception:
                                        pass
                                print(
                                    "Warning: no TTY for key input; falling back to stdin line mode.",
                                    file=sys.stderr,
                                )
                                # Last resort: line-buffered stdin; Enter will still end.
                                while not stop_evt.is_set():
                                    line = sys.stdin.readline()
                                    if not line:
                                        time.sleep(0.05)
                                        continue
                                    # If user hits Enter on empty line, treat as ENTER
                                    if line == "\n" or line == "\r\n":
                                        debug_log(
                                            self.verbose, "recorder", "Key input: ENTER (line mode)"
                                        )
                                        evt_q.put("ENTER")
                                        break
                                    # If first non-empty char is space, treat as SPACE
                                    if line and line[0] == " ":
                                        debug_log(
                                            self.verbose, "recorder", "Key input: SPACE (line mode)"
                                        )
                                        evt_q.put("SPACE")
                    except Exception as e:
                        print(f"Warning: key reader failed: {e}", file=sys.stderr)

            except Exception as e:
                # Log unexpected key reader errors to aid debugging, but keep recording running.
                print(f"Warning: key reader stopped unexpectedly: {e}", file=sys.stderr)

        # Unbounded audio queue to avoid drops on slower machines; control signals are separate.
        audio_q: queue.Queue[tuple[str, Any]] = queue.Queue()
        chunk_index = 1
        chunk_paths: list[Path] = []
        chunk_frames: list[int] = []
        chunk_offsets: list[float] = []
        offset_seconds_total = 0.0

        def writer_fn() -> None:
            nonlocal chunk_index, offset_seconds_total
            # Internal thresholds and analysis params
            threshold_rms = 0.015  # conservative RMS threshold for float32 [-1,1]
            window_frames = (
                int(round(self.buffer_sec * self.samplerate)) if self.buffer_sec > 0 else 0
            )

            # In-memory buffer since last cut
            buf_raw: list[Any] = []  # list of ndarray chunks
            buf_meta: list[tuple[int, bool]] = []  # (frames, is_silent) per chunk
            buf_len_frames = 0

            def _emit_chunk(frames_to_write: int, cause: str) -> None:
                nonlocal chunk_index, offset_seconds_total, buf_raw, buf_meta, buf_len_frames
                if frames_to_write <= 0:
                    return
                cur_path = self.session_dir / f"chunk_{chunk_index:04d}{self.ext}"
                fh = sf.SoundFile(
                    str(cur_path), mode="w", samplerate=self.samplerate, channels=self.channels
                )
                frames_left = frames_to_write
                new_buf_raw: list[Any] = []
                new_buf_meta: list[tuple[int, bool]] = []
                # Write from head of buffer up to frames_to_write; keep remainder in new buffer
                for arr, (n, is_silent) in list(zip(buf_raw, buf_meta, strict=False)):
                    if frames_left <= 0:
                        new_buf_raw.append(arr)
                        new_buf_meta.append((n, is_silent))
                        continue
                    if n <= frames_left:
                        fh.write(arr)
                        frames_left -= n
                        # drop this chunk from buffer
                        continue
                    # Partial consume
                    fh.write(arr[:frames_left])
                    remainder = arr[frames_left:]
                    rem_n = n - frames_left
                    new_buf_raw.append(remainder)
                    new_buf_meta.append((rem_n, is_silent))
                    frames_left = 0
                fh.flush()
                fh.close()

                written = frames_to_write - frames_left
                if written > 0:
                    dur = written / float(self.samplerate)
                    chunk_paths.append(cur_path)
                    chunk_frames.append(written)
                    chunk_offsets.append(offset_seconds_total)
                    offset_seconds_total += dur
                    debug_log(
                        self.verbose,
                        "recorder",
                        f"Saved chunk {chunk_index}: {cur_path.name} ({dur:.2f}s)",
                    )
                    tx_queue.put((chunk_index, cur_path, written, chunk_offsets[-1], cause))
                    debug_log(
                        self.verbose,
                        "recorder",
                        f"Enqueued chunk {chunk_index} for transcription (cause={cause})",
                    )
                else:
                    try:
                        cur_path.unlink(missing_ok=True)
                    except Exception:
                        pass
                # Update buffer to remainder
                buf_raw = new_buf_raw
                buf_meta = new_buf_meta
                buf_len_frames = sum(n for (n, _b) in buf_meta)
                chunk_index += 1
                if (
                    self.pause_after_first_chunk
                    and chunk_index == 2
                    and self.resume_event is not None
                ):
                    self._paused = True
                    debug_log(
                        self.verbose,
                        "recorder",
                        "Paused after first chunk; waiting for resume (prompt mode)",
                    )
                    self.resume_event.wait()
                    self._paused = False
                    debug_log(self.verbose, "recorder", "Resumed after prompt")

            def _analyze_and_cut_if_window_full() -> None:
                if window_frames <= 0:
                    return
                if buf_len_frames < window_frames:
                    return
                # Determine longest silent run within the first window_frames starting at buffer start
                longest_len = -1
                longest_end_at = 0
                pos = 0
                start_run = None
                run_len = 0
                considered = 0
                for n, is_silent in buf_meta:
                    take = min(n, max(0, window_frames - considered))
                    if take <= 0:
                        break
                    if is_silent:
                        if start_run is None:
                            start_run = pos
                            run_len = take
                        else:
                            run_len += take
                    else:
                        if start_run is not None and run_len > longest_len:
                            longest_len = run_len
                            longest_end_at = pos
                        start_run = None
                        run_len = 0
                    pos += take
                    considered += take
                # Close trailing run
                if considered >= window_frames and start_run is not None and run_len > longest_len:
                    longest_len = run_len
                    longest_end_at = pos

                # Decide cut position
                min_front = int(self.min_chunk_sec * self.samplerate)
                min_pause = int(self.silence_sec * self.samplerate) if self.silence_sec > 0 else 0
                if longest_len > 0 and (min_pause == 0 or longest_len >= min_pause):
                    # Cut at middle of longest silent run
                    cut_pos = longest_end_at - (longest_len // 2)
                    if cut_pos < min_front:
                        cut_pos = max(min_front, min(window_frames, cut_pos))
                else:
                    # No silence in window -> hard cut at window end
                    cut_pos = window_frames
                # Ensure lower bound
                cut_pos = max(min_front, cut_pos)
                _emit_chunk(cut_pos, "pause")

            while True:
                # First, handle any pending control commands so SPACE/ENTER are never blocked by frames backlog.
                try:
                    while True:
                        cmd = ctrl_q.get_nowait()
                        if cmd == "split_manual":
                            # Manual split: cut everything currently buffered
                            _emit_chunk(buf_len_frames, "space")
                        elif cmd == "finish":
                            # Emit any remaining audio as final chunk
                            if buf_len_frames > 0:
                                _emit_chunk(buf_len_frames, "finish")
                            tx_queue.put((-1, Path(), 0, 0.0, ""))
                            debug_log(self.verbose, "recorder", "Signaled transcription finish")
                            return
                except queue.Empty:
                    pass

                # Then, read frames if available; short timeout to re-check control queue regularly.
                try:
                    kind, payload = audio_q.get(timeout=0.05)
                except queue.Empty:
                    continue
                if kind == "frames":
                    data = payload
                    # Append to in-memory buffer
                    try:
                        arr = np.asarray(data, dtype=np.float32)
                        if arr.ndim == 2 and arr.shape[1] > 1:
                            arr_mono = arr.mean(axis=1)
                        else:
                            arr_mono = arr.reshape(-1)
                        rms = float(np.sqrt(np.mean(np.square(arr_mono)))) if arr_mono.size else 0.0
                    except Exception:
                        rms = 0.0
                    is_silent = bool(rms < threshold_rms)
                    nframes = len(arr_mono) if 'arr_mono' in locals() else len(data)
                    buf_raw.append(data)
                    buf_meta.append((nframes, is_silent))
                    buf_len_frames += nframes
                    # If we have a full window, analyze and cut at the best pause
                    _analyze_and_cut_if_window_full()
            tx_queue.put((-1, Path(), 0, 0.0, ""))

        def cb(indata: Any, frames: int, time_info: Any, status: Any) -> None:
            if status:
                print(status, file=sys.stderr)
            if not self._paused:
                audio_q.put(("frames", indata.copy()))

        key_t = threading.Thread(target=key_reader, daemon=True)
        writer_t = threading.Thread(target=writer_fn, daemon=True)
        key_t.start()
        writer_t.start()

        msg = "Recording… Press SPACE to split, Enter to finish."
        if self.buffer_sec > 0.0:
            msg += f" Block mode: analyze {self.buffer_sec:.0f}s window, cut at longest pause (min {self.min_chunk_sec:.2f}s)."
        elif self.silence_sec > 0.0:
            msg += (
                f" Auto-split on ≥{self.silence_sec:.2f}s silence (min {self.min_chunk_sec:.2f}s)."
            )
        print(msg)
        print("—" * 60)
        print("")

        debug_log(
            self.verbose,
            "recorder",
            f"Recording started (rate={self.samplerate}, channels={self.channels}, ext={self.ext})",
        )

        import sounddevice as sd

        with sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=cb):
            while True:
                try:
                    evt = evt_q.get(timeout=0.05)
                except queue.Empty:
                    continue
                if evt == "SPACE":
                    ctrl_q.put("split_manual")
                elif evt == "ENTER":
                    ctrl_q.put("finish")
                    break
        writer_t.join()
        debug_log(self.verbose, "recorder", "Recording finished")
        return chunk_paths, chunk_frames, chunk_offsets
