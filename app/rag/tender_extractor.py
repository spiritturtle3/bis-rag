from pathlib import Path

import fitz


def extract_tender_text(pdf_path: str | Path) -> str:
    """
    Extract text from a tender PDF.

    Args:
        pdf_path: Path to the tender PDF.

    Returns:
        Extracted text from all PDF pages.

    Raises:
        FileNotFoundError: If the PDF does not exist.
        ValueError: If the file is not a PDF or contains no extractable text.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"Tender PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Input file must be a PDF.")

    pages = []

    with fitz.open(path) as document:
        for page in document:
            text = page.get_text("text").strip()

            if text:
                pages.append(text)

    extracted_text = "\n\n".join(pages).strip()

    if not extracted_text:
        raise ValueError(
            "No extractable text found in the tender PDF. "
            "The PDF may be scanned or image-based."
        )

    return extracted_text