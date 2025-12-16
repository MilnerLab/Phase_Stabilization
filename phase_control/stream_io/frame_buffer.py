# phase_control/stream_io/frame_buffer.py
from multiprocessing import Value
import threading
from typing import Optional

import numpy as np

from phase_control.domain.models import Spectrum

from .models import StreamFrame, StreamMeta


class FrameBuffer:
    def __init__(self, meta: StreamMeta) -> None:
        self._lock = threading.Lock()
        self._latest: Optional[StreamFrame] = None
        self.meta: StreamMeta = meta

    def update(self, frame: StreamFrame) -> None:
        with self._lock:
            self._latest = frame

    def get_latest(self) -> Spectrum | None:
        if self._latest is None:
            return None
        with self._lock:
            spec = self._generate_Spectrogram(self._latest)
            self._latest = None
            return spec

    def _generate_Spectrogram(self, frame: StreamFrame) -> Spectrum:
        if self.meta.wavelengths is not None:
            return Spectrum.from_raw_data(self.meta.wavelengths, frame.counts)
        else:
            raise ValueError("Wavelengths not readable.")
        
        