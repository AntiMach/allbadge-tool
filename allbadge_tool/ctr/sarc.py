"""
Original code by SciresM @ https://github.com/SciresM/BadgeArcadeTool/blob/master/BadgeArcadeTool/SARC.cs
"""

import struct
import hashlib
from io import BytesIO
from pathlib import Path
from dataclasses import dataclass, field
from typing import Iterator

from allbadge_tool.ctr.yaz0 import yaz0_decompress


@dataclass(slots=True)
class SFATNode:
    file_name_hash: int
    file_name_offset: int
    file_data_start: int
    file_data_end: int

    @classmethod
    def unpack(cls, fs: BytesIO):
        return cls(*struct.unpack("<IIII", fs.read(16)))


@dataclass(slots=True)
class SFAT:
    header_size: int
    entry_count: int
    hash_mult: int
    nodes: list[SFATNode] = field(default_factory=list, repr=False)

    @classmethod
    def unpack(cls, fs: BytesIO):
        if fs.read(4) != b"SFAT":
            raise AttributeError("Invalid SFAT header")

        self = cls(*struct.unpack("<HHI", fs.read(8)))

        self.nodes.extend(SFATNode.unpack(fs) for _ in range(self.entry_count))

        return self


@dataclass(slots=True)
class SFNT:
    header_size: int
    unknown: int
    string_offset: int

    @classmethod
    def unpack(cls, fs: BytesIO):
        if fs.read(4) != b"SFNT":
            raise AttributeError("Invalid SFNT header")

        return cls(*struct.unpack("<HH", fs.read(4)), fs.tell())


@dataclass(slots=True, frozen=True)
class SFATEntry:
    sarc: "SARC"
    node: SFATNode

    @property
    def file_path(self):
        return self.sarc.get_decompressed_file_path(self.node)

    @property
    def file_hash(self):
        return self.sarc.get_file_hash(self.node)

    @property
    def file_data(self):
        return self.sarc.get_decompressed_data(self.node)


@dataclass(slots=True)
class SARC:
    data: bytes = field(repr=False)
    header_size: int = 0x14
    endianness: int = 0
    file_size: int = 0
    data_offset: int = 0
    unknown: int = 0
    sfat: SFAT = None
    sfnt: SFNT = None

    @classmethod
    def unpack(cls, data: bytes):
        self = cls(data)

        with BytesIO(self.data) as fs:
            if fs.read(4) != b"SARC":
                raise AttributeError("Invalid SARC header")

            (
                self.header_size,
                self.endianness,
                self.file_size,
                self.data_offset,
                self.unknown,
            ) = struct.unpack("<HHIII", fs.read(16))

            self.sfat = SFAT.unpack(fs)
            self.sfnt = SFNT.unpack(fs)

        if self.file_size != len(self.data):
            raise AttributeError("Specified file is not valid (incorrect file size)")

        return self

    @property
    def nodes(self) -> list[SFATNode]:
        return self.sfat.nodes

    @property
    def entries(self) -> Iterator[SFATEntry]:
        for node in self.nodes:
            yield SFATEntry(self, node)

    def get_file_path(self, node: SFATNode) -> Path:
        sb = b""
        offset = self.sfnt.string_offset + (node.file_name_offset & 0xFFFFFF) * 4

        while self.data[offset] != 0:
            sb += self.data[offset].to_bytes()
            offset += 1

        return Path(sb.decode("utf-8"))

    def get_decompressed_file_path(self, node: SFATNode) -> Path:
        if (path := self.get_file_path(node)).suffix == ".szs":
            return path.with_suffix("")
        return path

    def get_file_hash(self, node: SFATNode) -> str:
        return hashlib.sha256(self.get_file_data(node)).hexdigest()

    def get_file_data(self, node: SFATNode) -> bytes:
        return self.data[node.file_data_start + self.data_offset : node.file_data_end + self.data_offset]

    def get_decompressed_data(self, node: SFATNode) -> bytearray:
        data = self.get_file_data(node)
        return yaz0_decompress(data) if data[:4] == b"Yaz0" else data
