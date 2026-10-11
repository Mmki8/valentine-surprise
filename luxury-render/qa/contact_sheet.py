"""Tile images into one labelled contact sheet.

usage: python3 qa/contact_sheet.py out.png cols label1=path1 label2=path2 ...
"""
import sys
from PIL import Image, ImageDraw

out, cols = sys.argv[1], int(sys.argv[2])
items = [a.split("=", 1) for a in sys.argv[3:]]
TW = 800
tiles = []
for label, p in items:
    im = Image.open(p).convert("RGB")
    im = im.resize((TW, int(im.height * TW / im.width)))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 8 * len(label) + 16, 24], fill=(0, 0, 0))
    d.text((8, 6), label, fill=(255, 255, 0))
    tiles.append(im)
th = max(t.height for t in tiles)
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * TW, rows * th), (40, 40, 40))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * TW, (i // cols) * th))
sheet.save(out)
print("wrote", out, sheet.size)
