import pytesseract
from PIL import Image
import numpy as np
import json

# If needed (Linux containers)
# pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def extract_tables_from_image(image_path, row_threshold=15):
    """
    Extract tables from an image using Tesseract OCR
    and reconstruct rows/columns using bounding boxes.
    """

    img = Image.open(image_path).convert("RGB")
    img_np = np.array(img)

    data = pytesseract.image_to_data(
        img_np,
        output_type=pytesseract.Output.DICT,
        config="--psm 6"
    )

    words = []
    n = len(data["text"])

    for i in range(n):
        text = data["text"][i].strip()
        if text == "":
            continue

        words.append({
            "text": text,
            "x": data["left"][i],
            "y": data["top"][i],
            "w": data["width"][i],
            "h": data["height"][i]
        })

    # ---------- GROUP WORDS BY ROW (Y-AXIS CLUSTERING) ----------
    rows = []
    for word in sorted(words, key=lambda x: x["y"]):
        placed = False
        for row in rows:
            if abs(row[0]["y"] - word["y"]) < row_threshold:
                row.append(word)
                placed = True
                break
        if not placed:
            rows.append([word])

    # ---------- SORT EACH ROW LEFT → RIGHT ----------
    for row in rows:
        row.sort(key=lambda x: x["x"])

    # ---------- BUILD TABLE ----------
    table = []
    for row in rows:
        table.append([cell["text"] for cell in row])

    if len(table) < 2:
        raise ValueError("No table detected")

    headers = table[0]
    data_rows = table[1:]

    # ---------- NORMALIZE COLUMN COUNT ----------
    col_count = len(headers)
    clean_rows = []

    for row in data_rows:
        if len(row) < col_count:
            row += [""] * (col_count - len(row))
        elif len(row) > col_count:
            row = row[:col_count]
        clean_rows.append(row)

    # ---------- CREATE JSON ----------
    output = []
    for idx, row in enumerate(clean_rows):
        record = {
            "row_id": idx
        }
        for h, v in zip(headers, row):
            record[h] = v
        output.append(record)

    return output


# ---------- OPTIONAL CLI TEST ----------
if __name__ == "__main__":
    image_path = "sample.png"
    result = extract_tables_from_image(image_path)
    print(json.dumps(result, indent=2))
