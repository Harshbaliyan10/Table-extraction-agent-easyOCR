import streamlit as st
from PIL import Image
from extract_text import extract_tables, flatten_tables
import json

st.set_page_config(page_title="Table Extraction Agent", layout="wide")

st.title("📊 Table Extraction Agent (Tesseract OCR)")

uploaded_file = st.file_uploader(
    "Upload table image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")

    st.image(image, caption="Uploaded Image", use_column_width=True)

    try:
        table = extract_tables(image)

        if not table or len(table) < 2:
            st.error("No table detected.")
        else:
            json_output = flatten_tables(table, uploaded_file.name)

            st.success("✅ Extraction successful")

            st.subheader("JSON Output")
            st.json(json_output)

            st.download_button(
                label="⬇️ Download JSON",
                data=json.dumps(json_output, indent=2),
                file_name="tables.json",
                mime="application/json"
            )

    except Exception as e:
        st.error(f"❌ Error during extraction: {e}")
