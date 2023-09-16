"""
Original code by Wiimm @ https://wiki.tockdom.com/wiki/YAZ0_(File_Format)
"""


def yaz0_decompress(src: bytes) -> bytearray:
    if src[:4] != b"Yaz0":
        raise ValueError("Invalid Yaz0 data")

    src_pos = 16
    dest_pos = 0
    src_end = len(src)
    dest_end = int.from_bytes(src[4:8], "big")

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
