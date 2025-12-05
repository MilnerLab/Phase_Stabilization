# phase_control/analysis/plot.py
import time
import threading

import numpy as np
import matplotlib.pyplot as plt

from base_lib.models import Angle
from phase_control.analysis.config import AnalysisConfig
from phase_control.analysis.phase_corrector import PhaseCorrector
from phase_control.analysis.phase_tracker import PhaseTracker
from phase_control.correction_io.elliptec_ell14 import ElliptecRotator
from phase_control.domain.plotting import plot_model, plot_spectrogram
from phase_control.stream_io import StreamMeta, FrameBuffer


def run_analysis(
    buffer: FrameBuffer,
    stop_event: threading.Event,
) -> None:
    
    config = AnalysisConfig()
    phase_tracker = PhaseTracker(config)
    phase_corrector = PhaseCorrector()
    ell = ElliptecRotator()
    
    # Matplotlib setup
    plt.ion()
    fig, ax = plt.subplots()
    fig.tight_layout()
    fig.canvas.draw()
    fig.canvas.flush_events()

    try:
        while True:
            current_spectrum = buffer.get_latest()
            if current_spectrum is None:
                # No data yet, avoid busy-wait
                time.sleep(0.01)
                continue
            
            phase_tracker.update(current_spectrum)
    
            if phase_tracker.current_phase is not None:
                delta = phase_corrector.update(phase_tracker.current_phase)
            else:
                delta = Angle(0)
                
            ell.rotate(delta)
            
            plot_spectrogram(ax, current_spectrum)
            plot_model(ax, current_spectrum.wavelengths_nm, phase_tracker._config)
            
            ax.relim()
            ax.autoscale_view()

            fig.canvas.draw()
            fig.canvas.flush_events()
            time.sleep(0.02)
            

    except KeyboardInterrupt:
        print("\nLive plot interrupted by user.")
    finally:
        print("Live plot finished.")
        