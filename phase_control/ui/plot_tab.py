# phase_control/ui/plot_tab.py
from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from phase_control.analysis.config import AnalysisConfig
from phase_control.analysis.run_analysis import run_analysis
from phase_control.stream_io import FrameBuffer


class PlotTab:
    """
    Tab 'Plotting':

    - Run-Button, der run_analysis in einem separaten Thread startet
    - einfache Optionen, was im Plot gezeichnet werden soll
    """

    def __init__(
        self,
        parent: ttk.Notebook,
        buffer: FrameBuffer,
        config_provider: Callable[[], AnalysisConfig],
    ) -> None:
        self.frame = ttk.Frame(parent)
        self._buffer = buffer
        self._config_provider = config_provider

        # Analyse-Thread-Verwaltung
        self._analysis_thread: Optional[threading.Thread] = None
        self._analysis_stop_event: Optional[threading.Event] = None

        self._build_ui()

    # ------------------------------------------------------------------ #
    # UI
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}

        frame = self.frame
        frame.columnconfigure(0, weight=1)

        # Run-Button
        run_button = ttk.Button(frame, text="Run analysis", command=self._on_run_clicked)
        run_button.grid(row=0, column=0, sticky="ew", **pad)


    # ------------------------------------------------------------------ #
    # Analyse-Steuerung
    # ------------------------------------------------------------------ #

    def _on_run_clicked(self) -> None:
        """
        Wird aufgerufen, wenn der Run-Button gedrückt wird.
        - stoppt eine laufende Analyse (falls vorhanden)
        - startet run_analysis mit der aktuellen Config neu
        """
        self.stop_analysis()

        config = self._config_provider()

        stop_event = threading.Event()
        self._analysis_stop_event = stop_event

        def worker() -> None:
            run_analysis(
                buffer=self._buffer,
                stop_event=stop_event,
                config=config
            )

        thread = threading.Thread(
            target=worker,
            name="AnalysisThread",
            daemon=True,
        )
        self._analysis_thread = thread
        thread.start()

    def stop_analysis(self) -> None:
        """
        Stoppt eine eventuell laufende Analyse.
        """
        if self._analysis_stop_event is not None:
            self._analysis_stop_event.set()

        if self._analysis_thread is not None and self._analysis_thread.is_alive():
            # kurz warten, aber nicht hart blockieren
            self._analysis_thread.join(timeout=1.0)

        self._analysis_thread = None
        self._analysis_stop_event = None
