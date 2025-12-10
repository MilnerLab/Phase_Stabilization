# phase_control/ui/main_window.py
from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk

from phase_control.analysis.config import AnalysisConfig
from phase_control.stream_io import FrameBuffer
from .config_tab import ConfigTab
from .plot_tab import PlotTab


class MainWindow:
    """
    Haupt-UI für die x64-Seite:

    - Tab 'Plotting' mit Run-Button (startet run_analysis)
    - Tab 'Config parameters' mit AnalysisConfig-Form
    """

    def __init__(self, buffer: FrameBuffer, stop_event: threading.Event) -> None:
        self._buffer = buffer
        self._stop_event = stop_event

        self._root = tk.Tk()
        self._root.title("Phase control – Live analysis")

        self._notebook = ttk.Notebook(self._root)
        self._notebook.pack(fill="both", expand=True)

        # Aktuelle AnalysisConfig
        self._base_config = AnalysisConfig()

        # Tabs
        self._config_tab = ConfigTab(self._notebook, initial=self._base_config)
        self._plot_tab = PlotTab(
            parent=self._notebook,
            buffer=self._buffer,
            config_provider=self._get_current_config,
        )

        self._notebook.add(self._plot_tab.frame, text="Plotting")
        self._notebook.add(self._config_tab.frame, text="Config parameters")

        # Window-Close-Handling
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ #
    # Config-Erzeugung
    # ------------------------------------------------------------------ #

    def _get_current_config(self) -> AnalysisConfig:
        """
        Holt eine neue AnalysisConfig auf Basis der Werte im ConfigTab.
        """
        self._base_config = self._config_tab.build_config(self._base_config)
        return self._base_config

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    def _on_close(self) -> None:
        """
        Wird beim Schließen des Fensters aufgerufen.
        - stoppt laufende Analyse
        - setzt das globale stop_event (für reader_loop)
        - zerstört das Tk-Fenster
        """
        self._plot_tab.stop_analysis()
        self._stop_event.set()
        self._root.destroy()

    def run(self) -> None:
        """
        Startet die Tk mainloop (blockiert bis Fenster geschlossen ist).
        """
        self._root.mainloop()


def run_main_window(buffer: FrameBuffer, stop_event: threading.Event) -> None:
    """
    Convenience-Funktion für app.py.
    """
    ui = MainWindow(buffer=buffer, stop_event=stop_event)
    ui.run()
