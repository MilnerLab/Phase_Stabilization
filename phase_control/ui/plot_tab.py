# phase_control/ui/plot_tab.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from phase_control.analysis.run_analysis import AnalysisPlotResult


class PlotTab:
    """
    Plotting tab with an embedded Matplotlib figure.

    This tab does *not* know about the AnalysisEngine or the config.
    It only exposes:
      - update_plot(result) to draw new data
      - clear() to reset the plot
    """

    def __init__(self, parent: ttk.Notebook) -> None:
        self.frame = ttk.Frame(parent)

        # Tk state
        self._show_current_var = tk.BooleanVar(value=True)
        self._show_fit_var = tk.BooleanVar(value=True)
        self._show_zero_var = tk.BooleanVar(value=True)

        self._build_ui()

    # ------------------------------------------------------------------ #
    # UI
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}
        frame = self.frame
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Options (checkboxes)
        options_frame = ttk.LabelFrame(frame, text="Plot options")
        options_frame.grid(row=0, column=0, sticky="ew", **pad)
        options_frame.columnconfigure(0, weight=1)

        ttk.Checkbutton(
            options_frame,
            text="Show current spectrum",
            variable=self._show_current_var,
            command=self._update_visibility,
        ).grid(row=0, column=0, sticky="w", **pad)

        ttk.Checkbutton(
            options_frame,
            text="Show fitted spectrum",
            variable=self._show_fit_var,
            command=self._update_visibility,
        ).grid(row=1, column=0, sticky="w", **pad)

        ttk.Checkbutton(
            options_frame,
            text="Show zero-phase fit",
            variable=self._show_zero_var,
            command=self._update_visibility,
        ).grid(row=2, column=0, sticky="w", **pad)

        # Matplotlib figure
        plot_frame = ttk.Frame(frame)
        plot_frame.grid(row=1, column=0, sticky="nsew")
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)

        self._figure = Figure(figsize=(6, 4), dpi=100)
        self._ax = self._figure.add_subplot(111)

        (self._line_current,) = self._ax.plot([], [], label="Current")
        (self._line_fit,) = self._ax.plot([], [], label="Fit")
        (self._line_zero,) = self._ax.plot([], [], label="Zero-phase")

        self._ax.set_xlabel("Wavelength [nm]")
        self._ax.set_ylabel("Counts")
        self._ax.grid(True)
        self._ax.legend()

        self._canvas = FigureCanvasTkAgg(self._figure, master=plot_frame)
        self._canvas_widget = self._canvas.get_tk_widget()
        self._canvas_widget.grid(row=0, column=0, sticky="nsew")

        self._update_visibility()
        self._canvas.draw()

    def _update_visibility(self) -> None:
        self._line_current.set_visible(self._show_current_var.get())
        self._line_fit.set_visible(self._show_fit_var.get())
        self._line_zero.set_visible(self._show_zero_var.get())
        self._canvas.draw_idle()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def update_plot(self, result: AnalysisPlotResult) -> None:
        """Update the lines according to the given AnalysisPlotResult."""
        x = result.x

        if self._show_current_var.get():
            self._line_current.set_data(x, result.y_current)
        if self._show_fit_var.get() and result.y_fit is not None:
            self._line_fit.set_data(x, result.y_fit)
        if self._show_zero_var.get() and result.y_zero_phase is not None:
            self._line_zero.set_data(x, result.y_zero_phase)

        self._ax.relim()
        self._ax.autoscale_view()
        self._canvas.draw_idle()

    def clear(self) -> None:
        """Clear all plotted data."""
        self._line_current.set_data([], [])
        self._line_fit.set_data([], [])
        self._line_zero.set_data([], [])
        self._ax.relim()
        self._ax.autoscale_view()
        self._canvas.draw_idle()
