from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(".").resolve()


@dataclass
class Version:
    BASE_FORMAT = "allbadge_v{version}_{name}.{ext}"
    name: str
    version: str | None
    value: str | None

    @property
    def url(self) -> str | None:
        return f"https://npdl.cdn.nintendowifi.net/p01/nsa/{self.value}/data/allbadge_v{self.version}.dat?tm=2"

    @property
    def dat(self) -> str | None:
        return self.BASE_FORMAT.format(version=self.version, name=self.name, ext="dat")

    @property
    def sarc(self) -> str:
        return self.BASE_FORMAT.format(version=self.version, name=self.name, ext="sarc")

    @property
    def zip(self) -> str:
        return self.BASE_FORMAT.format(version=self.version, name=self.name, ext="zip")


class PCVersion(Version):
    BASE_FORMAT = "pc_{name}.{ext}"

    @property
    def url(self) -> None:
        return None

    @property
    def dat(self) -> None:
        return None


VERSIONS_130 = {
    "USA v130": Version("USA", 130, "OvbmGLZ9senvgV3K"),
    "EUR v130": Version("EUR", 130, "J6la9Kj8iqTvAPOq"),
    "JPN v130": Version("JPN", 130, "j0ITmVqVgfUxe0O9"),
}

VERSIONS_131 = {
    "USA v131": Version("USA", 131, "OvbmGLZ9senvgV3K"),
    "EUR v131": Version("EUR", 131, "J6la9Kj8iqTvAPOq"),
    "JPN v131": Version("JPN", 131, "j0ITmVqVgfUxe0O9"),
}

VERSIONS_PC = {
    "pc USA": PCVersion("USA", None, None),
    "pc EUR": PCVersion("EUR", None, None),
    "pc JPN": PCVersion("JPN", None, None),
}
