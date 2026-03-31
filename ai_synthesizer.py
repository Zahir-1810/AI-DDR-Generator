from google import genai
from PIL import Image
import os
from dotenv import load_dotenv

def get_gemini_client():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file. Please check your instructions on how to get one.")
    
    # Initialize the GenAI client
    return genai.Client(api_key=api_key)

def generate_ddr_report(text_data, image_paths):
    client = get_gemini_client()
    
    system_prompt = """
You are an expert property inspector and AI workflow engine.
Your task is to analyze the provided raw textual observations and extracted thermal/visual images to generate a structured Detailed Diagnostic Report (DDR).

== REQUIRED STRUCTURE ==
Your output MUST strictly follow the overall structure of this reference report template, incorporating all the extracted text data natively:

# COVER PAGE
- Report Date: [Current Date]
- Prepared By: [Inspector Name/UrbanRoof]
- Prepared For: [Extract or Guess Client Address/Name, otherwise output `[To be filled]`]

# SECTION 1 INTRODUCTION
## 1.1 BACKGROUND
[Brief introduction based on the extracted data, e.g., "Preliminary Health Assessment of the property based on visual and thermal testing."]
## 1.2 OBJECTIVE OF THE HEALTH ASSESSMENT
- To facilitate detection of flaws and prioritize repair.
- Evaluate scope of work.
## 1.3 SCOPE OF WORK
[Summarize tools and inspection methodology from data]

# SECTION 2 GENERAL INFORMATION
## 2.1 CLIENT & INSPECTION DETAILS
| Particular | Description |
|---|---|
| Customer Name | [Extracted or `[To be filled]`] |
| Site Address | [Extracted or `[To be filled]`] |
| Date of Inspection | [Extracted] |
## 2.2 DESCRIPTION OF SITE
| Particular | Description |
|---|---|
| Type of structure | [Extracted] |
| Age/Year | [Extracted] |

# SECTION 3 VISUAL OBSERVATION AND READINGS
Group observations by Area (Bathrooms, Balcony, Terrace, External Wall etc.)
For each area, provide a SUMMARY.
Create Data Tables or Checklists for Negative Side Inputs (Condition of leakage, season) and Positive Side Inputs (Gaps in tiles, broken tiles, etc.).
Use Markdown Tables with checkmarks (✓) for structured "Yes/No/Not sure" items based on the provided text.

# SECTION 4 ANALYSIS & SUGGESTIONS
## 4.1 ACTIONS REQUIRED & SUGGESTED THERAPIES
Discuss suggested repair treatments for each area (Grouting, Plumbing, Plastering, Waterproofing).
## 4.3 SUMMARY TABLE
Create a final table of recommended treatments per area.
## 4.4 & 4.5 PICTORIAL REFERENCES
Detailed observations tied directly with Images.

# SECTION 5 LIMITATION AND PRECAUTION NOTE
Add a standard disclaimer about the report being a visual/thermal assessment and subject to limitations.

== CONTENT RULES ==
- NEVER invent facts (hallucinate). Check the data carefully. Put `[N/A]` if unknown.
- Keep formatting clean using standard Markdown (Headers, Bold, Tables).

== IMAGE RULES ==
- Under Section 4.4 and Section 4.5 (Pictorial References), YOU MUST embed the relevant images under the correct observation using standard markdown: `![Observation description here](images/FILENAME)`.
- Replace FILENAME with the exact filename provided to you.
- Ensure the image path precisely follows `images/the_exact_filename.jpg` without any extra subdirectories or absolute paths. Just `images/FILENAME`.
- Mention "Image Not Available" if missing.
"""

    user_prompt = f"""
Here is the raw text from the visual inspection and thermal reports:
---
{text_data}
---

The following are the filenames of the images successfully extracted from these reports. These images are attached to this very prompt natively.
"""

    contents = [system_prompt, user_prompt]
    
    for path in image_paths:
        try:
            filename = os.path.basename(path)
            contents.append(f"Image Filename: {filename}")
            img = Image.open(path)
            contents.append(img)
        except Exception as e:
            print(f"Could not load image {path} to attach to prompt.")
            
    print(f"Sending multimodal request to Gemini API ({len(image_paths)} images attached)...")
    
    # Using Gemini 2.5 Flash / 1.5 Pro via api
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents
    )
    
    return response.text
