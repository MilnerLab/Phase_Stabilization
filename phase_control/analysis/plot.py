# phase_control/analysis/plot.py
import threading
import queue
from typing import List

import numpy as np
import matplotlib.pyplot as plt

from phase_control.stream_io.stream_client import SpectrometerStreamClient, StreamFrame



def _reader_worker(
    client: SpectrometerStreamClient,
    frame_queue: "queue.Queue[StreamFrame]",
    stop_event: threading.Event,
    max_queue_size: int = 10,
) -> None:
    """
    Background worker that reads frames from the stream client and pushes them
    into a queue for the main thread to process.

    If the queue is full, the oldest frame is dropped to stay close to real time.
    """
    try:
        for frame in client.frames():
            if stop_event.is_set():
                break

            try:
                # Try to put without blocking too long
                frame_queue.put(frame, timeout=0.1)
            except queue.Full:
                # Drop the oldest frame and try again
                try:
                    frame_queue.get_nowait()
                except queue.Empty:
                    pass
                try:
                    frame_queue.put_nowait(frame)
                except queue.Full:
                    # If it's still full, drop this frame as well
                    pass
    except Exception:
        # In a real app you'd log this somewhere
        pass
    finally:
        stop_event.set()


def run_plot() -> None:
    """
    Start the 32-bit acquisition process, receive spectra via the stream client,
    and display a live plot using 64-bit NumPy/Matplotlib.

    Reading from the acquisition process runs in a background thread.
    Analysis + plotting run in the main thread.
    """
    with SpectrometerStreamClient() as client:
        meta = client.meta

        # X axis
        if meta.wavelengths is not None:
            x = np.array(meta.wavelengths, dtype=float)
            x_label = "Wavelength [nm]"
        else:
            x = np.arange(meta.num_pixels, dtype=float)
            x_label = "Pixel"

        # Matplotlib setup (main thread)
        plt.ion()
        fig, ax = plt.subplots()

        y0 = np.zeros_like(x)
        (line,) = ax.plot(x, y0)

        ax.set_xlabel(x_label)
        ax.set_ylabel("Counts")
        ax.set_title(
            f"Live spectrum (Device {meta.device_index}, "
            f"{meta.exposure_ms:.1f} ms, avg={meta.average})"
        )

        fig.tight_layout()
        fig.canvas.draw()
        fig.canvas.flush_events()

        print("Live acquisition started (close the window or press Ctrl+C to stop).")

        # Queue + worker thread for incoming frames
        frame_queue: "queue.Queue[StreamFrame]" = queue.Queue(maxsize=10)
        stop_event = threading.Event()

        reader_thread = threading.Thread(
            target=_reader_worker,
            args=(client, frame_queue, stop_event),
            daemon=True,
        )
        reader_thread.start()

        try:
            while not stop_event.is_set() and plt.fignum_exists(fig.number):
                try:
                    # Wait for next frame from background thread
                    frame = frame_queue.get(timeout=0.2)
                except queue.Empty:
                    # No new data in this interval → just continue
                    continue

                # -------- YOUR HEAVY ANALYSIS GOES HERE --------
                # Basic example: just convert counts to float array
                y = np.array(frame.counts, dtype=float)

                # TODO: replace / extend with your own analysis
                # e.g. filtered_y = my_fft_analysis(y)

                # -------- PLOTTING (must stay in main thread) --------
                if y.size != x.size:
                    # Safety check: unexpected size mismatch
                    continue

                line.set_ydata(y)
                ax.relim()
                ax.autoscale_view()

                fig.canvas.draw()
                fig.canvas.flush_events()

        except KeyboardInterrupt:
            print("\nLive plot interrupted by user.")
        finally:
            # Signal the worker to stop and wait a bit for clean exit
            stop_event.set()
            reader_thread.join(timeout=2.0)

        print("Live plot finished.")
        plt.ioff()
        plt.show()


def main() -> None:
    run_plot()


if __name__ == "__main__":
    main()
