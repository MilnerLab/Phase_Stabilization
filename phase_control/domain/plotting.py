from ast import List
from dataclasses import asdict
from typing import Optional
from matplotlib.axes import Axes

from base_lib.functions import usCFG_projection
from base_lib.models import Angle, Length, Prefix
from phase_control.analysis.config import AnalysisConfig, FitParameter
from phase_control.domain.models import Spectrum

def plot_spectrogram(ax: Axes, spec: Spectrum, label: Optional[str] = None) -> None:
    
    wavelengths_nm = [w.value(Prefix.NANO) for w in spec.wavelengths]

    ax.plot(wavelengths_nm, spec.intensity, label=label)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Normalized intensity (a.u.)")

    if label is not None:
        ax.legend()

def plot_model(ax: Axes, wavelengths_nm: list[float], fit_params: FitParameter, label: Optional[str] = None) -> None:
    
    y =usCFG_projection(wavelengths_nm, **fit_params.to_fit_kwargs(usCFG_projection))
    ax.plot(wavelengths_nm, y, label=label)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Normalized intensity (a.u.)")

    if label is not None:
        ax.legend()
        
def plot_phase(ax: Axes, phases: list[Angle], label: Optional[str] = None) -> None:
    ax.plot(phases, label=label)
    ax.set_xlabel("Scan")
    ax.set_ylabel("Phase Angle (rad)")

    if label is not None:
        ax.legend()