from __future__ import annotations 
from dataclasses import dataclass

import numpy as np

from base_lib.models import Length, Prefix

@dataclass
class Spectrum:
    wavelengths: list[Length]
    intensity: list[float]
    
    @property
    def wavelengths_nm(self):
        return [w.value(Prefix.NANO) for w in self.wavelengths]

    @classmethod
    def from_raw_data(
        cls,
        wavelengths: list[float],
        counts: list[int],
    ) -> Spectrum: 
        intensities = [float(i) for i in counts]
        
        intensities = intensities - np.amin(intensities)
        intensities = intensities / np.amax(intensities)
        
        return cls([Length(w, Prefix.NANO) for w in wavelengths], intensities)
