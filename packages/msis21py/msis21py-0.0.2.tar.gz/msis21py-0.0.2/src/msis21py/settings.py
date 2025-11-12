# %%
from __future__ import annotations
from numbers import Number
from typing import List, Literal, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ControlMode = Literal['Off', 'On', 'Cross']
ApMode = Literal['Daily', 'Storm']


@dataclass
class Settings:
    """Settings for NRLMSIS-2.1 model evaluation.
    """
    f107: ControlMode = 'On'
    """F10.7 solar flux control mode."""
    time_independent: ControlMode = 'On'
    """Time-independent effects control mode."""
    symmetrical_annual: ControlMode = 'On'
    """Symmetrical annual effects control mode."""
    symmetrical_semiannual: ControlMode = 'On'
    """Symmetrical semiannual effects control mode."""
    asymmetrical_annual: ControlMode = 'On'
    """Asymmetrical annual effects control mode."""
    asymmetrical_semiannual: ControlMode = 'On'
    """Asymmetrical semiannual effects control mode."""
    diurnal: ControlMode = 'On'
    """Diurnal effects control mode."""
    semidiurnal: ControlMode = 'On'
    """Semidiurnal effects control mode."""
    ap_mode: ApMode = 'Daily'
    """Ap index mode."""
    all_spatiotemporal_effects: ControlMode = 'On'
    """All spatiotemporal effects control mode."""
    longitude_effects: ControlMode = 'On'
    """Longitude effects control mode."""
    time_and_mixed_effects: ControlMode = 'On'
    """Time and mixed time/longitude control mode."""
    ap_and_time_effects: ControlMode = 'On'
    """Mixed Ap/time/longitude effects control mode."""
    terdiurnal: ControlMode = 'On'
    """Terdiurnal effects control mode."""

    def to_json(self) -> str:
        """Convert settings to JSON string.

        Returns:
            str: JSON string representation of settings.
        """
        import json
        from dataclasses import asdict
        return json.dumps(asdict(self))


def _flags(inp: str) -> np.float32:
    if inp == 'Off':
        return np.float32(0)
    elif inp == 'On':
        return np.float32(1.0)
    elif inp == 'Daily':
        return np.float32(1.0)
    elif inp == 'Cross':
        return np.float32(2.0)
    elif inp == 'Storm':
        return np.float32(-1.0)
    else:
        raise ValueError(f'Unknown flag {inp}')


@dataclass
class ComputedSettings:
    """Computed settings for NRLMSIS-2.1 model evaluation.
    DO NOT create this class directly; use :obj:`ComputedSettings.from_settings()` instead.
    """
    switch_legacy: np.ndarray

    @staticmethod
    def from_settings(settings: Settings) -> ComputedSettings:
        """Create computed settings from user-defined settings.

        Args:
            settings (Settings): User-defined settings.

        Returns:
            ComputedSettings: Computed settings for model evaluation.
        """
        switch_legacy = np.full(25, 1.0, dtype=np.float32)
        switch_legacy[0] = _flags(settings.f107)
        switch_legacy[1] = _flags(settings.time_independent)
        switch_legacy[2] = _flags(settings.symmetrical_annual)
        switch_legacy[3] = _flags(settings.symmetrical_semiannual)
        switch_legacy[4] = _flags(settings.asymmetrical_annual)
        switch_legacy[5] = _flags(settings.asymmetrical_semiannual)
        switch_legacy[6] = _flags(settings.diurnal)
        switch_legacy[7] = _flags(settings.semidiurnal)
        switch_legacy[8] = _flags(settings.ap_mode)
        switch_legacy[9] = _flags(settings.all_spatiotemporal_effects)
        switch_legacy[10] = _flags(settings.longitude_effects)
        switch_legacy[11] = _flags(settings.time_and_mixed_effects)
        switch_legacy[12] = _flags(settings.ap_and_time_effects)
        switch_legacy[13] = _flags(settings.terdiurnal)
        return ComputedSettings(switch_legacy=switch_legacy)
