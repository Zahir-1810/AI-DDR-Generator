import markdown
from xhtml2pdf import pisa
import os

source_md = """
# Test Report
This is a test.
![Test image](unavailable.png)
"""

def main():
    html_content = markdown.markdown(source_md)
    # Add some basic CSS for images and formatting
    styled_html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Helvetica, sans-serif; }}
        img {{ max-width: 100%; height: auto; }}
    </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """
    
    with open("test.pdf", "w+b") as result_file:
        pisa_status = pisa.CreatePDF(styled_html, dest=result_file)
        print("Success:", not pisa_status.err)

if __name__ == "__main__":
    main()
