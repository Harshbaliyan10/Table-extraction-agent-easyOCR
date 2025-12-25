import streamlit as st
import tempfile
import os
import json

from extract_text import extract_tables_from_image

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Table Extraction Agent",
    layout="wide"
)

st.title("📊 Table Extraction Agent (EasyOCR)")
st.write("Upload an image containing a table. Output will be generated in **JSON format**.")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload image",
    type=["png", "jpg", "jpeg"]
)

# ---------------- PROCESS IMAGE ----------------
if uploaded_file is not None:
    # Save uploaded image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(uploaded_file.getbuffer())
        image_path = tmp.name

    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    try:
        # ✅ EasyOCR table extraction
        json_output = extract_tables_from_image(
            image_path=image_path,
            image_name=uploaded_file.name,
            table_id=0
        )

        # Show JSON output
        st.subheader("📄 Extracted JSON")
        st.json(json_output)

        # Save JSON (overwrite every run)
        output_file = "tables.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json_output, f, indent=2)

        st.success("✅ Extraction completed. JSON saved.")

        # Download button
        with open(output_file, "rb") as f:
            st.download_button(
                label="⬇️ Download JSON",
                data=f,
                file_name="tables.json",
                mime="application/json"
            )

    except Exception as e:
        st.error(f"❌ Error during extraction: {e}")

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)
