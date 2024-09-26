import streamlit as st
from PIL import Image
import pytesseract
import easyocr
import numpy as np
import fitz 

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def extract_text_with_pytesseract(image):
    text = pytesseract.image_to_string(image)
    return text

def extract_text_with_easyocr(image):
    reader = easyocr.Reader(["en"])
    result = reader.readtext(image)
    text = " ".join([res[1] for res in result])
    return text

def image_to_text(image, ocr_technique):
    if ocr_technique == "PyTesseract":
        return extract_text_with_pytesseract(image)
    elif ocr_technique == "EasyOCR":
        return extract_text_with_easyocr(image)
    else:
        return "Invalid OCR technique selected."

def download_text(text, file_format):
    # Create a text file for the extracted text
    if file_format == "Text File":
        st.download_button(
            label="Download Text File",
            data=text,
            file_name="extracted_text.txt",
            mime="text/plain"
        )
    elif file_format == "JSON":
        import json
        st.download_button(
            label="Download JSON File",
            data=json.dumps({"extracted_text": text}),
            file_name="extracted_text.json",
            mime="application/json"
        )

def extract_images_from_pdf(uploaded_file):
    images = []
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")  # Read the file from memory
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

def main():
    st.title("OCR Master: Image & PDF Text Extraction Tool")
    st.write("Upload an image or PDF and select an OCR technique to extract text.")

    # Sidebar for settings
    st.sidebar.header("Settings")
    ocr_technique = st.sidebar.selectbox(
        "Select OCR Technique:",
        ["PyTesseract", "EasyOCR"]
    )
    
    file_format = st.sidebar.selectbox(
        "Select Download Format:",
        ["Text File", "JSON"]
    )

    uploaded_file = st.file_uploader("Choose an image or PDF...", type=["jpg", "jpeg", "png", "pdf"])

    if uploaded_file is not None:
        try:
            if uploaded_file.type == "application/pdf":
                images = extract_images_from_pdf(uploaded_file)
                extracted_text = ""
                st.image(images[0], caption="First Page of PDF", use_column_width=True)

                for img in images:
                    with st.spinner("Extracting text..."):
                        extracted_text += image_to_text(np.array(img), ocr_technique) + "\n"

            else:
                image = Image.open(uploaded_file)
                image_array = np.array(image)
                st.image(image, caption="Uploaded Image", use_column_width=True)

                with st.spinner("Extracting text..."):
                    extracted_text = image_to_text(image_array, ocr_technique)

            st.subheader("Extracted Text:")
            st.text(extracted_text)

            if st.button("Download Extracted Text"):
                download_text(extracted_text, file_format)

        except Exception as e:
            st.error(f"Error: {e}")
            st.write("Please upload a valid image or PDF file.")

if __name__ == "__main__":
    main()
