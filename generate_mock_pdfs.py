from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw
import os

def create_test_image(filename, text, color):
    img = Image.new('RGB', (400, 300), color=color)
    d = ImageDraw.Draw(img)
    d.text((50, 150), text, fill=(255, 255, 255))
    img.save(filename)

os.makedirs("data", exist_ok=True)

try:
    create_test_image("insp_test.jpg", "Visual Image: Roof Damage", (100, 50, 50))
    create_test_image("therm_test.jpg", "Thermal Image: Roof Heat Loss", (50, 50, 200))

    def create_pdf(path, title, img_path, text_content):
        c = canvas.Canvas(path, pagesize=letter)
        c.drawString(100, 750, title)
        c.drawString(100, 730, text_content)
        c.drawImage(img_path, 100, 400, width=400, height=300)
        c.save()

    create_pdf("data/inspection_report.pdf", "Visual Inspection Report", "insp_test.jpg", "Observation: The Roof shows visible missing shingles. See photo below.")
    create_pdf("data/thermal_report.pdf", "Thermal Imaging Report", "therm_test.jpg", "Observation: High heat loss (blue area) detected at the Roof. See thermal scan below.")

    print("Successfully replaced PDFs for demonstration.")
finally:
    if os.path.exists("insp_test.jpg"): os.remove("insp_test.jpg")
    if os.path.exists("therm_test.jpg"): os.remove("therm_test.jpg")
