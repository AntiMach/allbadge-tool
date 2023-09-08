from dataclasses import dataclass, field

from badge_utils.modules.sarc import SARC


def read_string(data: bytes):
    return data.split(b"\0", 1)[0].decode("utf-8")


@dataclass
class BadgePrize:
    name: str
    collection_name: str
    data: bytes

    @classmethod
    def unpack(cls, data: bytes):
        return cls(
            read_string(data[0x44:0x74]),
            read_string(data[0x74:0xA4]),
            data,
        )


@dataclass
class BadgeCollection:
    name: str
    data: bytes

    @classmethod
    def unpack(cls, data: bytes):
        return cls(
            read_string(data[0x74:0xA4]),
            data,
        )


@dataclass
class AllbadgeData:
    prizes: list[BadgePrize] = field(default_factory=list)
    collections: list[BadgeCollection] = field(default_factory=list)

    @classmethod
    def unpack(cls, data: bytes):
        self = cls()

        for node in SARC.unpack(data).nodes:
            path = node.get_file_path()

            if path.suffix == ".prb":
                self.prizes.append(BadgePrize.unpack(node.get_data()))

            if path.suffix == ".cab":
                self.collections.append(BadgeCollection.unpack(node.get_data()))

        return self
