# phase_control/ui/config_tab.py
from __future__ import annotations

from dataclasses import fields
import tkinter as tk
from tkinter import ttk

from base_lib.models import Length, Prefix, Angle, Range
from phase_control.analysis.config import AnalysisConfig


class ConfigTab:

    def __init__(self, parent: ttk.Notebook, config: AnalysisConfig) -> None:
        self.frame = ttk.Frame(parent)

        # Shared config instance
        self._config = config

        # Tk variables
        self._carrier_var = tk.StringVar()
        self._starting_var = tk.StringVar()
        self._bandwidth_var = tk.StringVar()
        self._baseline_var = tk.StringVar()
        self._phase_var = tk.StringVar()
        self._acceleration_var = tk.StringVar()
        self._wl_min_var = tk.StringVar()
        self._wl_max_var = tk.StringVar()

        self._build_ui()
        self.refresh_from_config()

    # ------------------------------------------------------------------ #
    # UI
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

    def refresh_from_config(self) -> None:
        """
        Update UI fields from the shared config.
        Call this whenever the config has been changed elsewhere.
        """
        cfg = self._config

        self._carrier_var.set(f"{cfg.carrier_wavelength.value(Prefix.NANO):.6f}")
        self._starting_var.set(f"{cfg.starting_wavelength.value(Prefix.NANO):.6f}")
        self._bandwidth_var.set(f"{cfg.bandwidth.value(Prefix.NANO):.6f}")
        self._baseline_var.set(f"{cfg.baseline:.6f}")
        self._phase_var.set(f"{cfg.phase.Rad:.6f}")
        self._acceleration_var.set(f"{cfg.acceleration:.6f}")

        wl_min_nm = cfg.wavelength_range.min.value(Prefix.NANO)
        wl_max_nm = cfg.wavelength_range.max.value(Prefix.NANO)
        self._wl_min_var.set(f"{wl_min_nm:.6f}")
        self._wl_max_var.set(f"{wl_max_nm:.6f}")

    def apply_to_config(self) -> None:
        """
        Parse the UI fields and write the values into the shared config
        instance. This does not create a new AnalysisConfig; instead it
        builds a temporary one and copies all fields over.
        """
        cfg = self._config

        carrier_nm = self._parse_float(
            self._carrier_var.get(),
            cfg.carrier_wavelength.value(Prefix.NANO),
        )
        starting_nm = self._parse_float(
            self._starting_var.get(),
            cfg.starting_wavelength.value(Prefix.NANO),
        )
        bandwidth_nm = self._parse_float(
            self._bandwidth_var.get(),
            cfg.bandwidth.value(Prefix.NANO),
        )
        baseline = self._parse_float(self._baseline_var.get(), cfg.baseline)
        phase_rad = self._parse_float(self._phase_var.get(), cfg.phase.Rad)
        acceleration = self._parse_float(
            self._acceleration_var.get(),
            cfg.acceleration,
        )
        wl_min_nm = self._parse_float(
            self._wl_min_var.get(),
            cfg.wavelength_range.start.value(Prefix.NANO),
        )
        wl_max_nm = self._parse_float(
            self._wl_max_var.get(),
            cfg.wavelength_range.end.value(Prefix.NANO),
        )

        tmp = AnalysisConfig(
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

        for f in fields(cfg):
            setattr(cfg, f.name, getattr(tmp, f.name))
