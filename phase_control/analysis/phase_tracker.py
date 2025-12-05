import inspect
from typing import Any
import lmfit
import numpy as np
from base_lib.models import Angle, Prefix
from phase_control.analysis.config import AnalysisConfig
from phase_control.domain.models import Spectrum
from base_lib.functions import usCFG_projection



class PhaseTracker():
    current_phase: Angle | None = None
    
    def __init__(self, start_config: AnalysisConfig) -> None:
        self._config = start_config
    
    def update(self, spectrum: Spectrum) -> None:
        
        if self.current_phase is None:
            new_config = self._initialize_fit_parameters(spectrum)
        
        
    
    def _initialize_fit_parameters(self, spectrum: Spectrum) -> AnalysisConfig:
        
        sig = inspect.signature(usCFG_projection)
        first_arg_name = next(iter(sig.parameters))
        
        model = lmfit.Model(usCFG_projection, independent_vars=[first_arg_name])
        
        fit_kwargs: dict[str, Any] = self._config.to_fit_kwargs(usCFG_projection)
        fit_kwargs[first_arg_name] = spectrum.wavelengths_nm
        
        result = model.fit(spectrum.intensity, **fit_kwargs)
        return AnalysisConfig.from_fit_result(self._config, result)
    