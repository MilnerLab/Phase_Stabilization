from dataclasses import dataclass
import math

import numpy as np

from base_lib.models import Angle, AngleUnit

STARTING_PHASE = Angle(0, AngleUnit.DEG)
PHASE_TOLERANCE = Angle(10, AngleUnit.DEG)

CONVERSION_CONST = 1/4      
CORRECTION_SIGN = -1      # abhängig vom QWP

from dataclasses import dataclass

@dataclass
class PhaseCorrector:
    _correction_angle: Angle = Angle(0, AngleUnit.DEG)

    def update(self, phase: Angle) -> Angle:
        
        phase_wrapped = self._wrap_phase_pi(phase)

        phase_error = Angle(phase_wrapped - STARTING_PHASE)

        if np.abs(phase_error) > PHASE_TOLERANCE:
            correction_phase = phase_error
        else:
            correction_phase = Angle(0)

        self._correction_angle = self._convert_phase_to_hwp(correction_phase)
        return self._correction_angle
    
    @staticmethod
    def _wrap_phase_pi(phase: Angle) -> Angle:
        step = math.pi / 1.0
        k = round(phase/step)
        multiple = k * step
        
        return Angle(phase - multiple)
    
    @staticmethod
    def _convert_phase_to_hwp(phase: Angle) -> Angle:
        phase_deg = phase.Deg
        hwp_deg = CORRECTION_SIGN * phase_deg * CONVERSION_CONST
        return Angle(hwp_deg, AngleUnit.DEG)
