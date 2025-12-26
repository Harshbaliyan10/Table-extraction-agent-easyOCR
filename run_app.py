import streamlit as st
from PIL import Image
from extract_text import extract_tables, flatten_tables

st.set_page_config(
    page_title="Table Extraction Agent",
    layout="wide"
)

st.title("📊 Table Extraction Agent (Tesseract)")

uploaded_file = st.file_uploader(
    "Upload table image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    try:
        # ✅ Convert uploaded file to PIL Image
        image = Image.open(uploaded_file)

        st.image(image, caption="Uploaded Image", use_column_width=True)

        # ✅ PASS PIL IMAGE — NOT file, NOT bytes
        table = extract_tables(image)

        if not table or len(table) < 2:
            st.error("No table detected")
        else:
            json_rows = flatten_tables(
                table,
                image_name=uploaded_file.name
            )

            st.success("Extraction successful")

            st.json(json_rows)

    except Exception as e:
        st.error(f"Error during extraction: {e}")
