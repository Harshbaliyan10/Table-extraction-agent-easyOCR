import pytesseract
import numpy as np
from PIL import Image
import re


def extract_tables(image: Image.Image):
    """
    Extract raw table text using Tesseract
    Input: PIL Image
    Output: List of rows (list of strings)
    """

    # ✅ Convert PIL Image → NumPy array
    img_np = np.array(image)

    # OCR config tuned for tables
    custom_config = r'--oem 3 --psm 6'

    text = pytesseract.image_to_string(
        img_np,
        config=custom_config
    )

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    table = []
    for line in lines:
        # split on multiple spaces
        row = re.split(r"\s{2,}", line)
        table.append(row)

    return table


def flatten_tables(table, image_name="image.png"):
    """
    Convert table rows → row-wise JSON
    """

    headers = table[0]
    rows = table[1:]

    output = []

    for row_id, row in enumerate(rows):
        row_dict = {
            "image": image_name,
            "table_id": 0,
            "row_id": row_id
        }

        for i, header in enumerate(headers):
            row_dict[header] = row[i] if i < len(row) else ""

        output.append(row_dict)

    return output
