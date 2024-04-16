import asyncio
from pathlib import Path
from zipfile import ZipFile
from abc import ABC, abstractmethod

from allbadge_tool.ctr.boss import BOSS
from allbadge_tool.ctr.sarc import SARC
from allbadge_tool.ctr.boot9 import Boot9
from allbadge_tool.ctr.allbadge import badge_element_factory

from allbadge_tool.misc.beep import beep
from allbadge_tool.misc.const import Version
from allbadge_tool.misc.asyncdl import AsyncDownloader


class Program(ABC):
    @property
    @abstractmethod
    def versions(self) -> list[Version]:
        "List of versions to download"
        ...

    @property
    @abstractmethod
    def boot9_path(self) -> Path:
        "Location of the boot9.bin file"
        ...

    @property
    @abstractmethod
    def data_path(self) -> Path:
        "Location of the data folder"
        ...

    @abstractmethod
    def set_progress(self, text: str, ratio: float):
        "Recieves progress messages"
        ...

    @abstractmethod
    def set_error(self, error: str):
        "Receives error messages"
        ...

    @abstractmethod
    def log_message(self, message: str):
        "Receives generic log messages"
        ...

    @abstractmethod
    def start(self): ...

    @abstractmethod
    def end(self): ...

    def begin(self):
        """
        Begins the 3 step process to get badge data:
        - Download files
        - Decrypt files
        - Unpack files

        When an unexpected error occurs, execution is stopped
        """

        self.start()

        try:
            self._begin()

        except FileNotFoundError as e:
            self.log_message(f"File not found: {e.filename}")
            self.set_error(f"File not found: {e.filename}")

        except Exception as e:
            self.set_error(e.args[0])

        beep()
        self.end()

    def _begin(self):
        self.boot9 = Boot9.unpack(self.boot9_path.read_bytes())
        self.boss_key = self.boot9.get_keys(0x38).normal_key

        if not self.versions:
            raise Exception("No versions selected")

        asyncio.run(self.download_files())
        self.decrypt_files()
        self.repack_files()
        self.set_progress("Done", 1)

    # Step 1. Download files

    async def download_files(self):
        self.download_progress(0)

        self.log_message("1. Downloading files")

        async with AsyncDownloader() as downloader:
            downloader.set_progress_callback(self.download_progress)
            downloader.set_done_callback(self.download_done)

            for version in self.versions:
                downloader.add_entry(*self.download_entry(version))

    def download_entry(self, version: Version) -> tuple[str, Path] | tuple[()]:
        if version.url is None or version.dat is None:
            return ()

        file = self.data_path / version.dat

        if file.is_file():
            self.file_done(file.name, on_disk=True)
            return ()

        return (version.url, file)

    def download_done(self, file: Path, error: Exception | None):
        return self.file_done(file.name, error)

    # Step 2. Decrypt files

    def decrypt_files(self):
        self.decrypt_progress(0)
        self.log_message("2. Decrypting files")

        for i, version in enumerate(self.versions, 1):
            try:
                self.decrypt_file(i, version)
            except Exception as e:
                self.file_done(version.sarc, e)

    def decrypt_file(self, i: int, version: Version):
        if version.dat is None:
            return

        in_file = self.data_path / version.dat
        out_file = self.data_path / version.sarc

        if out_file.is_file():
            self.decrypt_progress(i)
            self.file_done(version.sarc, on_disk=True)
            return

        boss = BOSS.unpack(in_file.read_bytes())
        out_file.write_bytes(boss.decrypt(self.boss_key))

        self.decrypt_progress(i)
        self.file_done(version.sarc)

    # Step 3. Repack files

    def repack_files(self):
        self.repack_progress(0)
        self.log_message("3. Repacking files")

        for i, version in enumerate(self.versions):
            try:
                self.repack_file(i, version)
            except FileNotFoundError as e:
                self.file_done(version.sarc, e)
            except Exception as e:
                self.file_done(version.zip, e)

    def repack_file(self, i: int, version: Version):
        in_path = self.data_path / version.sarc
        out_path = self.data_path / version.zip

        if out_path.is_file():
            self.file_done(version.zip, on_disk=True)
            return

        sarc = SARC.unpack(in_path.read_bytes())

        with ZipFile(out_path, "w") as fp:
            for j, entry in enumerate(sarc.entries, 1):
                if badge := badge_element_factory(entry):
                    fp.writestr(badge.path, badge.data)

                self.repack_progress(i + j / sarc.node_count)

        self.file_done(version.zip)

    # Helper methods

    def download_progress(self, ratio: float):
        self.set_progress("Downloading", ratio)

    def decrypt_progress(self, file_ratio: float):
        self.set_progress("Decrypting", file_ratio / len(self.versions))

    def repack_progress(self, file_ratio: float):
        self.set_progress("Repacking", file_ratio / len(self.versions))

    def file_done(self, out_name: str, error: Exception | None = None, on_disk: bool = False):
        if isinstance(error, FileNotFoundError):
            self.log_message(f"\t❓ {out_name}")
        elif error:
            self.log_message(f"\t❌ {out_name}")
            self.log_message(f"\tReason: {error}")
        elif on_disk:
            self.log_message(f"\t💾 {out_name}")
        else:
            self.log_message(f"\t✔ {out_name}")
