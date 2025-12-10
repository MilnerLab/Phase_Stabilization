# phase_control/ui/config_tab.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from base_lib.models import Length, Prefix, Angle, Range
from phase_control.analysis.config import AnalysisConfig


class ConfigTab:
    """
    Tab für die Eingabe der Analysis-Parameter (AnalysisConfig).

    Zeigt einfache Textfelder für die wichtigsten Parameter:
    - carrier_wavelength [nm]
    - starting_wavelength [nm]
    - bandwidth [nm]
    - baseline
    - phase [rad]
    - acceleration
    - wavelength range [nm]
    """

    def __init__(self, parent: ttk.Notebook, initial: AnalysisConfig) -> None:
        self.frame = ttk.Frame(parent)

        # Tk-Variablen mit Defaults aus initialer Config
        self._carrier_var = tk.StringVar(
            value=f"{initial.carrier_wavelength.value(Prefix.NANO):.6f}"
        )
        self._starting_var = tk.StringVar(
            value=f"{initial.starting_wavelength.value(Prefix.NANO):.6f}"
        )
        self._bandwidth_var = tk.StringVar(
            value=f"{initial.bandwidth.value(Prefix.NANO):.6f}"
        )
        self._baseline_var = tk.StringVar(value=f"{initial.baseline:.6f}")
        self._phase_var = tk.StringVar(value=f"{initial.phase.Rad:.6f}")
        self._acceleration_var = tk.StringVar(value=f"{initial.acceleration:.6f}")

        wl_min = initial.wavelength_range.start.value(Prefix.NANO)
        wl_max = initial.wavelength_range.end.value(Prefix.NANO)
        self._wl_min_var = tk.StringVar(value=f"{wl_min:.6f}")
        self._wl_max_var = tk.StringVar(value=f"{wl_max:.6f}")

        self._build_ui()

    # ------------------------------------------------------------------ #
    # UI Aufbau
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}

        frame = self.frame
        frame.columnconfigure(1, weight=1)

        row = 0

        def add_labeled_entry(label: str, var: tk.StringVar) -> None:
            nonlocal row
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", **pad)
            ttk.Entry(frame, textvariable=var, width=16).grid(
                row=row, column=1, sticky="ew", **pad
            )
            row += 1

        add_labeled_entry("Carrier wavelength [nm]:", self._carrier_var)
        add_labeled_entry("Starting wavelength [nm]:", self._starting_var)
        add_labeled_entry("Bandwidth [nm]:", self._bandwidth_var)
        add_labeled_entry("Baseline:", self._baseline_var)
        add_labeled_entry("Phase [rad]:", self._phase_var)
        add_labeled_entry("Acceleration:", self._acceleration_var)
        ttk.Separator(frame).grid(row=row, column=0, columnspan=2, sticky="ew", **pad)
        row += 1
        add_labeled_entry("Wavelength min [nm]:", self._wl_min_var)
        add_labeled_entry("Wavelength max [nm]:", self._wl_max_var)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_float(value: str, fallback: float) -> float:
        try:
            return float(value.replace(",", "."))
        except ValueError:
            return fallback

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def build_config(self, base: AnalysisConfig | None = None) -> AnalysisConfig:
        """
        Erzeugt eine neue AnalysisConfig aus den UI-Werten.
        Wenn base gegeben ist, werden Felder bei Parse-Fehlern daraus übernommen.
        """
        if base is None:
            base = AnalysisConfig()

        carrier_nm = self._parse_float(
            self._carrier_var.get(),
            base.carrier_wavelength.value(Prefix.NANO),
        )
        starting_nm = self._parse_float(
            self._starting_var.get(),
            base.starting_wavelength.value(Prefix.NANO),
        )
        bandwidth_nm = self._parse_float(
            self._bandwidth_var.get(),
            base.bandwidth.value(Prefix.NANO),
        )
        baseline = self._parse_float(self._baseline_var.get(), base.baseline)
        phase_rad = self._parse_float(self._phase_var.get(), base.phase.Rad)
        acceleration = self._parse_float(
            self._acceleration_var.get(),
            base.acceleration,
        )
        wl_min_nm = self._parse_float(
            self._wl_min_var.get(),
            base.wavelength_range.start.value(Prefix.NANO),
        )
        wl_max_nm = self._parse_float(
            self._wl_max_var.get(),
            base.wavelength_range.end.value(Prefix.NANO),
        )

        return AnalysisConfig(
            carrier_wavelength=Length(carrier_nm, Prefix.NANO),
            starting_wavelength=Length(starting_nm, Prefix.NANO),
            bandwidth=Length(bandwidth_nm, Prefix.NANO),
            baseline=baseline,
            phase=Angle(phase_rad),
            acceleration=acceleration,
            wavelength_range=Range(
                Length(wl_min_nm, Prefix.NANO),
                Length(wl_max_nm, Prefix.NANO),
            ),
        )
