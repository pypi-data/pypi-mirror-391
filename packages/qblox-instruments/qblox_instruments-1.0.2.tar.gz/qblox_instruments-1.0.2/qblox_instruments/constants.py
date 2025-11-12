# ----------------------------------------------------------------------------
# Description    : IOChannelQSM QCoDeS interface
# Description    : Project wide constants
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2025)
# ----------------------------------------------------------------------------

from typing import Final, Literal, TypedDict

MIN_SAFE_VOLTAGE: Final[float] = -10.0
MAX_SAFE_VOLTAGE: Final[float] = +10.0


class QSMIOChannelConfig(TypedDict):
    """
    A type for a configuration dictionary of a IO channel of a QSM module.
    """

    channel: int
    coarse_voltage: float
    fine_voltage: float
    integration_time: float
    low_pass_filter_cutoff: int
    measure_mode: Literal[
        "automatic",
        "coarse",
        "fine_nanoampere",
        "fine_picoampere",
    ]
    ramping_rate: int
    source_mode: Literal[
        "v_source",
        "i_source",
        "ground",
        "open",
    ]
