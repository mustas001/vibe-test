#!/usr/bin/env python3
"""Render the arcade app icons (pure standard library, no Pillow needed).

Usage: python3 tools/make_icons.py   ->  writes icons/*.png
"""
import math, struct, zlib, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "icons"


def smooth(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def sd_round_rect(px, py, cx, cy, hw, hh, r):
    dx, dy = abs(px - cx) - (hw - r), abs(py - cy) - (hh - r)
    return math.hypot(max(dx, 0), max(dy, 0)) + min(max(dx, dy), 0) - r


def render(n):
    px = bytearray()
    aa = 1.5 / n
    for y in range(n):
        row = bytearray([0])  # PNG filter byte
        v = y / n
        for x in range(n):
            u = x / n
            # background: deep violet -> near black, with soft corner glows
            t = (u + v) / 2
            r, g, b = 27 * (1 - t) + 5 * t, 15 * (1 - t) + 4 * t, 69 * (1 - t) + 26 * t
            gl = math.exp(-((u - 0.18) ** 2 + (v - 0.9) ** 2) / 0.05)
            gr = math.exp(-((u - 0.82) ** 2 + (v - 0.1) ** 2) / 0.05)
            r, g, b = r + 255 * 0.22 * gr, g + 46 * 0.22 * gr, b + 147 * 0.22 * gr
            r, g, b = r + 0 * gl, g + 240 * 0.16 * gl, b + 255 * 0.16 * gl

            # dashed centre line
            if abs(u - 0.5) < 0.006 and int(v * 14) % 2 == 0:
                r, g, b = r + 40, g + 42, b + 70

            # paddles with glow
            for cx, col in ((0.26, (0, 240, 255)), (0.74, (255, 46, 147))):
                d = sd_round_rect(u, v, cx, 0.5 + (0.06 if cx < .5 else -0.06), 0.032, 0.17, 0.032)
                glow = math.exp(-max(d, 0) / 0.035) * 0.55
                cov = 1 - smooth(-aa, aa, d)
                r, g, b = r + col[0] * glow, g + col[1] * glow, b + col[2] * glow
                r, g, b = r * (1 - cov) + col[0] * cov, g * (1 - cov) + col[1] * cov, b * (1 - cov) + col[2] * cov

            # ball
            d = math.hypot(u - 0.5, v - 0.5) - 0.06
            glow = math.exp(-max(d, 0) / 0.05) * 0.8
            cov = 1 - smooth(-aa, aa, d)
            r, g, b = r + 200 * glow, g + 200 * glow, b + 255 * glow
            r, g, b = r * (1 - cov) + 255 * cov, g * (1 - cov) + 255 * cov, b * (1 - cov) + 255 * cov

            row += bytes((min(255, int(r)), min(255, int(g)), min(255, int(b))))
        px += row
    return px


def write_png(path, n):
    raw = render(n)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)
    print("wrote", path, f"{n}x{n}")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    write_png(OUT / "icon-192.png", 192)
    write_png(OUT / "icon-512.png", 512)
    write_png(OUT / "icon-maskable-512.png", 512)   # artwork already sits inside the maskable safe zone
    write_png(OUT / "apple-touch-icon.png", 180)
