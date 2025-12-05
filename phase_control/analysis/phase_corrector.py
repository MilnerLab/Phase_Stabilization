from collections import deque
from dataclasses import dataclass, field
from typing import Deque

from base_lib.models import Angle

@dataclass
class PhaseCorrector:
    low_threshold: Angle          
    high_threshold: Angle         
    window_size: int = 10         

    _history: Deque[Angle] = field(init=False, repr=False)
    _is_high: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if self.low_threshold >= self.high_threshold:
            raise ValueError("low_threshold must be smaller than high_threshold")
        self._history = deque(maxlen=self.window_size)

    @property
    def history(self) -> list[Angle]:
        """Return the stored phases (oldest -> newest)."""
        return list(self._history)

    @property
    def is_high(self) -> bool:
        """Current Schmitt-trigger output."""
        return self._is_high

    def update(self, phase: Angle) -> bool:
        """
        Add a new phase value and update Schmitt-trigger state.

        Returns the current Schmitt output (True = high, False = low).
        """
        self._history.append(phase)

        v = phase
        low = self.low_threshold
        high = self.high_threshold

        # klassischer Schmitt-Trigger:
        if not self._is_high:
            # waren bisher im "low"-Zustand
            if v >= high:
                self._is_high = True
        else:
            # waren bisher im "high"-Zustand
            if v <= low:
                self._is_high = False

        return self._is_high
