from app.ingestion.standard_normalizer import normalize_standard_number


def test_normalize_part_spacing():
    assert normalize_standard_number(
        "IS 3370 (Part1):2021"
    ) == "IS 3370 (Part 1):2021"


def test_normalize_existing_spacing():
    assert normalize_standard_number(
        "IS 3370 (Part 1):2021"
    ) == "IS 3370 (Part 1):2021"


def test_normalize_multiple_spaces():
    assert normalize_standard_number(
        "IS  4651(Part 4):2023"
    ) == "IS 4651(Part 4):2023"