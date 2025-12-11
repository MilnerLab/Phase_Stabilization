from collections import deque
import inspect
from typing import Any, cast
import lmfit
from base_lib.models import Angle
from phase_control.analysis.config import AnalysisConfig, FitParameter
from phase_control.domain.models import Spectrum
from base_lib.functions import usCFG_projection

RESIDUAL_THRESHOLD = 5
MAX_LEN = int(10)

class PhaseTracker():
    current_phase: Angle | None = None
    
    def __init__(self, start_config: AnalysisConfig) -> None:
        self._config: AnalysisConfig = start_config
        self._fits: deque[FitParameter] = deque(maxlen=self._config.avg_spectra)

    def update(self, spectrum: Spectrum) -> None:
        if len(self._fits) < self._config.avg_spectra and self.current_phase is None:
            self._fits.append(self._initialize_fit_parameters(spectrum))
            print("gathering configs")
            return
        else:
            if self.current_phase is None:
                self._config.copy_from(FitParameter.mean(self._fits))
                
            if len(self._fits) < self._config.avg_spectra:
                self._fits.append(self._fit_phase(spectrum))
                self.current_phase = Angle(0)
            else:
                new_config = FitParameter.mean(self._fits)
                self._fits.clear()
                
                if new_config.residual < self._config.residuals_threshold:
                    print("Residuals: ", new_config.residual)
                    self.current_phase = new_config.phase
                    self._config.phase = new_config.phase
    
    def _initialize_fit_parameters(self, spectrum: Spectrum) -> FitParameter:
        
        first_arg_name = self._get_first_arg_name()
        model = lmfit.Model(usCFG_projection, independent_vars=[first_arg_name])
        
        fit_kwargs: dict[str, Any] = self._config.to_fit_kwargs(usCFG_projection)
        fit_kwargs[first_arg_name] = spectrum.wavelengths_nm
        
        result = model.fit(spectrum.intensity, **fit_kwargs, max_nfev=int(1000000))
        return FitParameter.from_fit_result(self._config, result)
    
    
    def _fit_phase(self, spectrum: Spectrum) -> FitParameter:
        
        first_arg_name = self._get_first_arg_name()
        model = lmfit.Model(usCFG_projection, independent_vars=[first_arg_name])

        floats = self._config.to_fit_kwargs(usCFG_projection)  

        param_kwargs: dict[str, Any] = dict(floats)

        params = model.make_params(**param_kwargs)  
        for name, par in params.items():
            par.vary = (name == "phase")

        x_kwargs: dict[str, Any] = {first_arg_name: spectrum.wavelengths_nm}

        result = model.fit(
            spectrum.intensity,
            params=params,
            **x_kwargs,
        )
        
        return FitParameter.from_fit_result(self._config, result)

    def _get_first_arg_name(self) -> str:
        sig = inspect.signature(usCFG_projection)
        return next(iter(sig.parameters))
    