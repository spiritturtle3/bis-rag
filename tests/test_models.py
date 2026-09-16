from app.database.models import BISStandard


def test_bis_standard_model():
    data = {
        "standardNumber": "IS 3589:2001",
        "title": "Steel Pipes for Water and Sewage",
        "issuingOrganization": "Bureau of Indian Standards",
        "scope": "Requirements for steel pipes.",
        "category": "Product Standard",

        "productDetails": {
            "productType": "Steel Pipes",
            "productCategory": "Piping",
            "intendedUses": ["Water supply", "Sewage"]
        },

        "keywords": [
            "steel pipes",
            "water supply",
            "sewage"
        ],

        "currentEdition": {
            "year": 2001,
            "publishedDate": "2001-06-15",
            "status": "Active"
        },

        "amendments": [],

        "technicalRequirements": {
            "keyRequirements": [
                "Pipe dimensions",
                "Wall thickness"
            ],
            "testingAndInspection": {
                "required": True,
                "relatedTestStandard": "IS 2329:1968",
                "description": "Testing requirements."
            }
        },

        "alliedStandards": [],

        "compliance": {
            "mandatory": True,
            "certificationRequired": True,
            "schemes": ["BIS Product Certification"]
        },

        "procurementRelevance": {
            "recommendedFor": ["Water infrastructure"],
            "buyerConsiderations": ["Pipe dimensions"]
        },

        "applicableDomains": [
            "Construction",
            "Water Infrastructure"
        ],

        "language": "en",

        "source": {
            "sourceType": "BIS",
            "sourceName": "Bureau of Indian Standards",
            "sourceUrl": None,
            "retrievedDate": "2026-09-14",
            "verified": False
        }
    }

    standard = BISStandard(**data)

    assert standard.standardNumber == "IS 3589:2001"
    assert standard.productDetails.productType == "Steel Pipes"
    assert standard.currentEdition.year == 2001