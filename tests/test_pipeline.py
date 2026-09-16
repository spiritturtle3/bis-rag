from pathlib import Path

from app.database.models import BISStandard
from app.ingestion.pipeline import ingest_standard


def test_ingest_standard():
    pdf_path = Path("data/test/sample.pdf")

    standard = BISStandard(
        standardNumber="TEST-001",
        title="Sample Steel Pipes Standard",
        issuingOrganization="Bureau of Indian Standards",
        scope="Requirements for steel pipes used for water supply.",
        category="Product Standard",

        productDetails={
            "productType": "Steel Pipes",
            "productCategory": "Piping",
            "intendedUses": ["Water supply"],
        },

        keywords=[
            "steel pipes",
            "water supply",
            "piping",
        ],

        currentEdition={
            "year": 2026,
            "publishedDate": "2026-01-01",
            "status": "Active",
        },

        amendments=[],

        technicalRequirements={
            "keyRequirements": [
                "Dimensional requirements",
                "Mechanical properties",
            ],
            "testingAndInspection": {
                "required": True,
                "relatedTestStandard": None,
                "description": "Dimensional and mechanical testing.",
            },
        },

        alliedStandards=[],

        compliance={
            "mandatory": False,
            "certificationRequired": False,
            "schemes": [],
            "certificationBody": None,
            "qualityControlOrder": False,
            "notes": "Synthetic test record.",
        },

        procurementRelevance={
            "recommendedFor": ["Water supply procurement"],
            "buyerConsiderations": [
                "Check dimensions",
                "Check mechanical properties",
            ],
        },

        applicableDomains=[
            "Water supply",
            "Piping",
        ],

        language="en",

        source={
            "sourceType": "BIS",
            "sourceName": "Test BIS Source",
            "sourceUrl": "https://example.com",
            "retrievedDate": "2026-09-14",
            "verified": False,
        },
    )

    count = ingest_standard(
        str(pdf_path),
        standard,
    )

    assert count > 0