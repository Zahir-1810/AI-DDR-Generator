import streamlit as st
import os
import re
import base64
import io
import markdown
from xhtml2pdf import pisa
from dotenv import load_dotenv
from extractor import extract_content_from_pdf
from ai_synthesizer import generate_ddr_report

st.set_page_config(page_title="Applied AI Builder-DDR Generator", page_icon="🏢", layout="wide")

def embed_images_as_base64(markdown_text, images_dir):
    """Converts standard markdown image links into embedded base64 strings so Streamlit can render them natively"""
    def replacer(match):
        alt_text = match.group(1)
        filepath = match.group(2)
        # We know filepath is like 'images/filename.jpg'
        filename = os.path.basename(filepath)
        full_path = os.path.join(images_dir, filename)
        
        if os.path.exists(full_path):
            with open(full_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                ext = filename.split(".")[-1].lower()
                mime_type = "image/png" if ext == "png" else "image/jpeg"
                return f"![{alt_text}](data:{mime_type};base64,{encoded_string})"
        # If file not found, explicitly show "Image Not Available" text instead of a broken generic markdown icon
        return f"**[⚠️ Image Not Available: {alt_text}]**"
        
    pattern = r"\!\[([^\]]*)\]\((images/[^\)]+)\)"
    return re.sub(pattern, replacer, markdown_text)

def get_pdf_buffer(markdown_text, images_dir):
    def replacer(match):
        alt_text = match.group(1)
        filepath = match.group(2)
        filename = os.path.basename(filepath)
        full_path = os.path.abspath(os.path.join(images_dir, filename))
        full_path = full_path.replace("\\", "/")
        if os.path.exists(full_path):
            return f"![{alt_text}]({full_path})"
        return f"**[⚠️ Image Not Available: {alt_text}]**"
    
    pattern = r"\!\[([^\]]*)\]\((images/[^\)]+)\)"
    pdf_md = re.sub(pattern, replacer, markdown_text)
    
    html_content = markdown.markdown(pdf_md, extensions=['tables'])
    
    styled_html = f"""
    <html>
    <head>
    <style>
        @page {{ size: a4 portrait; margin: 2cm; }}
        body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; color: #333; line-height: 1.5; }}
        h1 {{ color: #2C3E50; font-size: 24pt; }}
        h2 {{ color: #34495E; border-bottom: 1px solid #ccc; padding-bottom: 5px; font-size: 16pt; margin-top: 20px; }}
        h3, h4 {{ color: #34495E; font-size: 13pt; margin-top: 15px; }}
        img {{ max-width: 100%; height: auto; display: block; margin: 15px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-block-end: 15px; page-break-inside: avoid; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
    </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """
    
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(styled_html, dest=buffer)
    if pisa_status.err:
        return None
    buffer.seek(0)
    return buffer

def main():
    st.title("Applied AI Builder-DDR Report Generation")
    st.write("Convert raw Inspection & Thermal PDF Reports into structured, client-ready DDR-Report through the power of multimodal AI.")
    
    # Init directories
    input_dir = "data/streamlit_uploads"
    output_dir = "output"
    images_dir = os.path.join(output_dir, "images")
    for d in [input_dir, output_dir, images_dir]:
        os.makedirs(d, exist_ok=True)
    
    # Sidebar
    st.sidebar.header("How It Works")
    st.sidebar.write("Upload both PDFs.")
    st.sidebar.write("Extract text and images.")
    st.sidebar.write("Merge findings into a DDR.")
    st.sidebar.write("Review and export the output.")
    st.sidebar.write("Download the Report as PDF")
    st.sidebar.header("Configuration")

    # Load API Key securely (Works for both Local .env and Streamlit Cloud st.secrets)
    load_dotenv()
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY", "")
    st.sidebar.warning("Note: The model takes 15-30 seconds to run because it parses heavy image files and performs rigorous contextual reasoning.")    


    # Main UI
    col1, col2 = st.columns(2)
    with col1:
        inspection_file = st.file_uploader("Upload Inspection Report (PDF)", type=["pdf"])
    with col2:
        thermal_file = st.file_uploader("Upload Thermal Report (PDF)", type=["pdf"])
        
    if st.button("Generate Diagnostic Report (DDR)", type="primary"):
        if not api_key:
            st.error("Missing Gemini API Key! If running locally, add it to `.env`. If deployed on Streamlit Cloud, add it to **App Settings -> Secrets**.")
            return
            
        if inspection_file and thermal_file:
            with st.spinner("Step 1/2: Extracting raw text and images from PDFs..."):
                # Save uploaded files temporarily
                insp_path = os.path.join(input_dir, "inspection_upload.pdf")
                therm_path = os.path.join(input_dir, "thermal_upload.pdf")
                
                with open(insp_path, "wb") as f:
                    f.write(inspection_file.getbuffer())
                with open(therm_path, "wb") as f:
                    f.write(thermal_file.getbuffer())
                    
                # Extract
                insp_text, insp_images = extract_content_from_pdf(insp_path, "Inspection", images_dir)
                therm_text, therm_images = extract_content_from_pdf(therm_path, "Thermal", images_dir)
                
                combined_text = insp_text + "\n\n" + therm_text
                all_images = insp_images + therm_images
            
            with st.spinner(f"Step 2/2: Prompting Gemini Multimodal with {len(all_images)} extracted images. This takes ~30 seconds..."):
                try:
                    report_markdown = generate_ddr_report(combined_text, all_images)
                    if report_markdown:
                        # Process markdown to show images in streamlit natively
                        rendered_md = embed_images_as_base64(report_markdown, images_dir)
                        
                        st.success("✅ DDR Generated Successfully!")
                        st.markdown("---")
                        # Display
                        st.markdown(rendered_md, unsafe_allow_html=True)
                        
                        # Provide download link for PDF
                        pdf_buffer = get_pdf_buffer(report_markdown, images_dir)
                        if pdf_buffer:
                            st.markdown("---")
                            st.download_button(
                                label="📥 Download DDR Report as PDF",
                                data=pdf_buffer,
                                file_name="Final_DDR_Report.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.error("Failed to generate PDF file.")
                    else:
                        st.error("Gemini failed to return a string. Please check the logs.")
                except Exception as e:
                    st.error(f"Error communicating with Gemini: {e}")
                    
        else:
            st.warning("Please upload both the Inspection and Thermal PDFs to continue.")

if __name__ == "__main__":
    main()
