import pymupdf


def extract_pdf(pdf_path: str) -> list[dict]:
    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text").strip()

        pages.append({
            "page": page_number,
            "text": text
        })

    document.close()

    return pages