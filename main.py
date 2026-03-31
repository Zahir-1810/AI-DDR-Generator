import os
from extractor import extract_content_from_pdf
from ai_synthesizer import generate_ddr_report

def main():
    print("Welcome to the DDR AI Generator Workflow!")
    
    # 1. Setup paths
    input_dir = "data"
    output_dir = "output"
    images_dir = os.path.join(output_dir, "images")
    
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"Created {input_dir}/ directory. Please place your PDFs here.")
        
    inspection_pdf = os.path.join(input_dir, "inspection_report.pdf")
    thermal_pdf = os.path.join(input_dir, "thermal_report.pdf")
    
    for required_file in [inspection_pdf, thermal_pdf]:
        if not os.path.exists(required_file):
            print(f"❌ Error: Could not find '{required_file}'. Please place it in the 'data' folder.")
            return

    # 2. Extract Data
    print("\n--- Step 1: Extracting Text & Images ---")
    insp_text, insp_images = extract_content_from_pdf(inspection_pdf, "Inspection", images_dir)
    therm_text, therm_images = extract_content_from_pdf(thermal_pdf, "Thermal", images_dir)
    
    combined_text = insp_text + "\n\n" + therm_text
    all_images = insp_images + therm_images
    
    print(f"Extracted {len(all_images)} images and combined text successfully.")

    # 3. AI Synthesize DDR
    print("\n--- Step 2: AI Workflow (Gemini) ---")
    try:
        report_markdown = generate_ddr_report(combined_text, all_images)
        
        # 4. Save Output
        if report_markdown:
            output_file = os.path.join(output_dir, "DDR_Final_Report.md")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_markdown)
            print(f"\n✅ Success! The final report was saved to: {output_file}")
            print(f"✅ Extracted images are saved in: {images_dir}/")
        else:
            print("\n❌ Error generating report from Gemini.")
            
    except Exception as e:
        print(f"\n❌ Pipeline Error: {e}")

if __name__ == "__main__":
    main()
