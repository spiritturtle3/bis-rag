from app.ingestion.cleaner import clean_text


def test_clean_text():
    raw = "  Hello    world  \r\n\r\n\r\n  This is   a test.  "

    cleaned = clean_text(raw)

    assert cleaned == "Hello world\n\nThis is a test."