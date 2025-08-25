import streamlit as st
import os
import tempfile
from pdf2image import convert_from_path
import pytesseract
from io import StringIO

def pdf_to_text(pdf_file):
    """Convert PDF to text using OCR"""
    
    # Create a temporary file to save the uploaded PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(pdf_file.read())
        tmp_file_path = tmp_file.name
    
    try:
        # Convert PDF pages to images
        pages = convert_from_path(tmp_file_path)
        
        # OCR each page and collect text
        full_text = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, page in enumerate(pages, start=1):
            status_text.text(f"Processing page {i}/{len(pages)}...")
            progress_bar.progress(i / len(pages))
            
            text = pytesseract.image_to_string(page)
            full_text.append(text)
        
        status_text.text("OCR processing complete!")
        return "\n".join(full_text)
    
    finally:
        # Clean up temporary file
        os.unlink(tmp_file_path)

def main():
    st.set_page_config(
        page_title="PDF to Text OCR",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 PDF to Text OCR Converter")
    st.markdown("Upload a PDF file and convert it to text using OCR (Optical Character Recognition)")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF file to extract text using OCR"
    )
    
    if uploaded_file is not None:
        # Display file details
        st.success(f"File uploaded: {uploaded_file.name}")
        st.info(f"File size: {uploaded_file.size / 1024:.2f} KB")
        
        # Process button
        if st.button("🔍 Extract Text", type="primary"):
            with st.spinner("Processing PDF... This may take a few moments."):
                try:
                    # Convert PDF to text
                    extracted_text = pdf_to_text(uploaded_file)
                    
                    if extracted_text.strip():
                        st.success("✅ Text extraction completed!")
                        
                        # Display statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Characters", len(extracted_text))
                        with col2:
                            st.metric("Words", len(extracted_text.split()))
                        with col3:
                            st.metric("Lines", len(extracted_text.split('\n')))
                        
                        # Text area for easy copying
                        st.markdown("### 📝 Extracted Text")
                        st.text_area(
                            "Copy the text below:",
                            value=extracted_text,
                            height=400,
                            help="Select all text (Ctrl+A) and copy (Ctrl+C) to use elsewhere",
                            key="extracted_text"
                        )
                        
                        # Download button as backup
                        st.download_button(
                            label="💾 Download as TXT file",
                            data=extracted_text,
                            file_name=f"{uploaded_file.name.replace('.pdf', '')}_extracted.txt",
                            mime="text/plain"
                        )
                        
                    else:
                        st.warning("⚠️ No text could be extracted from the PDF. The file might contain only images or be corrupted.")
                
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")
                    st.info("Make sure the PDF file is not corrupted and contains readable content.")
    
    # Instructions
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. **Upload** a PDF file using the file uploader above
        2. **Click** the "Extract Text" button to start OCR processing
        3. **Wait** for the processing to complete (may take a few moments for large files)
        4. **Copy** the extracted text from the text area
        5. **Download** the text as a .txt file if needed (optional)
        
        **Note:** This tool uses OCR (Optical Character Recognition) to extract text from PDF files.
        It works best with clear, high-quality scanned documents or image-based PDFs.
        """)
    
    # Technical info
    with st.expander("🔧 Technical Details"):
        st.markdown("""
        This application uses:
        - **pdf2image** to convert PDF pages to images
        - **pytesseract** (Tesseract OCR) to extract text from images
        - **Streamlit** for the web interface
        
        The OCR process converts each page of your PDF into an image and then
        uses machine learning to recognize and extract the text content.
        """)

if __name__ == "__main__":
    main()