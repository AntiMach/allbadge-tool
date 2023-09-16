import hashlib
from typing import Self
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Keys:
    key_x: str | None = None
    key_y: str | None = None
    normal_key: str | None = None


@dataclass
class Boot9:
    SHA512 = bytes.fromhex(
        "5addf30ecb46c624fa97bf1e83303ce5"
        "d36fabb4525c08c966cbaf0a397fe4c3"
        "3d8a4ad17fd0f4f509f547947779e1b2"
        "db32abc0471e785cacb3e2dde9b8c492"
    )
    PROT_SHA512 = bytes.fromhex(
        "d1f10601193b4154d8c7667102f7c5e2"
        "70fea49d50b04c6f7e374dbf15937c1a"
        "5568236bb551a5cb73bf789c9454c272"
        "7118c5eb849f0728561273b684ca1ae7"
    )

    KEYAREA_OFFSETS = 0x5860, 0x5C60
    PROT_OFFSETS = 0x8000, 0x0000
    AESIV_OFFSET = 0x170
    KEY_SIZE = 0x10

    OFFSETS = {
        0x04: [("key_y", 8)],
        0x05: [("key_y", 9)],
        0x06: [("key_y", 10)],
        0x07: [("key_y", 11)],
        0x08: [("key_y", 12)],
        0x09: [("key_y", 13)],
        0x0A: [("key_y", 14)],
        0x0B: [("key_y", 15)],
        0x0C: [("normal_key", 16)],
        0x0D: [("normal_key", 16)],
        0x0E: [("normal_key", 16)],
        0x0F: [("normal_key", 16)],
        0x10: [("normal_key", 17)],
        0x11: [("normal_key", 17)],
        0x12: [("normal_key", 17)],
        0x13: [("normal_key", 17)],
        0x14: [("normal_key", 18)],
        0x15: [("normal_key", 19)],
        0x16: [("normal_key", 20)],
        0x17: [("normal_key", 21)],
        0x18: [("normal_key", 22)],
        0x19: [("normal_key", 22)],
        0x1A: [("normal_key", 22)],
        0x1B: [("normal_key", 22)],
        0x1C: [("normal_key", 23)],
        0x1D: [("normal_key", 23)],
        0x1E: [("normal_key", 23)],
        0x1F: [("normal_key", 23)],
        0x20: [("normal_key", 24)],
        0x21: [("normal_key", 24)],
        0x22: [("normal_key", 24)],
        0x23: [("normal_key", 24)],
        0x24: [("normal_key", 25)],
        0x25: [("normal_key", 25)],
        0x26: [("normal_key", 25)],
        0x27: [("normal_key", 25)],
        0x28: [("normal_key", 25)],
        0x29: [("normal_key", 26)],
        0x2A: [("normal_key", 27)],
        0x2B: [("normal_key", 28)],
        0x2C: [("key_x", 0), ("normal_key", 29)],
        0x2D: [("key_x", 0), ("normal_key", 29)],
        0x2E: [("key_x", 0), ("normal_key", 29)],
        0x2F: [("key_x", 0), ("normal_key", 29)],
        0x30: [("key_x", 1), ("normal_key", 30)],
        0x31: [("key_x", 1), ("normal_key", 30)],
        0x32: [("key_x", 1), ("normal_key", 30)],
        0x33: [("key_x", 1), ("normal_key", 30)],
        0x34: [("key_x", 2), ("normal_key", 31)],
        0x35: [("key_x", 2), ("normal_key", 31)],
        0x36: [("key_x", 2), ("normal_key", 31)],
        0x37: [("key_x", 2), ("normal_key", 31)],
        0x38: [("key_x", 3), ("normal_key", 32)],
        0x39: [("key_x", 3), ("normal_key", 32)],
        0x3A: [("key_x", 3), ("normal_key", 32)],
        0x3B: [("key_x", 3), ("normal_key", 32)],
        0x3C: [("key_x", 4), ("normal_key", 32)],
        0x3D: [("key_x", 5), ("normal_key", 33)],
        0x3E: [("key_x", 6), ("normal_key", 34)],
        0x3F: [("key_x", 7), ("normal_key", 35)],
    }

    data: bytes
    is_dev_unit: bool
    is_prot: bool

    @classmethod
    def unpack(cls, data: bytes, is_dev_unit: bool = False) -> Self:
        _hash = hashlib.sha512(data).digest()

        if _hash not in (cls.SHA512, cls.PROT_SHA512):
            raise ValueError("Invalid boot9 data")

        return cls(data, is_dev_unit, _hash == cls.PROT_SHA512)

    def get_keyarea_offset(self) -> int:
        return self.PROT_OFFSETS[self.is_prot] + self.KEYAREA_OFFSETS[self.is_dev_unit] + self.AESIV_OFFSET

    def get_keys(self, slot: int) -> Keys:
        if not (offsets := self.OFFSETS.get(slot)):
            return Keys()

        keyarea_offset = self.get_keyarea_offset()

        keys = {}

        for key_type, position in offsets:
            offset = keyarea_offset + self.KEY_SIZE * position
            keys[key_type] = self.data[offset : offset + self.KEY_SIZE]

        return Keys(**keys)
