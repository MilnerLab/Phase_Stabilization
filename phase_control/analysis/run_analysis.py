# phase_control/analysis/run_analysis.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, cast

import numpy as np

from base_lib.functions import usCFG_projection
from base_lib.models import Angle
from phase_control.analysis.config import AnalysisConfig, FitParameter
from phase_control.analysis.phase_corrector import PhaseCorrector
from phase_control.analysis.phase_tracker import PhaseTracker
from phase_control.correction_io.elliptec_ell14 import ElliptecRotator
from phase_control.domain.models import Spectrum
from phase_control.stream_io import FrameBuffer, StreamMeta


@dataclass
class AnalysisPlotResult:
    """
    Everything the UI needs after a single analysis step.
    """
    x: np.ndarray
    y_current: np.ndarray
    y_fit: Optional[np.ndarray]
    y_zero_phase: Optional[np.ndarray]
    current_phase: Optional[Angle]
    correction_angle: Optional[Angle]
    spectrum: Spectrum


class AnalysisEngine:

    def __init__(
        self,
        config: AnalysisConfig,
        buffer: FrameBuffer
    ) -> None:
        # Shared config instance used by UI and analysis
        self.config = config

        # Data source
        self._buffer = buffer

        # Helpers – they keep a reference to the same config instance
        self._phase_tracker = PhaseTracker(cast(FitParameter, self.config))
        self._phase_corrector = PhaseCorrector()
        self._rotator = ElliptecRotator(max_address="0")

    def reset(self) -> None:
            """
            Optional reset for a fresh run (e.g. after big config changes).
            Recreates the PhaseTracker with the current shared config.
            """
            self._phase_tracker = PhaseTracker(self.config)
        # ------------------------------------------------------------------ #
        # Public API
        # ------------------------------------------------------------------ #

    def step(self) -> Optional[AnalysisPlotResult]:
        spectrum = self._buffer.get_latest()
        
        if spectrum is None:
            return None

        spectrum = spectrum.cut(self.config.wavelength_range)

        # Phase tracking
        self._phase_tracker.update(spectrum)
        current_phase: Optional[Angle] = self._phase_tracker.current_phase

        # Fit and zero-phase fit
        try:
            # PhaseTracker is expected to update self.config (same instance)
            kwargs_fit = self.config.to_fit_kwargs(usCFG_projection)
            y_fit = usCFG_projection(spectrum.wavelengths_nm, **kwargs_fit)

            kwargs_zero = dict(kwargs_fit)
            if "phase" in kwargs_zero:
                kwargs_zero["phase"] = 0.0
            y_zero = usCFG_projection(spectrum.wavelengths_nm, **kwargs_zero)
        except Exception:
            y_fit = None
            y_zero = None

        # Correction angle
        correction_angle: Optional[Angle] = None
        if current_phase is not None:
            correction_angle = self._phase_corrector.update(current_phase)
            self._rotator.rotate(correction_angle)

        return AnalysisPlotResult(
            x=spectrum.wavelengths_nm,
            y_current=spectrum.intensity,
            y_fit=y_fit,
            y_zero_phase=y_zero,
            current_phase=current_phase,
            correction_angle=correction_angle,
            spectrum=spectrum,
        )
