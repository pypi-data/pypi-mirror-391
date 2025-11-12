# ----------------------------------------------------------------------------
# Description    : Update file format utilities
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------
import configparser
import json
import os
import re
import tarfile
import tempfile
import zipfile
from collections.abc import Iterable, Mapping
from enum import Enum, auto
from typing import IO, Any, BinaryIO, Callable, Optional

from PySquashfsImage import SquashFsImage

from qblox_instruments.build import DeviceInfo
from qblox_instruments.cfg_man import log
from qblox_instruments.cfg_man.const import VERSION
from qblox_instruments.cfg_man.probe import ConnectionInfo


# ----------------------------------------------------------------------------
class ArchiveType(Enum):
    ZIP = auto()
    TAR_GZ = auto()
    TAR_XZ = auto()
    TAR_BZ2 = auto()
    TAR = auto()
    SQUASHFS = auto()


class ArchiveExtension(Enum):
    ZIP = auto()
    TAR_GZ = auto()
    TAR_XZ = auto()
    TAR_BZ2 = auto()
    TAR = auto()
    RAUC_BUNDLE = auto()


UPDATE_V1_ARCHIVE_TYPES = {
    ArchiveType.TAR,
    ArchiveType.TAR_BZ2,
    ArchiveType.TAR_GZ,
    ArchiveType.TAR_XZ,
    ArchiveType.ZIP,
}


RAUC_MANIFEST_FILE = "manifest.raucm"


class UpdateFile:
    """
    Representation of a device update file.
    """

    __slots__ = [
        "_fname",
        "_format",
        "_metadata",
        "_models",
        "_tempdir",
        "_update_fname",
    ]

    # ------------------------------------------------------------------------
    def __init__(self, fname: str, check_version: bool = True) -> None:
        """
        Loads an update file.

        Parameters
        ----------
        fname: str
            The file to load.
        check_version: bool
            Whether to throw a NotImplementedError if the minimum
            configuration management client version reported by the update
            file is newer than our client version.
        """
        super().__init__()

        # Save filename.
        self._fname = fname

        # Be lenient: if the user downloaded a release file and forgot to
        # extract it, extract it for them transparently.
        self._update_fname = None
        self._tempdir = None

        # Type declarations
        self._format: str
        self._metadata: dict[str, Any]
        self._models: Mapping[str, DeviceInfo]

        def extract(fin: IO[bytes]) -> None:
            log.debug(
                '"%s" looks like a release file, extracting update.tar.gz from it...',
                self._fname,
            )
            self._tempdir = tempfile.TemporaryDirectory()
            self._update_fname = os.path.join(self._tempdir.__enter__(), "update.tar.gz")
            with open(self._update_fname, "wb") as fout:
                while True:
                    buf = fin.read(4096)
                    if not buf:
                        break
                    while buf:
                        buf = buf[fout.write(buf) :]

        with open(self._fname, "rb") as f:
            archive_type = _detect_archive_type_magic(f)
        archive_extension = _detect_archive_extension(self._fname)

        if archive_type in UPDATE_V1_ARCHIVE_TYPES:
            try:
                log.debug('Determining file type of "%s"...', self._fname)
                with tarfile.TarFile.open(self._fname, "r:*") as tar_obj:
                    for name in tar_obj.getnames():
                        if name.endswith("update.tar.gz"):
                            with tar_obj.extractfile(name) as fin:
                                extract(fin)
                            break
                    else:
                        log.debug(
                            '"%s" looks like it might indeed be an update file.',
                            self._fname,
                        )
                        self._update_fname = self._fname
            except tarfile.TarError as err:
                log.debug(f"Error while trying to open {self._fname} as tar file.\n{err}")
                try:
                    with zipfile.ZipFile(self._fname, "r") as zip_obj:
                        for name in zip_obj.namelist():
                            if name.endswith("update.tar.gz"):
                                with zip_obj.open(name, "r") as fin:
                                    extract(fin)
                                break
                except zipfile.BadZipFile as err:
                    log.debug(f"Error while trying to open {self._fname} as zip file.\n{err}")
                    pass
            if self._update_fname is None:
                raise ValueError("invalid update file")

            # Read the tar file.
            try:
                log.debug('Scanning update tar file "%s"...', self._update_fname)
                with tarfile.TarFile.open(self._update_fname, "r:gz") as tar:
                    fmts: set[str] = set()
                    meta_json = None
                    models: set[str] = set()
                    metadata: dict[str, Any] = {}
                    for info in tar:
                        if info is None:
                            break
                        name = info.name
                        log.debug("  %s", name)
                        if name.startswith("."):
                            name = name[1:]
                        if name.startswith("/") or name.startswith("\\"):
                            name = name[1:]
                        name, *tail = re.split(r"/|\\", name, maxsplit=1)
                        if name == "meta.json" and not tail:
                            fmts.add("multi")
                            meta_json = info
                        elif name.startswith("only_"):
                            name = name[5:]
                            if name not in models:
                                fmts.add("multi")
                                metadata[name] = {
                                    "manufacturer": "qblox",
                                    "model": name,
                                }
                                models.add(name)
                        elif name == "common":
                            fmts.add("multi")
                        elif _detect_archive_extension(info.name) == ArchiveExtension.RAUC_BUNDLE:
                            with tar.extractfile(info.name) as sqfs:
                                if _detect_archive_type_magic(sqfs) == ArchiveType.SQUASHFS:
                                    imgbytes = sqfs.read()
                                    manifest = _read_rauc_manifest_bytes(imgbytes)
                                    if manifest:
                                        parsedmanifest = self._parse_rauc_manifest(manifest)
                                    else:
                                        raise RuntimeError("No manifest in RAUC bundle")
                                    models.add(parsedmanifest["update"]["compatible"])
                                    fmts.add("raucb")

                    log.debug("Scan complete")
                    log.debug("")
                    if meta_json is not None:
                        with tar.extractfile(meta_json) as f:
                            metadata.update(json.loads(f.read()))
                    self._process_update_file(fmts, metadata, models)

            except tarfile.TarError as err:
                log.debug(f"Error while trying to open {self._fname} as tar file.\n{err}")
                raise ValueError("invalid update file")

            # Check client version.
            if check_version and (
                self._metadata.get("meta", {}).get("min_cfg_man_client", (0, 0, 0)) > VERSION
            ):
                raise NotImplementedError(
                    "update file format is too new. Please update Qblox Instruments first"
                )
        elif (
            archive_type == ArchiveType.SQUASHFS
            and archive_extension == ArchiveExtension.RAUC_BUNDLE
        ):
            log.info("Seems to be a RAUC bundle! (squashfs type and raucb extension)")
            manifest = _read_rauc_manifest_path(self._fname)
            if manifest:
                parsedmanifest = self._parse_rauc_manifest(manifest)
            else:
                raise RuntimeError("No manifest in RAUC bundle")
            self._process_update_file(
                fmts={"raucb"}, metadata={}, models={parsedmanifest["update"]["compatible"]}
            )
        else:
            raise ValueError("invalid update file")

    def _process_update_file(
        self, fmts: set[str], metadata: dict[str, Any], models: set[str]
    ) -> None:
        if len(fmts) != 1:
            raise ValueError("invalid update file")
        self._format = next(iter(fmts))
        if self._format != "raucb":
            self._models = {
                model: DeviceInfo.from_dict(metadata[model]) for model in sorted(models)
            }
            self._metadata = metadata.get("meta", {})
        else:
            self._metadata = {}
            self._update_fname = self._fname
            self._models = {model: {} for model in sorted(models)}

    def _parse_rauc_manifest(self, content: str) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config.read_string(content)
        return config

    # ------------------------------------------------------------------------
    def close(self) -> None:
        """
        Cleans up any operating resources that we may have claimed.
        """
        if hasattr(self, "_tempdir") and self._tempdir is not None:
            self._tempdir.cleanup()
            self._tempdir = None

    # ------------------------------------------------------------------------
    def __del__(self) -> None:
        self.close()

    # ------------------------------------------------------------------------
    def __enter__(self) -> "UpdateFile":
        return self

    # ------------------------------------------------------------------------
    def __exit__(self, exc_type, exc_value, traceback) -> Optional[bool]:
        self.close()

    # ------------------------------------------------------------------------
    def needs_confirmation(self) -> Optional[str]:
        """
        Returns whether the update file requests the user to confirm something
        before application, and if so, what message should be printed.

        Returns
        -------
        Optional[str]
            None if there is nothing exceptional about this file, otherwise
            this is the confirmation message.
        """
        return self._metadata.get("confirm", None)

    # ------------------------------------------------------------------------
    def __str__(self) -> str:
        return self._fname

    # ------------------------------------------------------------------------
    def __repr__(self) -> str:
        return repr(self._fname)

    # ------------------------------------------------------------------------
    def summarize(self) -> str:
        """
        Returns a summary of the update file format.

        Returns
        -------
        str
            Update file summary.
        """
        return f"update file for {', '.join(self._models)}"

    # ------------------------------------------------------------------------
    def pprint(self, output: Callable[[str], None] = log.info) -> None:
        """
        Pretty-prints the update file metadata.

        Parameters
        ----------
        output: Callable[[str], None]
            The function used for printing. Each call represents a line.
        """
        min_client = self._metadata.get("min_cfg_man_client", None)
        if min_client is not None:
            min_client = ".".join(map(str, min_client))

        query_message = self._metadata.get("confirm", "None")

        output(f"Update file              : {self._fname}")
        output(f"File format              : {self._format}")
        output(f"Minimum client version   : {min_client}")
        output(f"Query message            : {query_message}")
        output(f"Contains updates for     : {len(self._models)} product(s)")
        for model, di in self._models.items():
            output(f"  Model                  : {model}")
            for key, pretty in (
                ("sw", "Application"),
                ("fw", "FPGA firmware"),
                ("kmod", "Kernel module"),
                ("cfg_man", "Cfg. manager"),
            ):
                if key in di:
                    output(f"    {pretty + ' version':<21}: {di[key]}")

    # ------------------------------------------------------------------------
    def load(
        self,
        ci: ConnectionInfo,
        included_slots: Optional[Iterable[int]] = None,
        excluded_slots: Optional[Iterable[int]] = None,
    ) -> BinaryIO:
        """
        Loads an update file, checking whether the given update file is
        compatible within the given connection context. Returns a file-like
        object opened in binary read mode if compatible, or throws a
        ValueError if there is a problem.

        Parameters
        ----------
        ci: ConnectionInfo
            Connection information object retrieved from autoconf(), to verify
            that the update file is compatible, or to make it compatible, if
            possible.
        included_slots: Optional[Iterable[int]]
            list of included slot indices. Optional, by default None.
        excluded_slots: Optional[Iterable[int]]
            list of excluded slot indices. Optional, by default None.

        Returns
        -------
        BinaryIO
            Binary file-like object for the update file. Will at least be
            opened for reading, and rewound to the start of the file. This may
            effectively be ``open(fname, "rb")``, but could also be a
            ``tempfile.TemporaryFile`` to an update file specifically
            converted to be compatible with the given environment. It is the
            responsibility of the caller to close the file.

        Raises
        ------
        ValueError
            If there is a problem with the given update file.
        """

        # Check whether the update includes data for all the devices we need to
        # support.
        log.info(f"Models In Cluster        : {sorted(ci.all_updatable_models)}")
        log.info(f"Models In Update Package : {sorted(set(self._models.keys()))}")

        incompatible_modules = set()

        def check_update_compatibility(slot: int, model: str) -> None:
            """
            Check if the given update file is compatible within the cluster.
            Take into account included and excluded slots: a module is not considered
            incompatible if it is also excluded from the update.
            :param slot:    slot number to check for
            :param model:   model name of module in slot
            """
            if model.endswith("qdm"):
                return

            if (model not in self._models) and (
                (included_slots is None and excluded_slots is None)
                or (included_slots is not None and slot in included_slots)
                or (excluded_slots is not None and slot not in excluded_slots)
            ):
                incompatible_modules.add(model)

        if ci.slot_index is not None:
            # Single slot update
            model = next(iter(ci.all_updatable_models))
            slot_no = int(ci.slot_index)
            log.info(f"Single-Slot Update in slot {slot_no}")
            check_update_compatibility(slot_no, model)

        elif ci.device.modules is not None:
            # Multiple slots update
            log.info("Multi-Slot Update")
            for slot, module in ci.device.modules.items():
                model = module.model
                slot_no = int(slot)
                check_update_compatibility(slot_no, model)

        else:
            raise RuntimeError("failed to determine update compatibility for update file")

        incompatible_modules = list(sorted(incompatible_modules))
        if incompatible_modules:
            if len(incompatible_modules) == 1:
                to_print = incompatible_modules[0]
            else:
                to_print = ", ".join(incompatible_modules[:-1]) + " and " + incompatible_modules[-1]
            raise ValueError(f"update file is not compatible with {to_print} devices")

        # No need to change the contents of the update file, so just open the
        # file as-is.
        return open(self._update_fname, "rb")


def _detect_archive_type_magic(file_obj: IO[bytes]) -> Optional[ArchiveType]:
    if not file_obj.seekable():
        return None
    header = file_obj.read(264)
    file_obj.seek(0)

    """
    Detect archive/image type based on magic bytes.

    Parameters
    ----------
    filepath: str
        The file to load.

    Returns
    -------
    ArchiveType
        An Enum with the different file types or None if not supported.
    """
    # with open(filepath, "rb") as f:
    # header = f.read(264)
    magic_type: Optional[ArchiveType] = None
    if header.startswith(b"\x50\x4b\x03\x04"):
        magic_type = ArchiveType.ZIP
    elif header.startswith(b"\x1f\x8b"):
        magic_type = ArchiveType.TAR_GZ
    elif header.startswith(b"\xfd\x37\x7a\x58\x5a\x00"):
        magic_type = ArchiveType.TAR_XZ
    elif header.startswith(b"\x42\x5a\x68"):
        magic_type = ArchiveType.TAR_BZ2
    elif header.startswith(b"hsqs"):
        # squashfs of rauc bundles has 'hsqs' ie 0x73717368 magic number
        magic_type = ArchiveType.SQUASHFS
    elif len(header) >= 262 and (header[257:262] in [b"ustar", b"ustar\x00"]):
        # Tar files do not have a fixed magic at the beginning,
        # but the ustar signature is at byte offset 257
        magic_type = ArchiveType.TAR

    return magic_type


def _detect_archive_extension(filepath: str) -> Optional[ArchiveExtension]:
    """
    Detects the archive type based on file extension.

    Parameters
    ----------
    filepath: str
        The file to load.

    Returns
    -------
    ArchiveExtension
        An Enum file extension type, 'zip', 'tar.gz', 'tar.xz', 'tar.bz2', 'tar', 'raucb'
        or None if not supported
    """
    filename = os.path.basename(filepath).lower()

    extension = None
    if filename.endswith((".zip",)):
        extension = ArchiveExtension.ZIP
    elif filename.endswith((".tar.gz", ".tgz")):
        extension = ArchiveExtension.TAR_GZ
    elif filename.endswith((".tar.xz", ".txz")):
        extension = ArchiveExtension.TAR_XZ
    elif filename.endswith((".tar.bz2", ".tbz2")):
        extension = ArchiveExtension.TAR_BZ2
    elif filename.endswith((".tar",)):
        extension = ArchiveExtension.TAR
    elif filename.endswith((".raucb",)):
        extension = ArchiveExtension.RAUC_BUNDLE

    return extension


def _read_rauc_manifest(fobj: [str, bytes]) -> Optional[str]:
    # Use SquashFsImage.from_file as default image object constructor
    # Use SquashFsImage.from_bytes if it is applicable.
    image_constructor = SquashFsImage.from_bytes if type(fobj) is bytes else SquashFsImage.from_file
    with image_constructor(fobj) as image:
        manifest = image.find("manifest.raucm")
        if manifest is not None:
            return manifest.read_bytes().decode("utf-8")
    return None


def _read_rauc_manifest_path(fpath: str) -> Optional[str]:
    with open(fpath, "rb") as f:
        return _read_rauc_manifest(f)


def _read_rauc_manifest_bytes(fdata: bytes) -> Optional[str]:
    return _read_rauc_manifest(fdata)
