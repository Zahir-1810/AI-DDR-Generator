import fitz

def main():
    try:
        doc = fitz.open("data/Main DDR.pdf")
        text = []
        for page in doc:
            text.append(page.get_text())
        with open("main_ddr_text.txt", "w", encoding="utf-8") as f:
            f.write("\n==========================\n".join(text))
        print("Success")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
