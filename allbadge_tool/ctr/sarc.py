"""
Original code by SciresM @ https://github.com/SciresM/BadgeArcadeTool/blob/master/BadgeArcadeTool/SARC.cs
"""

from enum import Enum
import struct
import hashlib
from io import BytesIO
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Iterator, Self

from allbadge_tool.ctr.yaz0 import yaz0_decompress


class ByteOrder(Enum):
    BIG = b"\xFE\xFF", ">"
    LITTLE = b"\xFF\xFE", "<"

    @classmethod
    def from_mark(cls, mark: bytes) -> Self:
        for order in cls:
            if mark == order.mark:
                return order

        raise ValueError(f"Unknown byte order mark '{mark.hex()}'")

    @property
    def mark(self) -> bytes:
        return self.value[0]

    def unpack(self, fmt: str, value: bytes) -> tuple[Any, ...]:
        return struct.unpack(f"{self.value[1]}{fmt}", value)


@dataclass(slots=True)
class SFATNode:
    file_name_hash: int
    file_name_offset: int
    file_data_start: int
    file_data_end: int

    @classmethod
    def unpack(cls, fs: BytesIO, byte_order: ByteOrder):
        return cls(*byte_order.unpack("IIII", fs.read(16)))


@dataclass(slots=True)
class SFAT:
    magic: bytes
    header_size: int
    entry_count: int
    hash_mult: int
    nodes: list[SFATNode] = field(repr=False)

    @classmethod
    def unpack(cls, fs: BytesIO, byte_order: ByteOrder):
        magic, header_size, entry_count, hash_mult = byte_order.unpack("4sHHI", fs.read(12))

        if magic != b"SFAT":
            raise AttributeError("Invalid SFAT header")

        nodes = [SFATNode.unpack(fs, byte_order) for _ in range(entry_count)]

        return cls(magic, header_size, entry_count, hash_mult, nodes)


@dataclass(slots=True)
class SFNT:
    magic: bytes
    header_size: int
    unknown: int
    string_offset: int

    @classmethod
    def unpack(cls, fs: BytesIO, byte_order: ByteOrder):
        magic, header_size, unknown = byte_order.unpack("4sHH", fs.read(8))

        if magic != b"SFNT":
            raise AttributeError("Invalid SFNT header")

        return cls(magic, header_size, unknown, fs.tell())


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
    data: bytes
    magic: bytes
    header_size: int
    byte_order: ByteOrder
    file_size: int
    data_offset: int
    unknown: int
    sfat: SFAT
    sfnt: SFNT

    @classmethod
    def unpack(cls, data: bytes):
        with BytesIO(data) as fs:
            magic, header_size, byte_order = struct.unpack("4s2s2s", fs.read(8))

            if magic != b"SARC":
                raise AttributeError("Invalid SARC header")

            byte_order = ByteOrder.from_mark(byte_order)

            (header_size,) = byte_order.unpack("H", header_size)
            file_size, data_offset, unknown = byte_order.unpack("III", fs.read(12))

            if file_size != len(data):
                raise AttributeError("Specified file is not valid (incorrect file size)")

            sfat = SFAT.unpack(fs, byte_order)
            sfnt = SFNT.unpack(fs, byte_order)

        return cls(data, magic, header_size, byte_order, file_size, data_offset, unknown, sfat, sfnt)

    @property
    def nodes(self) -> list[SFATNode]:
        return self.sfat.nodes

    @property
    def node_count(self) -> int:
        return self.sfat.entry_count

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
