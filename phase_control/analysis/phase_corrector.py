from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from base_lib.models import Angle, AngleUnit, Prefix


@dataclass
class PhaseCorrector:
    
    correction_phase: Optional[Angle] = field(default=None, init=False)
    _starting_phase: Optional[Angle] = field(default=None, init=False, repr=False)
    _last_moved_phase: Optional[Angle] = field(default=None, init=False, repr=False)

    def update(self, phase: Angle) -> Angle:
        
        if self._starting_phase is None:
            self._starting_phase = phase
            self.correction_phase = Angle(0)
        else:
            if self._last_moved_phase is None:
                self.correction_phase = Angle(phase - self._starting_phase)
                self._last_moved_phase = phase
            else:
                if np.abs(Angle(phase - self._last_moved_phase)) > Angle(2, AngleUnit.DEG):
                    self.correction_phase = Angle(phase - self._last_moved_phase)
                else:
                    self.correction_phase = Angle(0)

        return self.correction_phase

    def reset(self) -> None:
        self._starting_phase = None
        self.correction_phase = None
