import hashlib
from Crypto.Cipher import AES
from Crypto.Util import Counter
from dataclasses import dataclass


@dataclass(slots=True)
class Keys:
    key_x: str | None = None
    key_y: str | None = None
    normal_key: str | None = None

    def set(self, key: str, value: str):
        setattr(self, key, value)


class BootromeKeyStore:
    BOOT9_SHA512 = bytes.fromhex(
        "5addf30ecb46c624fa97bf1e83303ce5"
        "d36fabb4525c08c966cbaf0a397fe4c3"
        "3d8a4ad17fd0f4f509f547947779e1b2"
        "db32abc0471e785cacb3e2dde9b8c492"
    )
    BOOT9_PROT_SHA512 = bytes.fromhex(
        "d1f10601193b4154d8c7667102f7c5e2"
        "70fea49d50b04c6f7e374dbf15937c1a"
        "5568236bb551a5cb73bf789c9454c272"
        "7118c5eb849f0728561273b684ca1ae7"
    )

    KEYAREA_OFFSETS = 0x5860, 0x5C60
    BOOT9_PROT_OFFSETS = 0x8000, 0x0000
    AESIV_OFFSET = 0x170
    KEY_SIZE = 0x10

    OFFSETS: list[tuple[str, int, int]] = [
        ("key_x", 0x2C, 0),
        ("key_x", 0x2D, 0),
        ("key_x", 0x2E, 0),
        ("key_x", 0x2F, 0),
        ("key_x", 0x30, 1),
        ("key_x", 0x31, 1),
        ("key_x", 0x32, 1),
        ("key_x", 0x33, 1),
        ("key_x", 0x34, 2),
        ("key_x", 0x35, 2),
        ("key_x", 0x36, 2),
        ("key_x", 0x37, 2),
        ("key_x", 0x38, 3),
        ("key_x", 0x39, 3),
        ("key_x", 0x3A, 3),
        ("key_x", 0x3B, 3),
        ("key_x", 0x3C, 4),
        ("key_x", 0x3D, 5),
        ("key_x", 0x3E, 6),
        ("key_x", 0x3F, 7),
        ("key_y", 0x04, 8),
        ("key_y", 0x05, 9),
        ("key_y", 0x06, 10),
        ("key_y", 0x07, 11),
        ("key_y", 0x08, 12),
        ("key_y", 0x09, 13),
        ("key_y", 0x0A, 14),
        ("key_y", 0x0B, 15),
        ("normal_key", 0x0C, 16),
        ("normal_key", 0x0D, 16),
        ("normal_key", 0x0E, 16),
        ("normal_key", 0x0F, 16),
        ("normal_key", 0x10, 17),
        ("normal_key", 0x11, 17),
        ("normal_key", 0x12, 17),
        ("normal_key", 0x13, 17),
        ("normal_key", 0x14, 18),
        ("normal_key", 0x15, 19),
        ("normal_key", 0x16, 20),
        ("normal_key", 0x17, 21),
        ("normal_key", 0x18, 22),
        ("normal_key", 0x19, 22),
        ("normal_key", 0x1A, 22),
        ("normal_key", 0x1B, 22),
        ("normal_key", 0x1C, 23),
        ("normal_key", 0x1D, 23),
        ("normal_key", 0x1E, 23),
        ("normal_key", 0x1F, 23),
        ("normal_key", 0x20, 24),
        ("normal_key", 0x21, 24),
        ("normal_key", 0x22, 24),
        ("normal_key", 0x23, 24),
        ("normal_key", 0x24, 25),
        ("normal_key", 0x25, 25),
        ("normal_key", 0x26, 25),
        ("normal_key", 0x27, 25),
        ("normal_key", 0x28, 25),
        ("normal_key", 0x29, 26),
        ("normal_key", 0x2A, 27),
        ("normal_key", 0x2B, 28),
        ("normal_key", 0x2C, 29),
        ("normal_key", 0x2D, 29),
        ("normal_key", 0x2E, 29),
        ("normal_key", 0x2F, 29),
        ("normal_key", 0x30, 30),
        ("normal_key", 0x31, 30),
        ("normal_key", 0x32, 30),
        ("normal_key", 0x33, 30),
        ("normal_key", 0x34, 31),
        ("normal_key", 0x35, 31),
        ("normal_key", 0x36, 31),
        ("normal_key", 0x37, 31),
        ("normal_key", 0x38, 32),
        ("normal_key", 0x39, 32),
        ("normal_key", 0x3A, 32),
        ("normal_key", 0x3B, 32),
        ("normal_key", 0x3C, 32),
        ("normal_key", 0x3D, 33),
        ("normal_key", 0x3E, 34),
        ("normal_key", 0x3F, 35),
    ]

    boot9_data: bytes
    is_dev_unit: bool
    is_boot9_prot: bool
    store: dict[int, Keys]

    def __init__(self, boot9_data: bytes, is_dev_unit: bool = False) -> None:
        self.boot9_data = boot9_data

        self.is_dev_unit = is_dev_unit
        self.is_boot9_prot = hashlib.sha512(self.boot9_data).digest() == self.BOOT9_PROT_SHA512

        keyarea_offset = self.get_keyarea_offset()

        self.store = {}

        for key, slot, key_pos in self.OFFSETS:
            self.store.setdefault(slot, Keys())
            key_start = keyarea_offset + key_pos * self.KEY_SIZE
            key_end = key_start + self.KEY_SIZE
            self.store[slot].set(key, self.boot9_data[key_start:key_end])

    def get_keyarea_offset(self) -> int:
        return self.BOOT9_PROT_OFFSETS[self.is_boot9_prot] + self.KEYAREA_OFFSETS[self.is_dev_unit] + self.AESIV_OFFSET

    def decrypt_boss(self, boss_data: bytes) -> bytes:
        key = self.store[0x38].normal_key
        ctr = boss_data[0x1C:0x28] + 0x1.to_bytes(4, "big")

        cipher = AES.new(key, AES.MODE_CTR, counter=Counter.new(128, initial_value=int.from_bytes(ctr)))

        return cipher.decrypt(boss_data[0x28:])[0x26E:]
