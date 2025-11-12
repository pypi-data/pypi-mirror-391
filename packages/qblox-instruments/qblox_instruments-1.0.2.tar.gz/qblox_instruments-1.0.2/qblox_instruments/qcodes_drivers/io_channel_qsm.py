# ----------------------------------------------------------------------------
# Description    : IOChannelQSM QCoDeS interface
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2025)
# ----------------------------------------------------------------------------

# -- include -----------------------------------------------------------------

from functools import partial
from typing import Any, Union, get_type_hints

from qcodes import Instrument, InstrumentChannel
from qcodes import validators as vals

from qblox_instruments.constants import MAX_SAFE_VOLTAGE, MIN_SAFE_VOLTAGE, QSMIOChannelConfig
from qblox_instruments.docstring_helpers import partial_with_numpy_doc
from qblox_instruments.qcodes_drivers.component import Component
from qblox_instruments.types import FilterMode

# -- class -------------------------------------------------------------------


class IOChannelQSM(Component):
    """
    This class represents a QSM channel (for the Source Measurement Unit).
    It combines all channel specific parameters and functions
    into a single QCoDes InstrumentChannel.
    """

    # ------------------------------------------------------------------------
    def __init__(
        self,
        parent: Union[Instrument, InstrumentChannel],
        name: str,
        io_channel_idx: int,
    ) -> None:
        """
        Creates an IO channel class and adds all relevant parameters for the channel.

        Parameters
        ----------
        parent : Union[Instrument, InstrumentChannel]
            The QCoDeS class to which this IO channel belongs.
        name : str
            Name of this IO channel
        io_channel_idx : int
            The index of this IO channel in the parent instrument, representing
            which IO channel is controlled by this class.
        """

        # Initialize instrument channel
        super().__init__(parent, name)

        # Store SM channel index
        self._io_channel_idx = io_channel_idx

        # Add required parent attributes for the QCoDeS parameters to function
        for attr_name in IOChannelQSM._get_required_parent_attr_names():
            self._register(attr_name)

        # Add parameters

        self.add_parameter(
            "source_mode",
            label="Output sourcing behavior for the given channel",
            docstring="Sets/gets the output sourcing behavior for a specified channel.",
            unit="",
            vals=vals.Enum("v_source", "i_source", "ground", "open"),
            set_cmd=partial(
                self._set_io_channel_config_val,
                "source_mode",
            ),
            get_cmd=partial(
                self._get_io_channel_config_val,
                ["source_mode"],
            ),
        )

        self.add_parameter(
            "measure_mode",
            label="Measurement precision for the given channel",
            docstring="Sets/gets the measurement precision for a specified channel.",
            unit="",
            vals=vals.Enum("automatic", "coarse", "fine_nanoampere", "fine_picoampere"),
            set_cmd=partial(
                self._set_io_channel_config_val,
                "measure_mode",
            ),
            get_cmd=partial(
                self._get_io_channel_config_val,
                ["measure_mode"],
            ),
        )

        self.add_parameter(
            "ramping_rate",
            label="Ramping rate for output adjustment for the given channel",
            docstring="Sets/gets the ramping rate for output adjustment for the specified channel.",
            unit="V/s",
            vals=vals.Numbers(),
            set_cmd=partial(
                self._set_io_channel_config_val,
                "ramping_rate",
            ),
            get_cmd=partial(
                self._get_io_channel_config_val,
                ["ramping_rate"],
            ),
        )

        self.add_parameter(
            "integration_time",
            label="Integration time for the given channel",
            docstring="Sets/gets the integration time for the specified channel.",
            unit="s",
            vals=vals.Numbers(),
            set_cmd=partial(
                self._set_io_channel_config_val,
                "integration_time",
            ),
            get_cmd=partial(
                self._get_io_channel_config_val,
                ["integration_time"],
            ),
        )

        self.add_parameter(
            "coarse_voltage",
            label="Coarse voltage for the given channel",
            docstring="Sets/gets the coarse voltage for the specified channel.",
            unit="V",
            vals=vals.Numbers(min_value=MIN_SAFE_VOLTAGE, max_value=MAX_SAFE_VOLTAGE),
            set_cmd=self._set_coarse_voltage,
            get_cmd=partial(
                self._get_io_channel_config_val,
                ["coarse_voltage"],
            ),
        )

        self.add_parameter(
            "fine_voltage",
            label="Fine voltage for the given channel",
            docstring="Sets/gets the fine voltage for the specified channel.",
            unit="V",
            vals=vals.Numbers(0, 0.0025),
            set_cmd=partial(
                self._set_io_channel_config_val,
                "fine_voltage",
            ),
            get_cmd=partial(
                self._get_io_channel_config_val,
                ["fine_voltage"],
            ),
        )

        self.add_parameter(
            "low_pass_filter_cutoff",
            label="Output low-pass filter mode for the given channel",
            docstring="Sets/gets the output low-pass filter mode for a specified channel.",
            unit="Hz",
            vals=vals.Enum(*FilterMode),
            set_cmd=partial(
                self._set_io_channel_config_val,
                "low_pass_filter_cutoff",
            ),
            get_cmd=partial(
                self._get_io_channel_config_val,
                ["low_pass_filter_cutoff"],
            ),
            set_parser=FilterMode,
            get_parser=FilterMode,
        )

        # Set the default safe voltage range
        self._safe_voltage_range: tuple[float, float] = (MIN_SAFE_VOLTAGE, MAX_SAFE_VOLTAGE)

    # ------------------------------------------------------------------------
    @property
    def io_channel_idx(self) -> int:
        """
        Get IO channel index.

        Returns
        ----------
        int
            IOChannelQSM index
        """

        return self._io_channel_idx

    # ------------------------------------------------------------------------
    @staticmethod
    def _get_required_parent_attr_names() -> list:
        """
        Return list of parent attribute names that are required for the QCoDeS
        parameters to function, so that they can be registered to this object
        using the _register method.

        Returns
        ----------
        list
            List of parent attribute names to register.
        """

        # IOChannelQSM attributes
        attr_names = [
            "_get_io_channel_config_val",
            "_set_io_channel_config",
            "_measure_current",
            "_set_qsm_channel_to_zero",
            "_set_voltage_wait",
            "_set_instant",
            "_measure_voltage",
            "_set_safe_voltage_range",
        ]

        return attr_names

    # ------------------------------------------------------------------------
    def _register(self, attr_name: str) -> None:
        """
        Register parent attribute to this IO channel using functools.partial
        to pre-select the IO channel index. If the attribute does not exist in

        the parent class, a method that raises a `NotImplementedError`
        exception is registered instead. The docstring of the parent attribute
        is also copied to the registered attribute.

        Parameters
        ----------
        attr_name : str
            Attribute name of parent to register.
        """

        if hasattr(self.parent, attr_name):
            parent_attr = getattr(self.parent, attr_name)
            partial_doc = (
                "Note\n"
                + "----------\n"
                + "This method calls {1}.{0} using functools.partial to set the "
                + "IO channel index. The docstring above is of {1}.{0}:\n\n"
            ).format(attr_name, type(self.parent).__name__)
            partial_func = partial_with_numpy_doc(
                parent_attr, self.io_channel_idx, end_with=partial_doc
            )
            setattr(self, attr_name, partial_func)
        else:

            def raise_not_implemented_error(*args, **kwargs) -> None:
                raise NotImplementedError(
                    f'{self.parent.name} does not have "{attr_name}" attribute.'
                )

            setattr(self, attr_name, raise_not_implemented_error)

    def _set_io_channel_config_val(self, key: Any, val: Any) -> None:
        """
        Set value of specific IO channel configuration parameter.

        Parameters
        ----------
        key : Any
            Configuration key to access.
        val: Any
            Value to set parameter to.
        """

        setting = {key: val}
        self._set_io_channel_config(setting)

    def measure_current(self) -> float:
        """
        Returns the current measured for a specified channel.

        Returns
        -------
        float
            The measured current for the specified channel in amperes.
        """

        return self._measure_current()

    def measure_voltage(self) -> float:
        """
        Returns the voltage measured for a specified channel.

        Returns
        -------
        float
            The measured voltage for the specified channel in volts.

        Raises
        ------
        Exception
            If the io channel number is not 0 or 4.
        """

        if self._io_channel_idx not in (0, 4):
            raise ValueError(
                f"measure_voltage is only implemented for io channels 0 and 4 on module "
                f"'{self.parent.name}'"
            )

        return self._measure_voltage()

    def set_qsm_outputs_to_zero(self) -> None:
        """
        Resets the output for the channel to zero.

        Returns
        -------
        None
        """
        self._set_qsm_channel_to_zero()

    def _check_safe_voltage_range(self, voltage: float) -> None:
        """
        Ensure that the given voltage falls within safety limits.

        Parameters
        ----------
        voltage : float
            The voltage to test against the safety limits.

        Raises
        -------
        ValueError
            The given voltage is out of range.
        """
        min_v, max_v = self._safe_voltage_range
        if not min_v <= voltage <= max_v:
            raise ValueError(
                f"A voltage of {voltage:+} V cannot be set because it falls outside the safety "
                f"range of {min_v:+} V to {max_v:+} V"
            )

    def _set_coarse_voltage(self, voltage: float) -> None:
        """
        Set the coarse voltage for the current channel.

        Parameters
        ----------
        voltage : float
            The coarse voltage to set.
        """
        self._check_safe_voltage_range(voltage)
        self._set_io_channel_config_val("coarse_voltage", voltage)

    def set_safe_voltage_range(self, min_voltage: float, max_voltage: float) -> None:
        """
        Set the safe voltage range for the current channel.

        Parameters
        ----------
        min_voltage : float
            The desired minimum voltage in volts.
        max_voltage : float
            The desired maximum voltage in volts.
        """
        self._set_safe_voltage_range(min_voltage, max_voltage)

    def set_voltage_wait(self, voltage: float) -> None:
        """
        Sets the voltage for a specified channel and blocks execution
        until the voltage stabilizes at the requested value.

        Returns
        -------
        None
        """
        self._check_safe_voltage_range(voltage)
        self._set_voltage_wait(voltage)

    def set_instant(self, voltage: float) -> None:
        """
        Sets the voltage for a specified channel immediately,
        bypassing ramping constraints.

        Returns
        -------
        None
        """
        self._check_safe_voltage_range(voltage)
        self._set_instant(voltage)

    def _validate_config(self, config: QSMIOChannelConfig) -> None:
        """
        Validate manually the configuration dict for the IO channel.

        Parameters
        ----------
        config : QSMIOChannelConfig
            Manually provided config file

        Returns
        --------
        None

        Raises
        --------
            RuntimeError
        """

        for param_name, param_value in config.items():
            # 'Channel' is part of the config but needs not to be validated
            if param_name == "channel":
                continue

            try:
                vals = self.parameters[param_name]
            except KeyError:
                raise RuntimeError(
                    f"Configuration validation failed: Parameter '{param_name}' "
                    f"is not a valid QSM IO channel parameter. "
                    f"Expected one of: {list(get_type_hints(QSMIOChannelConfig).keys())}. "
                    f"Please verify your configuration dictionary contains"
                    f" only supported parameters."
                )
            vals.validate(param_value)

    def set_io_channel_config(self, config: dict[str, str]) -> None:
        """
        Set the IO channel config of the IO channel.

        Returns
        -------
        None

        Raises
        -------
        ValidationError
        """
        self._validate_config(config)
        self._set_io_channel_config(config)
