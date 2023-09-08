from Crypto.Cipher import AES
from Crypto.Util import Counter


BOOT9_PROT_OFFSET = 0x8000
KEYAREA_OFFSETS = 0x5860, 0x5C60
AESIV_OFFSET = 0x170
KEY_SIZE = 0x10


def get_boss_key(boot9: bytes, dev_unit: bool = False) -> bytes:
    keyarea_offset = BOOT9_PROT_OFFSET + KEYAREA_OFFSETS[dev_unit] + AESIV_OFFSET

    boss_key_offset = keyarea_offset + 32 * KEY_SIZE

    return boot9[boss_key_offset : boss_key_offset + KEY_SIZE]


def decrypt_boss(data: bytes, key: bytes) -> bytes:
    if data[:0x4] != b"boss":
        raise ValueError("Invalid file type")

    counter = int.from_bytes(data[0x1C:0x28] + 0x1.to_bytes(4))
    cipher = AES.new(key, AES.MODE_CTR, counter=Counter.new(128, initial_value=counter))

    return cipher.decrypt(data[0x28:])[0x26E:]


def decrypt_boss_with_boot9(data: bytes, boot9: bytes, dev_unit: bool = False) -> bytes:
    return decrypt_boss(data, get_boss_key(boot9, dev_unit))
