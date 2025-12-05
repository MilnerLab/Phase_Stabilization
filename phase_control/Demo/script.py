from pathlib import Path
from matplotlib import pyplot as plt

from base_lib.models import Length, Prefix, Range
from phase_control.Demo.data_io.data_loader import load_spectra
from phase_control.analysis.config import AnalysisConfig
from phase_control.analysis.phase_tracker import PhaseTracker
from phase_control.domain.models import Spectrum
from phase_control.domain.plotting import plot_model, plot_phase, plot_spectrogram


config = AnalysisConfig()

path = Path("Z:\\Droplets\\20251120\\Spectra_GA=26_DA=15p9\\spectrum-20-Nov-2025_121750 - both arms 10ms.txt")

spectra = load_spectra(path)
spectra_cut = [s.cut(config.wavelength_range) for s in spectra]

phase_tracker = PhaseTracker(config)
phases = []

for s in spectra:
    phase_tracker.update(s)
    # phase_correcter(phase_tracker.current_phase)
    phases.append(phase_tracker.current_phase)

fig, ax = plt.subplots(figsize=(8, 4))
#plot_spectrogram(ax, spectra_cut[0])
#plot_model(ax, spectra_cut[0], phase_tracker._config)
plot_phase(ax, phases)
fig.tight_layout()
plt.show()


