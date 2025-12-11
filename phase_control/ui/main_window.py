# phase_control/ui/main_window.py
from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk

from phase_control.analysis.config import AnalysisConfig
from phase_control.analysis.run_analysis import AnalysisEngine, AnalysisPlotResult
from .config_tab import ConfigTab
from .plot_tab import PlotTab


class MainWindow:
    """
    Main x64 UI:

    - Top-level "Run analysis" button (hosted by the MainWindow).
    - Tab "Plotting" with the embedded plot.
    - Tab "Config parameters" with AnalysisConfig fields.

    The MainWindow orchestrates everything:
    - on Run:
        * pushes UI values into the shared config
        * resets the AnalysisEngine
        * starts a Tk .after loop that calls engine.run_once()
          and passes the result to PlotTab + ConfigTab.
    """

    def __init__(
        self,
        config: AnalysisConfig,
        engine: AnalysisEngine,
        stop_event: threading.Event,
    ) -> None:
        self._config = config
        self._engine = engine
        self._stop_event = stop_event

        self._root = tk.Tk()
        self._root.title("Phase control – Live analysis")

        # Top control bar with Run button
        control_frame = ttk.Frame(self._root)
        control_frame.pack(side="top", fill="x")

        self._run_button = ttk.Button(
            control_frame,
            text="Run analysis",
            command=self._on_run_clicked,
        )
        self._run_button.pack(side="left", padx=8, pady=4)

        # Notebook with tabs
        self._notebook = ttk.Notebook(self._root)
        self._notebook.pack(fill="both", expand=True)

        self._config_tab = ConfigTab(self._notebook, config=self._config)
        self._plot_tab = PlotTab(self._notebook)

        self._notebook.add(self._plot_tab.frame, text="Plotting")
        self._notebook.add(self._config_tab.frame, text="Config parameters")

        # Analysis loop state
        self._running: bool = False
        self._after_id: str | None = None

        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ #
    # Analysis control
    # ------------------------------------------------------------------ #

    def _on_run_clicked(self) -> None:
        """
        Called when the Run button is pressed.

        - stop any running loop
        - push UI values -> shared config
        - reset engine
        - start Tk .after loop
        """
        self._stop_analysis()

        self._config_tab.apply_to_config()
        self._engine.reset()

        self._running = True
        self._schedule_next_step(delay_ms=0)

    def _stop_analysis(self) -> None:
        self._running = False
        if self._after_id is not None:
            try:
                self._root.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = None

    def _schedule_next_step(self, delay_ms: int = 20) -> None:
        if not self._running:
            return
        self._after_id = self._root.after(delay_ms, self._step_once)

    def _step_once(self) -> None:
        if not self._running:
            return

        result = self._engine.run_once()
        if result is None:
            # no data yet -> try again a bit later
            self._schedule_next_step(delay_ms=50)
            return

        # Update plot
        self._plot_tab.update_plot(result)

        # Config was potentially updated by PhaseTracker (same instance),
        # so mirror that back into the UI.
        self._config_tab.refresh_from_config()

        # Next step
        self._schedule_next_step(delay_ms=20)

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    def _on_close(self) -> None:
        self._stop_analysis()
        self._stop_event.set()
        self._root.destroy()

    def run(self) -> None:
        self._root.mainloop()


def run_main_window(
    config: AnalysisConfig,
    engine: AnalysisEngine,
    stop_event: threading.Event,
) -> None:
    ui = MainWindow(config=config, engine=engine, stop_event=stop_event)
    ui.run()
