from pydantic import BaseModel, Field
from typing import Optional


class ProductDetails(BaseModel):
    productType: Optional[str] = None
    productCategory: Optional[str] = None
    productDescription: Optional[str] = None
    materials: list[str] = Field(default_factory=list)
    intendedUses: list[str] = Field(default_factory=list)
    applications: list[str] = Field(default_factory=list)
    synonyms: list[str] = Field(default_factory=list)


class TechnicalRequirements(BaseModel):
    keyRequirements: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    grades: list[str] = Field(default_factory=list)
    dimensions: list[str] = Field(default_factory=list)
    performanceRequirements: list[str] = Field(default_factory=list)
    designRequirements: list[str] = Field(default_factory=list)
    specificationRequirements: list[str] = Field(default_factory=list)


class TestingAndInspection(BaseModel):
    required: Optional[bool | str] = None
    testMethods: list[str] = Field(default_factory=list)
    relatedTestStandards: list[str] = Field(default_factory=list)
    inspectionRequirements: list[str] = Field(default_factory=list)


class AlliedStandard(BaseModel):
    standardNumber: str
    relationshipType: str
    title: Optional[str] = None
    description: Optional[str] = None


class Edition(BaseModel):
    edition: Optional[str] = None
    year: Optional[int] = None
    publishedDate: Optional[str] = None
    status: Optional[str] = None


class Amendment(BaseModel):
    amendmentNumber: Optional[str] = None
    date: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class Compliance(BaseModel):
    mandatory: Optional[bool | str] = None
    certificationRequired: Optional[bool | str] = None
    certificationScheme: Optional[str] = None
    schemes: list[str] = Field(default_factory=list)
    qualityControlOrder: Optional[bool | str] = None
    crsApplicability: Optional[bool | str] = None
    hallmarkingApplicability: Optional[bool | str] = None
    certificationBody: Optional[str] = None
    notes: Optional[str] = None


class ProcurementRelevance(BaseModel):
    applicableToProcurement: Optional[bool] = None
    recommendedFor: list[str] = Field(default_factory=list)
    specificationPoints: list[str] = Field(default_factory=list)
    buyerConsiderations: list[str] = Field(default_factory=list)
    procurementKeywords: list[str] = Field(default_factory=list)


class StandardRelationship(BaseModel):
    relatedStandardNumber: str
    relationshipType: str
    description: Optional[str] = None


class MultilingualTerms(BaseModel):
    language: str
    terms: list[str] = Field(default_factory=list)


class EvidenceReference(BaseModel):
    page: Optional[int] = None
    section: Optional[str] = None
    clause: Optional[str] = None


class Source(BaseModel):
    sourceType: Optional[str] = None
    sourceName: Optional[str] = None
    sourceUrl: Optional[str] = None
    url: Optional[str] = None
    publicationDate: Optional[str] = None
    retrievedDate: Optional[str] = None
    verified: bool = False
    evidenceReferences: list[EvidenceReference] = Field(default_factory=list)


class BISStandard(BaseModel):
    # Basic standard information
    standardNumber: str
    title: str
    issuingOrganization: str
    scope: str
    category: Optional[str] = None
    applicableDomains: list[str] = Field(default_factory=list)

    # Product information
    productDetails: ProductDetails = Field(
        default_factory=ProductDetails
    )

    keywords: list[str] = Field(default_factory=list)

    # Technical specifications
    technicalRequirements: TechnicalRequirements = Field(
        default_factory=TechnicalRequirements
    )

    # Testing and inspection
    testingAndInspection: TestingAndInspection = Field(
        default_factory=TestingAndInspection
    )

    # Allied standards
    # Kept as a list because this matches the current PDF/test format.
    alliedStandards: list[AlliedStandard] = Field(
        default_factory=list
    )

    # Current edition/version
    currentEdition: Optional[Edition] = None

    # Amendments
    amendments: list[Amendment] = Field(
        default_factory=list
    )

    # Compliance/certification
    compliance: Compliance = Field(
        default_factory=Compliance
    )

    # Procurement
    procurementRelevance: ProcurementRelevance = Field(
        default_factory=ProcurementRelevance
    )

    # Explicit relationships between standards
    standardRelationships: list[StandardRelationship] = Field(
        default_factory=list
    )

    # Language/multilingual support
    language: str = "en"
    multilingualTerms: list[MultilingualTerms] = Field(
        default_factory=list
    )

    # Source/evidence
    source: Source = Field(
        default_factory=Source
    )