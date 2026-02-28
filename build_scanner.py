#!/usr/bin/env python3
import os

BASE = r"E:\Qr_Attendence"

with open(os.path.join(BASE, "jsqr.min.js"), "r", encoding="utf-8") as f:
    jsqr_content = f.read()

template_path = os.path.join(BASE, "_scanner_template.html")
with open(template_path, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("/* JSQR_EMBED */", jsqr_content, 1)

out_path = os.path.join(BASE, "Scanner.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = os.path.getsize(out_path) / 1024
print(f"Scanner.html written: {size_kb:.1f} KB")
print("Done.")
