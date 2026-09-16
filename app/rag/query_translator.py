import re


# Common Hindi procurement/engineering terms mapped to
# English terms already present in our BIS dataset.
HINDI_TERMS = {
    "पानी": "water",
    "जल": "water",
    "टंकी": "tank",
    "भंडारण": "storage",
    "भंडारण टंकी": "storage tank",
    "कंक्रीट": "concrete",
    "प्रबलित": "reinforced",
    "सीमेंट": "cement",
    "नींव": "foundation",
    "निर्माण": "construction",
    "डिजाइन": "design",
    "मिट्टी": "soil",
    "जांच": "investigation",
    "परीक्षण": "testing",
    "पाइप": "pipe",
    "जल निकासी": "drainage",
    "सीवर": "sewerage",
    "ईंट": "brick",
    "दरवाजा": "door",
    "खिड़की": "window",
    "भूकंप": "earthquake",
    "औद्योगिक": "industrial",
    "माप": "measurement",
}


def translate_query(query: str) -> str:
    """
    Convert common Hindi BIS/procurement terms into
    English search terms.

    Unknown words are preserved.
    """

    if not query or not query.strip():
        return ""

    translated = query.strip()

    # Replace longer phrases first.
    terms = sorted(
        HINDI_TERMS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for hindi, english in terms:
        translated = translated.replace(
            hindi,
            english,
        )

    # Remove duplicate whitespace.
    translated = re.sub(
        r"\s+",
        " ",
        translated,
    ).strip()

    return translated