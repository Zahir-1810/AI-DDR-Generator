import fitz  # PyMuPDF
import os

def extract_content_from_pdf(pdf_path, prefix, output_dir="output/images"):
    """
    Extracts text and images from a PDF.
    Saves images locally to output_dir with the given prefix.
    Returns the full combined text, and a list of extracted image paths.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = fitz.open(pdf_path)
    full_text = []
    extracted_images = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Extract text from the page
        text = page.get_text()
        if text.strip():
            full_text.append(f"--- Page {page_num + 1} ({prefix} Report) ---\n{text}")

        # Extract images from the page
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            # Safe limit: stop if we've pulled 15 images from this document
            if len(extracted_images) >= 15:
                break
                
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Skip tiny images (usually logos, headers, vectors)
            if len(image_bytes) < 15000:
                continue
                
            # Generate a unique filename for the reference
            image_filename = f"{prefix}_page{page_num+1}_img{img_index+1}.{image_ext}"
            image_path = os.path.join(output_dir, image_filename)
            
            # Save the image
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            
            extracted_images.append(image_path)
            
        if len(extracted_images) >= 15:
            break
    
    doc.close()
    
    # Return exactly what we extracted so the LLM has everything
    combined_text = "\n\n".join(full_text)
    return combined_text, extracted_images
