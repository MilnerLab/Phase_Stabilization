# app.py (im Repo-Root, x64 side)
import threading

from phase_control.analysis.config import AnalysisConfig
from phase_control.analysis.run_analysis import AnalysisEngine
from phase_control.stream_io import (
    SpectrometerStreamClient,
    FrameBuffer,
    StreamMeta,
)
from phase_control.ui.main_window import run_main_window


def reader_loop(
    client: SpectrometerStreamClient,
    buffer: FrameBuffer,
    stop_event: threading.Event,
) -> None:
    """
    Background thread:

    - consumes frames from the SpectrometerStreamClient
    - updates the FrameBuffer with the latest frame
    - exits when stop_event is set or the stream ends
    """
    try:
        for frame in client.frames():
            if stop_event.is_set():
                break
            buffer.update(frame)
    finally:
        client.stop()


def main() -> None:
    """
    x64 side entry point:

    - start 32-bit acquisition subprocess via SpectrometerStreamClient
    - create the shared AnalysisConfig instance
    - create FrameBuffer + AnalysisEngine
    - start a reader thread
    - run the Tk main window (tabs) in the main thread
    """
    client = SpectrometerStreamClient()
    meta: StreamMeta = client.start()

    buffer = FrameBuffer(meta)
    config = AnalysisConfig()
    engine = AnalysisEngine(config=config, buffer=buffer)

    stop_event = threading.Event()

    reader = threading.Thread(
        target=reader_loop,
        args=(client, buffer, stop_event),
        name="SpectrometerReaderThread",
        daemon=True,
    )
    reader.start()

    try:
        run_main_window(config=config, engine=engine, stop_event=stop_event)
    finally:
        stop_event.set()
        reader.join(timeout=2.0)
        client.stop()


if __name__ == "__main__":
    main()
