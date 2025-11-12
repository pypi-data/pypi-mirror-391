import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

import py7zr
import rarfile


@dataclass
class ArchiveEntry:
    """Representation of a file or directory within an archive."""

    name: str
    size: Optional[int] = None
    compressed: Optional[int] = None
    is_dir: bool = False

    @property
    def display_size(self) -> str:
        """Return a human-friendly string for the file size."""
        if (size := self.size) is None:
            return ""
        # Convert bytes to a more readable format
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024:
                return f"{size:.0f} {unit}"
            size /= 1024
        return f"{size:.0f} PB"


class Archiver:
    def get_file_list(self, path: Path) -> List[ArchiveEntry]: ...
    def matches_filetype(self, path: Path) -> bool: ...
    def extract(self, path: Path,
                entries: Optional[Sequence[ArchiveEntry]], dest: Path) -> None: ...


class ZipArchiver(Archiver):
    def get_file_list(self, path: Path):
        entries: List[ArchiveEntry] = []
        with zipfile.ZipFile(path, "r") as zf:
            for info in zf.infolist():
                entries.append(
                    ArchiveEntry(
                        name=info.filename,
                        size=info.file_size,
                        compressed=info.compress_size,
                        is_dir=info.is_dir(),
                    )
                )
        return entries

    def extract(self, path: Path, entries: Optional[Sequence[ArchiveEntry]], dest: Path) -> None:
        with zipfile.ZipFile(path, "r") as zf:
            if entries is None:
                zf.extractall(path=dest)
            else:
                for entry in entries:
                    if not entry.is_dir:
                        zf.extract(entry.name, path=dest)

    def matches_filetype(self, path: Path):
        ext = path.suffix.lower()
        return ext == ".zip"


class SevenZipArchiver(Archiver):
    def get_file_list(self, path: Path):
        entries: List[ArchiveEntry] = []
        with py7zr.SevenZipFile(path, mode="r") as sz:
            # getnames returns names only; getinfo returns FileInfo objects
            for name in sz.getnames():
                info = sz.getinfo(name)  # type: ignore[no-untyped-call]
                entries.append(
                    ArchiveEntry(
                        name=name,
                        size=info.uncompressed,
                        compressed=info.compressed,
                        is_dir=info.is_directory,
                    )
                )
        return entries

    def extract(self, path: Path, entries: Optional[Sequence[ArchiveEntry]], dest: Path) -> None:
        with py7zr.SevenZipFile(path, mode="r") as sz:
            if entries is None:
                sz.extractall(path=dest)
            else:
                targets = [e.name for e in entries]
                sz.extract(path=dest, targets=targets)

    def matches_filetype(self, path: Path):
        ext = path.suffix.lower()
        return ext == ".7z"


class RarArchiver(Archiver):
    def get_file_list(self, path: Path):
        entries: List[ArchiveEntry] = []
        with rarfile.RarFile(path) as rf:
            for info in rf.infolist():
                entries.append(
                    ArchiveEntry(
                        name=info.filename,
                        size=info.file_size,
                        compressed=info.compress_size,
                        is_dir=info.isdir(),
                    )
                )
        return entries

    def extract(self, path: Path, entries: Optional[Sequence[ArchiveEntry]], dest: Path) -> None:
        with rarfile.RarFile(path) as rf:
            if entries is None:
                rf.extractall(path=dest)
            else:
                for entry in entries:
                    if not entry.is_dir:
                        rf.extract(entry.name, path=dest)

    def matches_filetype(self, path: Path):
        ext = path.suffix.lower()
        return ext == ".rar"


class TarArchiver(Archiver):
    def get_file_list(self, path: Path):
        entries: List[ArchiveEntry] = []
        with tarfile.open(path, "r:*") as tar:
            for member in tar.getmembers():
                entries.append(
                    ArchiveEntry(
                        name=member.name,
                        size=member.size if member.isfile() else None,
                        compressed=None,
                        is_dir=member.isdir(),
                    )
                )
        return entries

    def extract(self, path: Path, entries: Optional[Sequence[ArchiveEntry]], dest: Path) -> None:
        with tarfile.open(path, "r:*") as tar:
            if entries is None:
                tar.extractall(path=dest)
            else:
                members = [m for m in tar.getmembers() if m.name in {
                    e.name for e in entries}]
                tar.extractall(path=dest, members=members)

    def matches_filetype(self, path: Path):
        ext = path.suffix.lower()
        return path.name.lower().endswith((".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz", ".tar.zst")) or ext == ".tar"


ARCHIVERS: List[Archiver] = [ZipArchiver(), SevenZipArchiver(),
                             RarArchiver(), TarArchiver()]


def create_archiver_for(path: Path) -> Optional[Archiver]:
    for archiver in ARCHIVERS:
        if archiver.matches_filetype(path):
            return archiver

    return None
