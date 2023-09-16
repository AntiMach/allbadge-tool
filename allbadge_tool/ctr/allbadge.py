from dataclasses import dataclass

from allbadge_tool.ctr.sarc import SFATEntry


def read_string(data: bytes):
    return data.split(b"\0", 1)[0].decode("utf-8")


def allbadge_factory(entry: SFATEntry):
    if entry.file_path.suffix == ".prb":
        return BadgePrize.unpack(entry.file_data)

    if entry.file_path.suffix == ".cab":
        return BadgeCollection.unpack(entry.file_data)


@dataclass
class BadgePrize:
    name: str
    collection_name: str
    data: bytes

    @classmethod
    def unpack(cls, data: bytes):
        return cls(read_string(data[0x44:0x74]), read_string(data[0x74:0xA4]), data)

    @property
    def path(self):
        return f"{self.collection_name}/{self.name}.prb"


@dataclass
class BadgeCollection:
    name: str
    data: bytes

    @classmethod
    def unpack(cls, data: bytes):
        return cls(
            read_string(data[0x2C:0x5C]),
            data,
        )

    @property
    def path(self):
        return f"{self.name}/{self.name}.cab"
