import easyocr
import cv2
import numpy as np
from collections import defaultdict

def extract_tables_from_image(
    image_path,
    image_name="image.png",
    table_id=0,
    y_threshold=15
):
    """
    Extract table rows from image using EasyOCR and return row-wise JSON
    """

    reader = easyocr.Reader(['en'], gpu=False)

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not read image")

    results = reader.readtext(img)

    # Each item: (bbox, text, confidence)
    rows = defaultdict(list)

    for bbox, text, conf in results:
        # bbox = [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        y_center = int(sum(point[1] for point in bbox) / 4)
        x_center = int(sum(point[0] for point in bbox) / 4)

        rows[y_center].append((x_center, text))

    # Sort rows top-to-bottom
    sorted_rows = sorted(rows.items(), key=lambda x: x[0])

    # Merge nearby rows
    merged_rows = []
    for y, cells in sorted_rows:
        if not merged_rows:
            merged_rows.append((y, cells))
        else:
            prev_y, prev_cells = merged_rows[-1]
            if abs(prev_y - y) <= y_threshold:
                prev_cells.extend(cells)
            else:
                merged_rows.append((y, cells))

    # Sort cells left-to-right
    table_rows = []
    for _, cells in merged_rows:
        cells_sorted = sorted(cells, key=lambda x: x[0])
        row_text = [cell[1] for cell in cells_sorted]
        table_rows.append(row_text)

    # First row assumed header
    headers = table_rows[0]
    data_rows = table_rows[1:]

    output = []

    for idx, row in enumerate(data_rows):
        row_dict = {
            "image": image_name,
            "table_id": table_id,
            "row_id": idx
        }

        for col_idx, header in enumerate(headers):
            value = row[col_idx] if col_idx < len(row) else ""
            row_dict[header.strip()] = value.strip()

        output.append(row_dict)

    return output


# -------- TEST LOCALLY --------
if __name__ == "__main__":
    import json

    image_path = "sample.png"  # change this
    result = extract_tables_from_image(
        image_path=image_path,
        image_name="sample.png"
    )

    print(json.dumps(result, indent=2))

