import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
import zipfile


st.title("Bulk PDF Creator - Certificates")
uploaded_file = st.file_uploader("Choose a PDF template", type="pdf")

# Collect list of names
names_input = st.text_area("Enter names (one per line):", "John Doe\nJane Smith\nBob Johnson")
names_list = names_input.splitlines()
event_name = st.text_input("Enter the Event Name", "Annual Day")
event_date = st.text_input("Enter the Event Date", "2024-09-17")

# Button to start generation
if st.button("Generate PDFs"):
    if uploaded_file is not None and names_list and event_name and event_date:
        # Create a BytesIO buffer for the ZIP file
        zip_buffer = BytesIO()

        # Open the ZIP file in write mode
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            template_pdf = uploaded_file.read()

            for name in names_list:
                with fitz.open(stream=template_pdf, filetype="pdf") as pdf:
                    page = pdf[0]  # Assuming the text is on the first page

                    placeholders = {
                        "{name}": name,
                        "{date}": event_date,
                        "{event}": event_name
                    }

                    for placeholder, value in placeholders.items():
                        instance = page.search_for(placeholder)
                        if instance:
                            inst = instance[0]  # Get the first instance
                            page.add_redact_annot(inst, value, fontsize=24,fontname="helv",align=fitz.TEXT_ALIGN_CENTER)

                    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

                    pdf_output = BytesIO()
                    pdf.save(pdf_output)
                    pdf_output.seek(0)

                    zip_file.writestr(f"{name}_certificate.pdf", pdf_output.read())

        # Prepare the ZIP file for download
        zip_buffer.seek(0)

        # Download the ZIP file
        st.download_button(
            label="Download All Certificates as ZIP",
            data=zip_buffer,
            file_name="certificates.zip",
            mime="application/zip"
        )
    else:
        st.error("Please upload a PDF, enter names, event name, and date.")
