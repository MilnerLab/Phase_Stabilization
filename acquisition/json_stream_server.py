# acquisition/json_stream_server.py
import json
import time

from .spm002 import Spectrometer, SpectrometerConfig, SpectrumData


def spectrum_to_frame(spectrum: SpectrumData) -> dict:
    return {
        "type": "frame",
        "timestamp": spectrum.timestamp.isoformat(),
        "device_index": spectrum.device_index,
        "counts": spectrum.counts,
        # wavelengths are static → we send them once in the meta message
    }


def main() -> None:
    """
    Simple streaming server:
    - opens the spectrometer
    - sends one meta JSON object
    - then sends frames as JSON lines (one per spectrum) to stdout

    This script is intended to be started by a 64-bit Python process
    via subprocess, so that the data can be analyzed in a 64-bit environment.
    """
    config = SpectrometerConfig()

    with Spectrometer(config=config) as spectrometer:
        # Acquire one spectrum to get static info
        first = spectrometer.acquire_spectrum()

        meta = {
            "type": "meta",
            "device_index": first.device_index,
            "num_pixels": len(first),
            "wavelengths": first.wavelengths,  # may be None
            "exposure_ms": first.exposure_ms,
            "average": first.average,
            "dark_subtraction": first.dark_subtraction,
        }

        # Send meta as first line
        print(json.dumps(meta), flush=True)

        # Then stream frames
        while True:
            spectrum = spectrometer.acquire_spectrum()
            frame = spectrum_to_frame(spectrum)
            print(json.dumps(frame), flush=True)
            # Adjust loop speed if needed; if exposure dominates, you can set this to 0
            time.sleep(0.0)


if __name__ == "__main__":
    main()
