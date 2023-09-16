from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(".").resolve()


@dataclass
class Version:
    name: str
    version: str
    value: str

    @property
    def url(self) -> str:
        return f"https://npdl.cdn.nintendowifi.net/p01/nsa/{self.value}/data/allbadge_v{self.version}.dat?tm=2"

    @property
    def dat(self) -> str:
        return f"allbadge_v{self.version}_{self.name}.dat"

    @property
    def sarc(self) -> str:
        return f"allbadge_v{self.version}_{self.name}.sarc"

    @property
    def zip(self) -> str:
        return f"allbadge_v{self.version}_{self.name}.zip"


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
