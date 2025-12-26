import pytesseract
from PIL import Image
import numpy as np


def extract_tables(image_path):
    """
    Extract a table from image and return structured rows
    """
    img = Image.open(image_path).convert("RGB")
    img_np = np.array(img)

    data = pytesseract.image_to_data(
        img_np,
        output_type=pytesseract.Output.DICT,
        config="--psm 6"
    )

    words = []
    for i in range(len(data["text"])):
        txt = data["text"][i].strip()
        if txt:
            words.append({
                "text": txt,
                "x": data["left"][i],
                "y": data["top"][i]
            })

    # ---------- GROUP WORDS INTO ROWS ----------
    rows = []
    row_threshold = 15

    for w in sorted(words, key=lambda x: x["y"]):
        placed = False
        for row in rows:
            if abs(row[0]["y"] - w["y"]) < row_threshold:
                row.append(w)
                placed = True
                break
        if not placed:
            rows.append([w])

    # ---------- SORT ROWS LEFT → RIGHT ----------
    table = []
    for row in rows:
        row_sorted = sorted(row, key=lambda x: x["x"])
        table.append([cell["text"] for cell in row_sorted])

    return table


def flatten_tables(table, image_name="image.png"):
    """
    Convert table rows into row-wise JSON
    """
    headers = table[0]
    rows = table[1:]

    flattened = []

    for idx, row in enumerate(rows):
        record = {
            "image": image_name,
            "table_id": 0,
            "row_id": idx
        }

        for h, v in zip(headers, row):
            record[h] = v

        flattened.append(record)

    return flattened
