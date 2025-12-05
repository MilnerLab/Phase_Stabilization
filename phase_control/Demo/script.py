from pathlib import Path
from matplotlib import pyplot as plt

from base_lib.models import Length, Prefix, Range
from phase_control.Demo.data_io.data_loader import load_spectra
from phase_control.analysis.config import AnalysisConfig
from phase_control.analysis.phase_tracker import PhaseTracker
from phase_control.domain.models import Spectrum
from phase_control.domain.plotting import plot_model, plot_spectrogram


config = AnalysisConfig()

path = Path("Z:\\Droplets\\20251120\\Spectra_GA=26_DA=15p9\\spectrum-20-Nov-2025_121750 - both arms 10ms.txt")

spectra = load_spectra(path)

def cut(range_wl: Range, spectrum: Spectrum):
    wave = []
    intensity = []
    for i in range(len(spectrum.wavelengths)):
        if range_wl.is_in_range(spectrum.wavelengths[i]):
            wave.append(spectrum.wavelengths[i])
            intensity.append(spectrum.intensity[i])
            
    return Spectrum(wave, intensity)
        
spectra_cut = [cut(config.wavelength_range, s) for s in spectra]
'''
phase_correcter = PhaseCorrector(config)
phases = []

for s in spectra:
    phase_correcter.update(s)
    phases.append(phase_correcter.current_phase)
'''
fig, ax = plt.subplots(figsize=(8, 4))
plot_spectrogram(ax, spectra_cut[0])
plot_model(ax, spectra_cut[0], config)

fig.tight_layout()
plt.show()


