from dataclasses import dataclass
from Crypto.Cipher import AES
from Crypto.Util import Counter


@dataclass(slots=True)
class BOSS:
    counter: bytes
    encrypted_data: bytes

    @classmethod
    def unpack(cls, data: bytes):
        if data[:0x4] != b"boss":
            raise ValueError("Invalid BOSS data")

        return cls(
            int.from_bytes(data[0x1C:0x28] + 0x1.to_bytes(4)),
            data[0x28:],
        )

    def decrypt(self, key: bytes) -> bytes:
        cipher = AES.new(key, AES.MODE_CTR, counter=Counter.new(128, initial_value=self.counter))

        return cipher.decrypt(self.encrypted_data)[0x26E:]
