# Applied AI Builder - DDR Generator 🏢

An AI-powered tool designed to automate the generation of **Detailed Diagnostic Reports (DDR)** for property inspections. By combining raw Visual Inspection and Thermal Imaging PDF reports, this application leverages Google's **Gemini Multimodal API** to construct comprehensive, client-ready structural health assessments.

---

## 🚀 Key Features

- **Automated Data Extraction**: Safely extracts readable text and high-res images from uploaded PDFs using `PyMuPDF`.
- **Multimodal AI Synthesis**: Prompts Gemini 2.5 Flash / 1.5 Pro with large context sizes to intelligently collate text and photos without hallucinating data.
- **Reference-Targeted Structuring**: Output is generated into a strict 5-part layout exactly like industry-standard reports (Cover, Intro, General Info, Visual Observations, Analysis & Therapies).
- **Direct PDF Export**: Transforms the multimodal Markdown output—including base64/local image embeddings—directly into a stylised, formatted, downloadable `.pdf` file using pure Python libraries (`xhtml2pdf`).
- **User-Friendly Interface**: Built with `Streamlit` for a clean, browser-based drag-and-drop workflow.

---

## 🛠️ Architecture

1. **`app.py`**: The Streamlit frontend. Handles file uploads, binds the extractor and synthesizer pipelines, renders visual markdown, and initiates the PDF byte-stream generation.
2. **`extractor.py`**: Extracts the text natively by pages and captures all relevant images above a defined resolution threshold. 
3. **`ai_synthesizer.py`**: Contains the meticulously crafted system prompt templates and handles API communication with Google's GenAI tools.

---

## 💻 Installation & Local Usage

### Prerequisites
- Python 3.9+
- A [Google Gemini API Key](https://aistudio.google.com/)

### Step-by-Step

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd DDR-Report-Generator-main
   ```

2. **Set up a Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your API Key:**
   - Create a file named `.env` in the root folder.
   - Add your Gemini Key:
     ```env
     GEMINI_API_KEY="your-api-key-here"
     ```

5. **Run the Application:**
   ```bash
   streamlit run app.py
   ```
   The Streamlit server will launch and provide a local interface on `http://localhost:8501`.

---

## 📄 How to Use

1. Open the application.
2. In the "**Upload Inspection Report**" zone, upload the raw visual `.pdf` file.
3. In the "**Upload Thermal Report**" zone, upload the associated thermal reading `.pdf` file.
4. Click **Generate Diagnostic Report (DDR)**.
   - *Wait ~15-30 seconds as the multimodal LLM reasons through the documents and images.*
5. Review the rendered report directly on the main page.
6. Click **Download DDR Report as PDF** to save the generated document to your device. 

---

## 📦 Dependencies

- `streamlit`: For Web UI
- `google-genai`: Connects to Gemini's generative models
- `PyMuPDF (fitz)`: To extract texts and images efficiently
- `markdown` & `xhtml2pdf`: Converts the AI's markdown response (with image paths) into the final exportable PDF
- `python-dotenv`: Environment variable management
- `Pillow`: Image buffering and payload prep

---

## 🔒 Limitations & Precautions
- **Image Over-Saturation**: If PDFs have 50+ images, process extraction limits them logically so the LLM context window isn't overloaded.
- **AI Hallucinations**: While tightly constrained via system prompting, always give the final DDR report a quick visual skim to ensure the AI associated the exact correct image with the specific textual observation.
