#!/usr/bin/env python3
import csv, hashlib, json, os, re, sys
import qrcode
from PIL import Image, ImageDraw, ImageFont

SECRET_KEY   = "CHANGE_THIS_SECRET_KEY_2024"
INPUT_CSV    = "students.csv"
OUTPUT_DIR   = "qr_codes"
SCANNER_HTML = "Scanner.html"
IMG_W = 600; IMG_H = 700; QR_SIZE = 480; FONT_SIZE = 32; NAME_Y_GAP = 20

def make_signature(sid):
    return hashlib.sha1((sid + SECRET_KEY).encode()).hexdigest()

def sanitize_filename(name):
    name = name.strip().replace(" ", "_")
    return re.sub(r"[^\w\-]", "", name)

def load_font(size):
    for path in ["arial.ttf", "Arial.ttf",
                 "/System/Library/Fonts/Helvetica.ttc",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        try: return ImageFont.truetype(path, size)
        except (IOError, OSError): pass
    print("  [warn] No TTF font found.")
    return ImageFont.load_default()

def generate_qr_image(name, student_id):
    payload = f"{student_id}|{make_signature(student_id)}"
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
    qr.add_data(payload); qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_img = qr_img.resize((QR_SIZE, QR_SIZE), Image.LANCZOS)
    canvas = Image.new("RGB", (IMG_W, IMG_H), "white")
    qr_x = (IMG_W - QR_SIZE) // 2
    qr_y = (IMG_H - QR_SIZE) // 2 - 30
    canvas.paste(qr_img, (qr_x, qr_y))
    draw = ImageDraw.Draw(canvas)
    font = load_font(FONT_SIZE)
    try:
        bbox = draw.textbbox((0, 0), name, font=font)
        text_w = bbox[2] - bbox[0]
    except AttributeError:
        text_w, _ = draw.textsize(name, font=font)
    draw.text(((IMG_W - text_w) // 2, qr_y + QR_SIZE + NAME_Y_GAP), name, fill="black", font=font)
    return canvas

def handle_duplicate_filename(base, used):
    if base not in used: used.add(base); return base
    c = 2
    while True:
        cand = f"{base}_{c}"
        if cand not in used: used.add(cand); return cand
        c += 1

def update_scanner_html(students):
    if not os.path.isfile(SCANNER_HTML):
        print(f"  [warn] {SCANNER_HTML} not found - skipping.")
        return
    with open(SCANNER_HTML, "r", encoding="utf-8") as fh:
        html = fh.read()
    js_obj = json.dumps(students, ensure_ascii=False, indent=2)
    new_html = re.sub(
        r"const STUDENTS\s*=\s*\{[^;]*\};",
        f"const STUDENTS = {js_obj};",
        html, count=1, flags=re.DOTALL)
    if new_html == html:
        print("  [warn] Could not locate STUDENTS in Scanner.html")
        return
    with open(SCANNER_HTML, "w", encoding="utf-8") as fh:
        fh.write(new_html)
    print(f"  Scanner.html updated with {len(students)} students.")

def main():
    if not os.path.isfile(INPUT_CSV):
        print(f"ERROR: {INPUT_CSV!r} not found. Create with columns: Name,ID,Group")
        sys.exit(1)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    students_db = {}; used = set(); success = 0; errors = 0
    with open(INPUT_CSV, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        required = {"Name", "ID", "Group"}
        if not required.issubset(set(reader.fieldnames or [])):
            print(f"ERROR: CSV must have columns: {required}")
            sys.exit(1)
        rows = list(reader)
    total = len(rows)
    print(f"\nGenerating QR codes for {total} students ...\n")
    for i, row in enumerate(rows, 1):
        name = row["Name"].strip()
        sid  = row["ID"].strip()
        grp  = row["Group"].strip()
        if not name or not sid:
            print(f"  [{i}/{total}] SKIP - empty Name or ID")
            errors += 1; continue
        safe = handle_duplicate_filename(sanitize_filename(name), used)
        out_path = os.path.join(OUTPUT_DIR, f"{safe}.png")
        try:
            img = generate_qr_image(name, sid)
            img.save(out_path, "PNG")
            print(f"  [{i}/{total}] OK   {out_path:<40}  ({sid}, {grp})")
            students_db[sid] = {"name": name, "group": grp}
            success += 1
        except Exception as exc:
            print(f"  [{i}/{total}] ERR  {name}: {exc}"); errors += 1
    print(f"\n  {success} QR images saved to: {os.path.abspath(OUTPUT_DIR)}/")
    print("\nUpdating Scanner.html ...")
    update_scanner_html(students_db)
    print(f"\nDone. {success} generated, {errors} errors.")
    if success:
        print("\nNext steps:")
        print("  1. Share QR PNGs from qr_codes/ with students")
        print("  2. Open Scanner.html on iPhone")
        print("  3. Tap New Session and start scanning")

if __name__ == "__main__":
    main()
