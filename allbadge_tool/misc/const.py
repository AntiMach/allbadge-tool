from pathlib import Path
from dataclasses import dataclass
from typing import Any, ClassVar

BASE_DIR = Path(".").resolve()


class Version:
    BASE_FORMAT: ClassVar[str]

    name: Any
    version: Any

    @property
    def sarc(self) -> str:
        return self.BASE_FORMAT.format(version=self.version, name=self.name, ext="sarc")

    @property
    def zip(self) -> str:
        return self.BASE_FORMAT.format(version=self.version, name=self.name, ext="zip")


@dataclass
class CDNVersion(Version):
    BASE_FORMAT = "allbadge{version}_{name}.{ext}"

    name: str
    version: str
    value: str

    @property
    def url(self) -> str:
        return f"https://npdl.cdn.nintendowifi.net/p01/nsa/{self.value}/data/allbadge{self.version}.dat?tm=2"

    @property
    def dat(self) -> str:
        return self.BASE_FORMAT.format(version=self.version, name=self.name, ext="dat")


@dataclass
class PCVersion(Version):
    BASE_FORMAT = "pc_{name}.{ext}"

    name: str
    version: None = None


USA_REGION_CODE = "OvbmGLZ9senvgV3K"
EUR_REGION_CODE = "J6la9Kj8iqTvAPOq"
JPN_REGION_CODE = "j0ITmVqVgfUxe0O9"

VERSIONS_100 = {
    "JPN v100": CDNVersion("JPN", "", JPN_REGION_CODE),
}

VERSIONS_130 = {
    "USA v130": CDNVersion("USA", "_v130", USA_REGION_CODE),
    "EUR v130": CDNVersion("EUR", "_v130", EUR_REGION_CODE),
    "JPN v130": CDNVersion("JPN", "_v130", JPN_REGION_CODE),
}

VERSIONS_131 = {
    "USA v131": CDNVersion("USA", "_v131", USA_REGION_CODE),
    "EUR v131": CDNVersion("EUR", "_v131", EUR_REGION_CODE),
    "JPN v131": CDNVersion("JPN", "_v131", JPN_REGION_CODE),
}

VERSIONS_PC = {
    "pc USA": PCVersion("USA"),
    "pc EUR": PCVersion("EUR"),
    "pc JPN": PCVersion("JPN"),
}
