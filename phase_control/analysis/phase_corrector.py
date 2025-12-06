from dataclasses import dataclass, field
import math
from typing import Optional

import numpy as np

from base_lib.models import Angle, AngleUnit, Prefix

STARTING_PHASE = Angle(0, AngleUnit.DEG)
PHASE_TOLERANCE = Angle(20, AngleUnit.DEG)

# grober Startwert: 1° HWP ändert die Fit-Phase um ca. 4°
# → HWP_deg = - phase_deg / 4
CONVERSION_CONST = 45 / 180      # deg_HWP pro deg_Phase
CORRECTION_SIGN = 1      

from dataclasses import dataclass

@dataclass
class PhaseCorrector:
    _correction_angle: Angle = Angle(0, AngleUnit.DEG)

    def update(self, phase: Angle) -> Angle:
        phase_wrapped = self._wrap_phase_pi(phase)

        phase_error = Angle(phase_wrapped - STARTING_PHASE)

        if np.abs(phase_error) > PHASE_TOLERANCE:
            correction_phase = phase_error
            print("Correction needed!", correction_phase.Deg)
        else:
            correction_phase = Angle(0)

        self._correction_angle = self._convert_phase_to_hwp(correction_phase)
        return self._correction_angle
    
    def update_different_logic(self, phase: Angle)-> Angle:
        phase_wrapped = self._wrap_phase_pi(phase)
        
        # different corrector logic

        #self._correction_angle = self._convert_phase_to_hwp(correction_phase)
        return self._correction_angle

    @staticmethod
    def _wrap_phase_pi(phase: Angle) -> Angle:
        pi = math.pi
        rad = phase.Rad
        wrapped = (rad + 0.5 * pi) % pi - 0.5 * pi
        return Angle(wrapped *2, AngleUnit.RAD)

    @staticmethod
    def _convert_phase_to_hwp(phase: Angle) -> Angle:
        phase_deg = phase.Deg
        hwp_deg = CORRECTION_SIGN * phase_deg * CONVERSION_CONST
        return Angle(hwp_deg, AngleUnit.DEG)
