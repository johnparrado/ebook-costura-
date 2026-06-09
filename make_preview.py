#!/usr/bin/env python3
"""Genera preview.png (1200x630) sin dependencias externas (solo stdlib)."""
import struct, zlib, math

W, H = 1200, 630
buf = bytearray([0]) * (W * H * 3)

def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i+1], buf[i+2] = c

def lerp(a, b, t):
    return tuple(int(a[k] + (b[k]-a[k]) * t) for k in range(3))

# --- gradient background (plum dark -> plum -> wine) ---
top = (0x4a, 0x10, 0x28)
mid = (0x7a, 0x1f, 0x3d)
bot = (0x90, 0x2c, 0x4c)
for y in range(H):
    t = y / (H-1)
    c = lerp(top, mid, t*1.4) if t < 0.6 else lerp(mid, bot, (t-0.6)/0.4)
    for x in range(W):
        i = (y*W+x)*3
        buf[i], buf[i+1], buf[i+2] = c

# --- subtle dot pattern ---
dot = (0xff, 0xff, 0xff)
for y in range(0, H, 46):
    for x in range(0, W, 46):
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                xi, yi = x+dx, y+dy
                if 0 <= xi < W and 0 <= yi < H:
                    i = (yi*W+xi)*3
                    for k in range(3):
                        buf[i+k] = min(255, buf[i+k] + 10)

GOLD = (0xe7, 0xcf, 0x94)
GOLD2 = (0xc9, 0xa2, 0x4b)
CREAM = (0xfd, 0xf3, 0xe9)
ROSE = (0xc9, 0x8a, 0x9b)

def fill_rect(x0, y0, x1, y1, c):
    for y in range(max(0,y0), min(H,y1)):
        for x in range(max(0,x0), min(W,x1)):
            px(x, y, c)

def disc(cx, cy, r, c):
    for y in range(cy-r, cy+r+1):
        for x in range(cx-r, cx+r+1):
            if (x-cx)**2 + (y-cy)**2 <= r*r:
                px(x, y, c)

def ring(cx, cy, r, w, c):
    for y in range(cy-r-w, cy+r+w+1):
        for x in range(cx-r-w, cx+r+w+1):
            d = math.hypot(x-cx, y-cy)
            if r-w <= d <= r+w:
                px(x, y, c)

# --- decorative dashed stitch frame ---
def dashed_h(y, c, dash=18, gap=14):
    x = 30
    while x < W-30:
        fill_rect(x, y, x+dash, y+5, c)
        x += dash+gap
def dashed_v(x, c, dash=18, gap=14):
    y = 30
    while y < H-30:
        fill_rect(x, y, x+5, y+dash, c)
        y += dash+gap
dashed_h(34, GOLD); dashed_h(H-40, GOLD)
dashed_v(34, GOLD); dashed_v(W-40, GOLD)

# --- right-side motif: dress form / maniqui silhouette ---
cx = 980
# stand
fill_rect(cx-6, 250, cx+6, 470, GOLD2)
fill_rect(cx-70, 470, cx+70, 484, GOLD2)
# bust (two overlapping discs + body)
disc(cx, 150, 70, CREAM)
for y in range(150, 360):
    half = int(95 - 60*((y-150)/210) + 28*math.sin((y-150)/210*math.pi))
    fill_rect(cx-half, y, cx+half, y+1, CREAM)
# neck top
disc(cx, 95, 26, GOLD)
# seam lines on form
for yy in range(150, 350, 4):
    px(cx, yy, ROSE); px(cx+1, yy, ROSE)
# thread spool bottom-left of motif
sx, sy = 1075, 470
fill_rect(sx, sy, sx+58, sy+96, GOLD)
fill_rect(sx-10, sy, sx+68, sy+12, GOLD2)
fill_rect(sx-10, sy+84, sx+68, sy+96, GOLD2)

# ---------- 5x7 bitmap font ----------
FONT = {
 'A':["01110","10001","10001","11111","10001","10001","10001"],
 'C':["01110","10001","10000","10000","10000","10001","01110"],
 'D':["11110","10001","10001","10001","10001","10001","11110"],
 'E':["11111","10000","10000","11110","10000","10000","11111"],
 'I':["11111","00100","00100","00100","00100","00100","11111"],
 'L':["10000","10000","10000","10000","10000","10000","11111"],
 'N':["10001","11001","10101","10101","10011","10001","10001"],
 'O':["01110","10001","10001","10001","10001","10001","01110"],
 'P':["11110","10001","10001","11110","10000","10000","10000"],
 'R':["11110","10001","10001","11110","10100","10010","10001"],
 'S':["01111","10000","10000","01110","00001","00001","11110"],
 'T':["11111","00100","00100","00100","00100","00100","00100"],
 'U':["10001","10001","10001","10001","10001","10001","01110"],
 'G':["01110","10001","10000","10111","10001","10001","01111"],
 'M':["10001","11011","10101","10101","10001","10001","10001"],
 '0':["01110","10001","10011","10101","11001","10001","01110"],
 '1':["00100","01100","00100","00100","00100","00100","01110"],
 '2':["01110","10001","00001","00010","00100","01000","11111"],
 '7':["11111","00001","00010","00100","01000","01000","01000"],
 '+':["00000","00100","00100","11111","00100","00100","00000"],
 '.':["00000","00000","00000","00000","00000","00110","00110"],
 '-':["00000","00000","00000","11111","00000","00000","00000"],
 '$':["00100","01111","10100","01110","00101","11110","00100"],
 ' ':["00000","00000","00000","00000","00000","00000","00000"],
}

def text_width(s, scale, gap):
    return len(s) * (5*scale + gap) - gap

def draw_text(s, x, y, scale, c, gap=None):
    if gap is None: gap = scale
    cur = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for ry, row in enumerate(g):
            for rx, bit in enumerate(row):
                if bit == '1':
                    fill_rect(cur+rx*scale, y+ry*scale, cur+rx*scale+scale, y+ry*scale+scale, c)
        cur += 5*scale + gap

# --- texts (left aligned within left zone) ---
LX = 70
# eyebrow
draw_text("GUIA PROFESIONAL", LX, 120, 4, GOLD, gap=4)
# title two lines
draw_text("EL ARTE DE", LX, 185, 11, CREAM, gap=8)
draw_text("LA COSTURA", LX, 290, 11, GOLD, gap=8)
# highlight
draw_text("+7000 PATRONES Y MOLDES", LX, 410, 5, CREAM, gap=4)
# price pill
fill_rect(LX-6, 470, LX+330, 545, GOLD)
draw_text("SOLO $12 USD", LX+18, 487, 7, (0x5c,0x15,0x30), gap=6)

# ---------- encode PNG ----------
def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y*W*3:(y+1)*W*3]
    comp = zlib.compress(bytes(raw), 9)
    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)
        return c
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", comp))
        f.write(chunk(b"IEND", b""))

write_png("preview.png")
print("preview.png generado")
