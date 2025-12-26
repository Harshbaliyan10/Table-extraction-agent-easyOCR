import pytesseract
import cv2
import numpy as np
from PIL import Image

# -------- IMAGE PREPROCESSING --------
def preprocess_image(image: Image.Image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
    return thresh


# -------- CORE EXTRACTION --------
def extract_tables(image: Image.Image):
    processed = preprocess_image(image)

    data = pytesseract.image_to_data(
        processed,
        output_type=pytesseract.Output.DICT,
        config="--psm 6"
    )

    rows = {}
    for i in range(len(data["text"])):
        text = data["text"][i].strip()
        if not text:
            continue

        y = data["top"][i]
        row_key = y // 15  # group by Y proximity

        rows.setdefault(row_key, []).append(
            (data["left"][i], text)
        )

    # Sort rows by Y and words by X
    table = []
    for _, words in sorted(rows.items()):
        row = [w[1] for w in sorted(words)]
        table.append(row)

    return table


# -------- FLATTEN TO JSON --------
def flatten_tables(table, image_name):
    headers = table[0]
    results = []

    for row_id, row in enumerate(table[1:]):
        item = {
            "image": image_name,
            "table_id": 0,
            "row_id": row_id
        }

        for i, header in enumerate(headers):
            item[header] = row[i] if i < len(row) else ""

        results.append(item)

    return results
