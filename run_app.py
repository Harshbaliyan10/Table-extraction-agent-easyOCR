import streamlit as st
import tempfile
import os
import json

from extract_text import extract_tables, flatten_tables

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Table Extraction Agent",
    layout="wide"
)

st.title("📊 Table Extraction Agent")
st.write("Upload an image containing tables. Output will be generated in **JSON format**.")

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
        # Extract tables (raw)
        tables = extract_tables(image_path)

        # Convert to flattened JSON format
        json_output = flatten_tables(uploaded_file.name, tables)

        # Show JSON output in UI
        st.subheader("📄 Extracted JSON")
        st.json(json_output)

        # Save JSON file (overwrite each run)
        output_file = "tables.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json_output, f, indent=2)

        st.success("✅ Extraction completed. JSON saved as tables.json")

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
        # Cleanup temp file
        if os.path.exists(image_path):
            os.remove(image_path)
