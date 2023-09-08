"""
Original code by SciresM @ https://github.com/SciresM/BadgeArcadeTool/blob/master/BadgeArcadeTool/SARC.cs
Yaz0 decompression by Wiimm @ https://wiki.tockdom.com/wiki/YAZ0_(File_Format)
Sources converted to Python by AntiMach with ChatGPT
"""

import struct
import hashlib
from io import BytesIO
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class SFATNode:
    _sarc: "SARC" = field(repr=False)
    file_name_hash: int = 0
    file_name_offset: int = 0
    file_data_start: int = 0
    file_data_end: int = 0

    @classmethod
    def unpack(cls, fs: BytesIO, sarc: "SARC"):
        return cls(sarc, *struct.unpack("<IIII", fs.read(16)))

    def get_file_path(self):
        return self._sarc.get_decompressed_file_path(self)

    def get_file_hash(self):
        return self._sarc.get_file_hash(self)

    def get_data(self):
        return self._sarc.get_decompressed_data(self)


@dataclass
class SFAT:
    header_size: int = 0
    entry_count: int = 0
    hash_mult: int = 0
    nodes: list[SFATNode] = field(default_factory=list, repr=False)

    @classmethod
    def unpack(cls, fs: BytesIO, sarc: "SARC"):
        if fs.read(4) != b"SFAT":
            raise AttributeError("Invalid SFAT header")

        self = cls(*struct.unpack("<HHI", fs.read(8)))

        self.nodes.extend(SFATNode.unpack(fs, sarc) for _ in range(self.entry_count))

        return self


@dataclass
class SFNT:
    header_size: int = 0
    unknown: int = 0
    string_offset: int = 0

    @classmethod
    def unpack(cls, fs: BytesIO):
        if fs.read(4) != b"SFNT":
            raise AttributeError("Invalid SFNT header")

        return cls(*struct.unpack("<HH", fs.read(4)), fs.tell())


@dataclass
class SARC:
    data: bytes = field(repr=False)
    header_size: int = 0x14
    endianness: int = 0
    file_size: int = 0
    data_offset: int = 0
    unknown: int = 0
    sfat: SFAT = field(default_factory=SFAT)
    sfnt: SFNT = field(default_factory=SFNT)

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

            self.sfat = SFAT.unpack(fs, self)
            self.sfnt = SFNT.unpack(fs)

        if self.file_size != len(self.data):
            raise AttributeError("Specified file is not valid (incorrect file size)")

        return self

    @property
    def nodes(self) -> list[SFATNode]:
        return self.sfat.nodes

    def get_file_path(self, entry: SFATNode) -> Path:
        sb = b""
        offset = self.sfnt.string_offset + (entry.file_name_offset & 0xFFFFFF) * 4

        while self.data[offset] != 0:
            sb += self.data[offset].to_bytes()
            offset += 1

        return Path(sb.decode("utf-8"))

    def get_decompressed_file_path(self, entry: SFATNode) -> Path:
        if (path := self.get_file_path(entry)).suffix == ".szs":
            return path.with_suffix("")
        return path

    def get_file_hash(self, entry: SFATNode) -> str:
        return hashlib.sha256(self.get_file_data(entry)).hexdigest()

    def get_file_data(self, entry: SFATNode) -> bytes:
        return self.data[entry.file_data_start + self.data_offset : entry.file_data_end + self.data_offset]

    def get_decompressed_data(self, entry: SFATNode) -> bytearray:
        data = self.get_file_data(entry)
        return self.yaz0_decompress(data) if data[:4] == b"Yaz0" else data

    @staticmethod
    def yaz0_decompress(src: bytes) -> bytearray:
        src_pos = 16
        dest_pos = 0
        src_end = len(src)
        dest_end = struct.unpack(">I", src[4:8])[0]

        dest = bytearray(dest_end)

        group_head = 0
        group_head_len = 0

        while src_pos < src_end and dest_pos < dest_end:
            if not group_head_len:
                group_head = src[src_pos]
                src_pos += 1
                group_head_len = 8

            group_head_len -= 1

            if group_head & 0x80:
                dest[dest_pos] = src[src_pos]
                src_pos += 1
                dest_pos += 1
                group_head <<= 1
                continue

            b1, b2 = src[src_pos : src_pos + 2]
            src_pos += 2

            copy_src = dest_pos - ((b1 & 0x0F) << 8 | b2) - 1

            n = b1 >> 4

            if not n:
                n = src[src_pos] + 0x12
                src_pos += 1
            else:
                n += 2

            assert n >= 3 and n <= 0x111

            if copy_src < 0 or dest_pos + n > len(dest):
                raise ValueError("Corrupted data!")

            for _ in range(n):
                dest[dest_pos] = dest[copy_src]
                dest_pos += 1
                copy_src += 1

            group_head <<= 1

        assert src_pos <= len(src)
        assert dest_pos <= len(dest)

        return dest
