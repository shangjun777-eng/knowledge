"""Generate simple placeholder avatar/favicon PNGs without external dependencies."""

import os
import struct
import zlib


def make_png(path: str, size: int) -> None:
    width = height = size
    background = (15, 23, 42)
    chip = (59, 130, 246)
    pin = (148, 163, 184)

    rows = []
    for y in range(height):
        row = bytearray([0])  # filter type: none
        for x in range(width):
            r, g, b = background

            if 0.25 * width <= x < 0.75 * width and 0.25 * height <= y < 0.75 * height:
                r, g, b = chip

            horizontal_pin = 0.15 * width <= x < 0.85 * width and (
                0.18 * height <= y < 0.24 * height
                or 0.76 * height <= y < 0.82 * height
            )
            vertical_pin = 0.15 * height <= y < 0.85 * height and (
                0.18 * width <= x < 0.24 * width
                or 0.76 * width <= x < 0.82 * width
            )
            if horizontal_pin or vertical_pin:
                r, g, b = pin

            row += bytes([r, g, b, 255])
        rows.append(bytes(row))

    raw = b"".join(rows)

    def chunk(tag: bytes, data: bytes) -> bytes:
        payload = tag + data
        return (
            struct.pack(">I", len(data))
            + payload
            + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")

    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    os.makedirs("assets/img", exist_ok=True)
    make_png("assets/img/avatar.png", 256)
    make_png("assets/img/favicon.png", 64)
    print("generated assets/img/avatar.png and assets/img/favicon.png")
