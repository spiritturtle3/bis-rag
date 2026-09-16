import re


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text while preserving meaningful content.
    """

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove excessive spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove spaces around newlines
    text = re.sub(r" *\n *", "\n", text)

    return text.strip()