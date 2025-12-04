# examples/live_plot.py
import time
from typing import List

import matplotlib.pyplot as plt

from spm002 import Spectrometer, SpectrometerConfig, SpectrumData, SpectrometerError


def get_x_axis(spectrum: SpectrumData) -> List[float]:
    """
    Decide which x-axis to use: wavelength if available, otherwise pixel index.
    """
    if spectrum.wavelengths is not None:
        return spectrum.wavelengths
    return [float(p) for p in spectrum.pixels]


def run_live_plot() -> None:
    """
    Connect to the spectrometer, configure it, and display a live spectrum.
    """
    config = SpectrometerConfig(
        device_index=0,
        exposure_ms=50.0,
        average=1,
        dark_subtraction=0,
        mode=0,
        scan_delay=0,
    )

    with Spectrometer(config=config) as spectrometer:
        # First acquisition to initialize the plot
        spectrum = spectrometer.acquire_spectrum()
        x = get_x_axis(spectrum)
        y = spectrum.counts

        plt.ion()
        fig, ax = plt.subplots()
        (line,) = ax.plot(x, y)

        if spectrum.wavelengths is not None:
            ax.set_xlabel("Wavelength [nm]")
        else:
            ax.set_xlabel("Pixel")

        ax.set_ylabel("Counts")
        ax.set_title(
            f"Live spectrum (Device {config.device_index}, "
            f"{config.exposure_ms:.1f} ms, avg={config.average})"
        )

        fig.tight_layout()
        fig.canvas.draw()
        fig.canvas.flush_events()

        print("Starting live acquisition... (close the window or press Ctrl+C to stop)")

        try:
            while plt.fignum_exists(fig.number):
                spectrum = spectrometer.acquire_spectrum()
                line.set_ydata(spectrum.counts)

                ax.relim()
                ax.autoscale_view()

                fig.canvas.draw()
                fig.canvas.flush_events()

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nLive plot interrupted by user.")

        print("Live plot finished.")


def main() -> None:
    try:
        run_live_plot()
    except SpectrometerError as exc:
        print(f"Spectrometer error: {exc}")


if __name__ == "__main__":
    main()
