# --------------------------------------------------------------------------
# Description    : Qblox instruments build information
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# --------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

# -- definitions -------------------------------------------------------------

# Wildcard import definition
__all__ = ["BuildInfo", "DeviceInfo", "__version__", "get_build_info"]


# -- classes -----------------------------------------------------------------


@dataclass(init=False, frozen=True)
class BuildInfo:
    """
    Class representing build information for a particular component.
    """

    __slots__ = ("build", "dirty", "hash", "version")
    version: tuple[int, int, int]
    build: datetime
    hash: int
    dirty: False

    # ------------------------------------------------------------------------
    def __init__(
        self,
        version: Union[str, tuple[int, int, int]],
        build: Union[str, int, datetime],
        hash: Union[str, int],  # noqa: A002 (used in dict and json)
        dirty: Union[str, bool],
    ) -> None:
        """
        Makes a build information object.

        Parameters
        ----------
        version: Union[str, tuple[int, int, int]]
            Either a canonical version string or a three-tuple of integers.
        build: Union[str, int, datetime],
            The build timestamp, either as a string formatted like
            "17/11/2021-19:04:53" (as used in ``*IDN?``), a Unix timestamp in
            seconds, or a Python datetime object.
        hash: Union[str, int]
            The git hash of the repository that the build was run from,
            either as a hex string with at least 8 characters, or as an
            integer. If 0x is prefixed, the hash may have less than 8 digits,
            implying zeros in front.
        dirty: Union[str, bool]
            Whether the git repository was dirty at the time of the build,
            either as a ``0`` or ``1`` string (as in ``*IDN?``) or as the
            boolean itself.
        """
        git_hash = hash

        # Convert and check version.
        if isinstance(version, str):
            version = map(int, version.split("."))
        version = tuple(version)
        if len(version) != 3:
            raise ValueError("invalid version specified")
        for comp in version:
            if not isinstance(comp, int):
                raise TypeError("unsupported type for version")
            if comp < 0:
                raise ValueError("invalid version specified")
        object.__setattr__(self, "version", version)

        # Convert and check build timestamp.
        if isinstance(build, str):
            build = datetime.strptime(build, "%d/%m/%Y-%H:%M:%S")
        elif isinstance(build, int):
            build = datetime.fromtimestamp(build)
        if not isinstance(build, datetime):
            raise TypeError("unsupported type for build")
        object.__setattr__(self, "build", build)

        # Convert and check git hash.
        if isinstance(git_hash, str):
            m = re.fullmatch("0x[0-9a-fA-F]{1,8}|[0-9a-fA-F]{8}", git_hash)
            if not m:
                raise ValueError(f"invalid or too short git hash specified: {git_hash!r}")
            git_hash = int(m.group(0), 16)
        if not isinstance(git_hash, int):
            raise TypeError("unsupported type for hash")
        if git_hash < 0 or git_hash > 0xFFFFFFFF:
            raise ValueError("hash integer out of range")
        object.__setattr__(self, "hash", git_hash)

        # Convert and check dirty flag.
        if isinstance(dirty, str):
            if dirty == "0":
                dirty = False
            elif dirty == "1":
                dirty = True
            else:
                raise ValueError("invalid string specified for dirty")
        if not isinstance(dirty, bool):
            raise TypeError("unsupported type for dirty")
        object.__setattr__(self, "dirty", dirty)

    # ------------------------------------------------------------------------
    @property
    def version_str(self) -> str:
        """
        The version as a string.

        :type: str
        """
        return ".".join(map(str, self.version))

    # ------------------------------------------------------------------------
    @property
    def build_str(self) -> str:
        """
        The build time as a string, as formatted for ``*IDN?``.

        :type: str
        """
        return self.build.strftime("%d/%m/%Y-%H:%M:%S")

    # ------------------------------------------------------------------------
    @property
    def build_iso(self) -> str:
        """
        The build time as a string, formatted using the ISO date format.

        :type: str
        """
        return self.build.isoformat()

    # ------------------------------------------------------------------------
    @property
    def build_unix(self) -> int:
        """
        The build time as a unix timestamp in seconds.

        :type: int
        """
        return int(self.build.timestamp())

    # ------------------------------------------------------------------------
    @property
    def hash_str(self) -> str:
        """
        The git hash as a string.

        :type: str
        """
        return f"{self.hash:08x}"

    # ------------------------------------------------------------------------
    @property
    def dirty_str(self) -> str:
        """
        The dirty flag as a ``0`` or ``1`` string (as used for ``*IDN?``).

        :type: str
        """
        return "1" if self.dirty else "0"

    # ------------------------------------------------------------------------
    @classmethod
    def from_idn(cls, idn: str, prefix: str = "") -> Optional["BuildInfo"]:
        """
        Constructs a build information structure from an ``*IDN?`` string.

        Parameters
        ----------
        idn: str
            The ``*IDN?`` string.
        prefix: str
            The prefix used for each key (currently ``fw``, ``kmod``, ``sw``,
            or ``cfgMan``).

        Returns
        -------
        Optional[BuildInfo]
            The build information structure if data is available for the given
            key, or None if not.
        """
        build_data = {
            x[0]: x[1] for x in (s.split("=", maxsplit=1) for s in idn.split(",")[-1].split())
        }
        try:
            return cls(
                build_data[f"{prefix}Version"],
                build_data[f"{prefix}Build"],
                build_data[f"{prefix}Hash"],
                build_data[f"{prefix}Dirty"],
            )
        except KeyError:
            return None

    # ------------------------------------------------------------------------
    def to_idn(self, prefix: str = "") -> str:
        """
        Formats this build information object in the same way ``*IDN?`` is
        formatted.

        Parameters
        ----------
        prefix: str
            The prefix used for each key (currently ``fw``, ``kmod``, ``sw``,
            or ``cfgMan``).

        Returns
        -------
        str
            The part of the ``*IDN?`` string for this build information object.
        """
        return (
            f"{prefix}Version={self.version_str} "
            f"{prefix}Build={self.build_str} "
            f"{prefix}Hash=0x{self.hash:08X} "
            f"{prefix}Dirty={self.dirty_str}"
        )

    # ------------------------------------------------------------------------
    @classmethod
    def from_dict(cls, build_data: dict) -> "BuildInfo":
        """
        Constructs a build information structure from a JSON-capable dict,
        as used in ZeroMQ/CBOR descriptions, plug&play descriptions, update
        file metadata, and various other places.

        Parameters
        ----------
        build_data: dict
            Dictionary with (at least) the following keys:

             - ``"version"``: iterable of three integers representing the
               version;
             - ``"build"``: Unix timestamp in seconds representing the build
               timestamp;
             - ``"hash"``: the first 8 hex digits of the git hash as an
               integer; and
             - ``"dirty"``: boolean dirty flag.

        Returns
        -------
        BuildInfo
            The build information structure.
        """
        return cls(
            build_data["version"],
            build_data["build"],
            build_data["hash"],
            build_data["dirty"],
        )

    # ------------------------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Formats this build information object as a JSON-capable dict, as used
        in ZeroMQ/CBOR descriptions, plug&play descriptions, update file
        metadata, and various other places.

        Returns
        -------
        dict
            The generated dictionary, having the following keys:

             - ``"version"``: iterable of three integers representing the
               version;
             - ``"build"``: Unix timestamp in seconds representing the build
               timestamp;
             - ``"hash"``: the first 8 hex digits of the git hash as an
               integer; and
             - ``"dirty"``: boolean dirty flag.

        """
        return {
            "version": self.version,
            "build": self.build_unix,
            "hash": self.hash,
            "dirty": self.dirty,
        }

    # ------------------------------------------------------------------------
    def to_idn_dict(self) -> dict:
        """
        Formats this build information object as a human-readable JSON-capable dict,
        as used in get_idn.

        Returns
        -------
        dict
            The generated dictionary, having the following keys:

             - ``"version"``: string representation of the version;
             - ``"build"``: string representation of timestamp in seconds representing the build
               timestamp;
             - ``"hash"``: string representation of the first 8 hex digits of the git hash; and
             - ``"dirty"``: boolean dirty flag.

        """
        return {
            "version": self.version_str,
            "build": self.build_str,
            "hash": self.hash_str,
            "dirty": self.dirty,
        }

    # ------------------------------------------------------------------------
    def to_tuple(self) -> tuple:
        """
        Formats this build information object as a tuple for ordering purposes.

        Returns
        -------
        tuple
            A tuple, containing all the information in this structure in a
            canonical format.
        """
        return (self.version, self.build_unix, self.hash, self.dirty)

    # ------------------------------------------------------------------------
    def __str__(self) -> str:
        return (
            f"{self.version_str}, built on {self.build_iso} from git hash {self.hash_str}"
            f"{' (dirty)' if self.dirty else ''}"
        )


# --------------------------------------------------------------------------
@dataclass(frozen=True)
class DeviceBuildInfo:
    """
    Class representing build info for a complete device.
    """

    firmware: BuildInfo
    kernel_module: BuildInfo
    application: BuildInfo
    config_manager: BuildInfo

    @classmethod
    def from_idn(cls, idn: str) -> "BuildInfo":
        return cls(
            firmware=BuildInfo.from_idn(idn, "fw"),
            kernel_module=BuildInfo.from_idn(idn, "kmod"),
            application=BuildInfo.from_idn(idn, "sw"),
            config_manager=BuildInfo.from_idn(idn, "cfgMan"),
        )

    def to_idn(self) -> str:
        return " ".join(
            [
                self.firmware.to_idn("fw"),
                self.kernel_module.to_idn("kmod"),
                self.application.to_idn("sw"),
                self.config_manager.to_idn("cfgMan"),
            ]
        )


# --------------------------------------------------------------------------
class DeviceInfo:
    """
    Class representing the build and model information of a device. Has the
    same information content as what ``*DESCribe?`` returns.
    """

    __slots__ = [
        "_build",
        "_is_extended_instrument",
        "_is_rf",
        "_manufacturer",
        "_model",
        "_modules",
        "_name",
        "_serial",
    ]

    # ------------------------------------------------------------------------
    def __init__(
        self,
        manufacturer: str,
        model: str,
        name: str = "unknown",
        serial: Optional[str] = None,
        is_extended_instrument: bool = False,
        is_rf: bool = False,
        build: Optional[DeviceBuildInfo] = None,
        modules: Optional[dict[str, "DeviceInfo"]] = None,
    ) -> None:
        if not isinstance(manufacturer, str):
            raise TypeError("invalid type specified for manufacturer")
        self._manufacturer = manufacturer.replace(" ", "_").lower()

        if not isinstance(model, str):
            raise TypeError("invalid type specified for model")
        self._model = model.replace(" ", "_").lower()

        if not isinstance(name, str):
            raise TypeError("invalid type specified for name")
        self._name = name

        if serial is not None and not isinstance(serial, str):
            raise TypeError("invalid type specified for serial")
        self._serial = serial

        if not isinstance(is_extended_instrument, bool):
            raise TypeError("invalid type specified for is_extended_instrument")
        self._is_extended_instrument = is_extended_instrument

        if not isinstance(is_rf, bool):
            raise TypeError("invalid type specified for is_rf")
        self._is_rf = is_rf

        if build is not None and not isinstance(build, DeviceBuildInfo):
            raise TypeError("invalid type specified for build: %r")
        self._build = build

        if modules is not None and (
            not isinstance(modules, dict)
            or not all(isinstance(k, str) and isinstance(v, DeviceInfo) for k, v in modules.items())
        ):
            raise TypeError("invalid type specified for modules")
        self._modules = modules

    # ------------------------------------------------------------------------
    @property
    def manufacturer(self) -> str:
        """
        The manufacturer name, in lowercase_with_underscores format.

        :type: str
        """
        return self._manufacturer

    # ------------------------------------------------------------------------
    @property
    def model(self) -> str:
        """
        The model name, in lowercase_with_underscores format.

        :type: str
        """
        return self._model

    # ------------------------------------------------------------------------
    @property
    def name(self) -> str:
        """
        The customer-specified name of the instrument.

        :type: str
        """
        return self._name

    # ------------------------------------------------------------------------
    def update_name(self, new_name: str) -> None:
        """
        Update the name of the device if the new name is not "unknown".

        Parameters
        ----------
        new_name: str
            The new name to set.
        """
        if isinstance(new_name, str):
            self._name = new_name

    # ------------------------------------------------------------------------
    @property
    def is_extended_instrument(self) -> bool:
        """
        Indicates whether the module is an extended instrument.

        :type: bool
        """
        return self._is_extended_instrument

    # ------------------------------------------------------------------------
    @property
    def is_rf(self) -> bool:
        """
        Indicates whether the module has RF functionality.

        :type: bool
        """
        return self._is_rf

    # ------------------------------------------------------------------------
    @property
    def serial(self) -> Optional[str]:
        """
        The serial number, if known.

        :type: Optional[str]
        """
        return self._serial

    # ------------------------------------------------------------------------
    @property
    def build(self) -> Optional[DeviceBuildInfo]:
        """
        The device build information, if known.

        :type: Optional[DeviceBuildInfo]
        """
        return self._build

    @build.setter
    def build(self, build: Optional[DeviceBuildInfo]) -> None:
        self._build = build

    # ------------------------------------------------------------------------
    @property
    def sw_build(self) -> Optional[BuildInfo]:
        """
        The software/application build information, if known.

        :type: Optional[BuildInfo]
        """
        if self._build:
            return self._build.application
        return None

    # ------------------------------------------------------------------------
    @property
    def fw_build(self) -> Optional[BuildInfo]:
        """
        The FPGA firmware build information, if known.

        :type: Optional[BuildInfo]
        """
        if self._build:
            return self._build.firmware
        return None

    # ------------------------------------------------------------------------
    @property
    def kmod_build(self) -> Optional[BuildInfo]:
        """
        The kernel module build information, if known.

        :type: Optional[BuildInfo]
        """
        if self._build:
            return self._build.kernel_module
        return None

    # ------------------------------------------------------------------------
    @property
    def cfg_man_build(self) -> Optional[BuildInfo]:
        """
        The configuration management build information, if known.

        :type: Optional[BuildInfo]
        """
        if self._build:
            return self._build.config_manager
        return None

    # ------------------------------------------------------------------------
    @property
    def modules(self) -> Optional[dict[str, "DeviceInfo"]]:
        """
        The managed modules, if any.

        :type: Optional[dict[str, DeviceInfo]]
        """
        return self._modules

    # ------------------------------------------------------------------------
    def set_modules_from_idn(self, modules_description: dict[str, str]) -> None:
        self._modules = {
            module_id.lstrip("SLOT "): DeviceInfo.from_idn(module_data)
            for module_id, module_data in modules_description.items()
        }

    # ------------------------------------------------------------------------
    def get_build_info(self, key: str) -> Optional[BuildInfo]:
        """
        Returns build information for the given key.

        Parameters
        ----------
        key: str
            The key. Must be one of:

             - ``"sw"``: returns the application build info;
             - ``"fw"``: returns the FPGA firmware build info;
             - ``"kmod"``: returns the kernel module build info; or
             - ``"cfg_man"`` or ``"cfgMan"``: returns the configuration manager
               build info.

        Returns
        -------
        Optional[BuildInfo]
            The build information structure, if known.

        Raises
        ------
        KeyError
            For unknown keys.
        """
        if self._build is None:
            return None

        if key == "sw":
            return self._build.application
        elif key == "fw":
            return self._build.firmware
        elif key == "kmod":
            return self._build.kernel_module
        elif key in ("cfg_man", "cfgMan"):
            return self._build.config_manager
        else:
            raise KeyError(f"unknown key {key!r}")

    # ------------------------------------------------------------------------
    def __getitem__(self, key: str) -> BuildInfo:
        """
        Same as get_build_info(), but raises a KeyError if no data is known.

        Parameters
        ----------
        key: str
            The key. Must be one of:

             - ``"sw"``: returns the application build info;
             - ``"fw"``: returns the FPGA firmware build info;
             - ``"kmod"``: returns the kernel module build info; or
             - ``"cfg_man"`` or ``"cfgMan"``: returns the configuration
               manager build info.

        Returns
        -------
        BuildInfo
            The build information structure.

        Raises
        ------
        KeyError
            If no data is known for the given key or the key itself is unknown.
        """
        result = self.get_build_info(key)
        if result is None:
            raise KeyError(f"no data for key {key!r}")
        return result

    # ------------------------------------------------------------------------
    def __contains__(self, key: str) -> bool:
        """
        Returns whether data is known for the given key.

        Parameters
        ----------
        key: str
            The key. Must be one of:

             - ``"sw"``: returns the application build info;
             - ``"fw"``: returns the FPGA firmware build info;
             - ``"kmod"``: returns the kernel module build info; or
             - ``"cfg_man"`` or ``"cfgMan"``: returns the configuration
               manager build info.

        Returns
        -------
        bool
            Whether data is known.
        """
        try:
            return self.get_build_info(key) is not None
        except KeyError:
            return False

    # ------------------------------------------------------------------------
    @classmethod
    def from_idn(cls, idn: str) -> "DeviceInfo":
        """
        Constructs a device information structure from an ``*IDN?`` string.

        Parameters
        ----------
        idn: str
            The ``*IDN?`` string.

        Returns
        -------
        DeviceInfo
            The parsed device information structure.
        """

        manufacturer, model, *serial, build_data = idn.split(",")
        serial = serial[0] if serial else None
        device_build_info = DeviceBuildInfo.from_idn(build_data)

        return cls(
            manufacturer,
            model,
            "unknown",
            serial,
            False,  # Assuming default value
            False,  # Assuming default value
            device_build_info,
            None,
        )

    # ------------------------------------------------------------------------
    def to_idn(self) -> str:
        """
        Formats this device information object in the same way ``*IDN?`` is
        formatted.

        Returns
        -------
        str
            The ``*IDN?`` string.
        """
        idn = self._build.to_idn() if self._build else ""
        if self._serial is not None:
            idn = f"{self._serial},{idn}"
        idn = f"{self._manufacturer},{self._model},{idn}"
        return idn

    # ------------------------------------------------------------------------
    @classmethod
    def from_dict(cls, description: dict) -> "DeviceInfo":
        """
        Constructs a device information structure from a JSON-capable dict,
        as used in ZeroMQ/CBOR descriptions, plug&play descriptions, update
        file metadata, and various other places.

        Parameters
        ----------
        description: dict
            Dictionary with the following keys:

             - ``"manufacturer"``: manufacturer name (string);
             - ``"model"``: model name (string);
             - ``"name"``: device name (string);
             - ``"ser"``: serial number (string);
             - ``"is_extended_instrument"``: flag indicating if the device
               is an extended instrument (boolean);
             - ``"is_rf"``: flag indicating if the device has RF functionality (boolean);
             - ``"sw"``: application build information (dict);
             - ``"fw"``: FPGA firmware build information (dict);
             - ``"kmod"``: kernel module build information (dict);
             - ``"cfg_man"``: configuration management build information (dict);
             - ``"modules"``: dictionary of modules (optional).

        Returns
        -------
        DeviceInfo
            The build information structure.
        """
        return cls(
            description.get("manufacturer", "unknown"),
            description.get("model", "unknown"),
            description.get("name", "unknown"),
            description.get("ser"),
            description.get("is_extended_instrument", False),
            description.get("is_rf", False),
            DeviceBuildInfo(
                BuildInfo.from_dict(description["fw"]),
                BuildInfo.from_dict(description["kmod"]),
                BuildInfo.from_dict(description["sw"]),
                BuildInfo.from_dict(description["cfg_man"]),
            )
            if "fw" in description
            and "kmod" in description
            and "sw" in description
            and "cfg_man" in description
            else None,
            (
                {
                    module_id: DeviceInfo.from_dict(module_data)
                    for module_id, module_data in description.get("modules", {}).items()
                }
                if "modules" in description
                else None
            ),
        )

    # ------------------------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Formats this device information object as a JSON-capable dict, as used
        in ZeroMQ/CBOR descriptions, plug&play descriptions, update file
        metadata, and various other places.

        Returns
        -------
        dict
            The generated dictionary, having the following keys:

             - ``"manufacturer"``: manufacturer name (string);
             - ``"model"``: model name (string);
             - ``"name"``: device name (string);
             - ``"ser"``: serial number (string);
             - ``"is_extended_instrument"``: flag indicating if the device is an
                                             extended instrument (boolean);
             - ``"is_rf"``: flag indicating if the device has RF functionality
                            (boolean);
             - ``"sw"``: application build information (dict);
             - ``"fw"``: FPGA firmware build information (dict);
             - ``"kmod"``: kernel module build information (dict);
             - ``"cfg_man"``: configuration management build information (dict);
             - ``"modules"``: dictionary of modules (optional).

            Some keys may be omitted if the information is not available.
        """
        description = {}
        if self._manufacturer != "unknown":
            description["manufacturer"] = self._manufacturer
        if self._model != "unknown":
            description["model"] = self._model
        if self._name != "unknown":
            description["name"] = self._name
        description["is_extended_instrument"] = self._is_extended_instrument
        description["is_rf"] = self._is_rf
        if self._serial is not None:
            description["ser"] = self._serial
        for key in ("sw", "fw", "kmod", "cfg_man"):
            bi = self.get_build_info(key)
            if bi is not None:
                description[key] = bi.to_dict()
        if self._modules:
            description["modules"] = {
                module_id: module.to_dict() for module_id, module in self._modules.items()
            }

        return description

    # ------------------------------------------------------------------------
    def to_idn_dict(self) -> dict:
        """
        Formats this device information object as a human-readable
        JSON-capable dict, as used get_idn.

        Returns
        -------
        dict
            The generated dictionary, having the following keys:

             - ``"manufacturer"``: manufacturer name (string);
             - ``"model"``: model name (string);
             - ``"serial_number"``: serial number (string);
             - ``"firmware"``: build info (dict);
                - ``"fpga"``: FPGA firmware build information (dict);
                - ``"kernel_mod"``: kernel module build information (dict);
                - ``"application"``: application build information (dict); and
                - ``"driver"``: driver build information (dict);

            Some keys may be omitted if the information is not available.
        """
        description = {}
        if self._manufacturer != "unknown":
            description["manufacturer"] = self._manufacturer
        if self._model != "unknown":
            description["model"] = self._model
        if self._serial is not None:
            description["serial_number"] = self._serial
        description["firmware"] = {}
        for key, idn_key in zip(["fw", "kmod", "sw"], ["fpga", "kernel_mod", "application"]):
            bi = self.get_build_info(key)
            if bi is not None:
                description["firmware"][idn_key] = bi.to_idn_dict()
        description["firmware"]["driver"] = get_build_info().to_idn_dict()
        return description

    # ------------------------------------------------------------------------
    def to_tuple(self) -> tuple:
        """
        Formats this device information object as a tuple for ordering
        purposes.

        Returns
        -------
        tuple
            A tuple, containing all the information in this structure in a
            canonical format.
        """
        return (
            self._manufacturer,
            self._model,
            self._name,
            self._serial,
            self._is_extended_instrument,
            self._is_rf,
            self._build,
            tuple(sorted(self._modules)) if self._modules else None,
        )

    # ------------------------------------------------------------------------
    def __eq__(self, other) -> bool:
        if isinstance(other, DeviceInfo):
            return self.to_tuple() == other.to_tuple()

        return NotImplemented

    # ------------------------------------------------------------------------
    def __str__(self) -> str:
        return f"{self.manufacturer} {self.model}"

    # ------------------------------------------------------------------------
    def __hash__(self) -> int:
        return hash(self.to_tuple())


# -- functions -----------------------------------------------------------------


def get_build_info() -> BuildInfo:
    """
    Get build information for Qblox Instruments.

    Returns
    -------
    BuildInfo
        Build information structure for Qblox Instruments.
    """

    return BuildInfo(version="1.0.2", build="11/11/2025-14:33:33", hash="0xf8886029", dirty=False)


# Set version.
__version__ = get_build_info().version_str
