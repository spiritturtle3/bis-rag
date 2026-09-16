from app.database.models import BISStandard


def standard_to_text(standard: BISStandard) -> str:
    """
    Convert a BISStandard record into searchable text.

    The output intentionally includes:
    - standard identity
    - scope
    - product details
    - keywords
    - technical requirements
    - testing information
    - allied standards
    - edition/amendment information
    - compliance
    - procurement relevance

    Empty fields are skipped.
    """

    sections = []

    # ---------------------------------------------------------
    # Identity
    # ---------------------------------------------------------

    sections.append(
        f"Standard Number: {standard.standardNumber}"
    )

    sections.append(
        f"Title: {standard.title}"
    )

    if standard.issuingOrganization:
        sections.append(
            f"Issuing Organization: "
            f"{standard.issuingOrganization}"
        )

    if standard.category:
        sections.append(
            f"Category: {standard.category}"
        )

    if standard.applicableDomains:
        sections.append(
            "Applicable Domains: "
            + ", ".join(standard.applicableDomains)
        )

    # ---------------------------------------------------------
    # Scope
    # ---------------------------------------------------------

    if standard.scope.strip():
        sections.append(
            f"Scope: {standard.scope}"
        )

    # ---------------------------------------------------------
    # Product Details
    # ---------------------------------------------------------

    product = standard.productDetails

    product_lines = []

    if product.productType:
        product_lines.append(
            f"Product Type: {product.productType}"
        )

    if product.productCategory:
        product_lines.append(
            f"Product Category: {product.productCategory}"
        )

    if product.productDescription:
        product_lines.append(
            f"Product Description: "
            f"{product.productDescription}"
        )

    if product.materials:
        product_lines.append(
            "Materials: "
            + ", ".join(product.materials)
        )

    if product.intendedUses:
        product_lines.append(
            "Intended Uses: "
            + ", ".join(product.intendedUses)
        )

    if product.applications:
        product_lines.append(
            "Applications: "
            + ", ".join(product.applications)
        )

    if product.synonyms:
        product_lines.append(
            "Synonyms: "
            + ", ".join(product.synonyms)
        )

    if product_lines:
        sections.append(
            "Product Details:\n"
            + "\n".join(product_lines)
        )

    # ---------------------------------------------------------
    # Keywords
    # ---------------------------------------------------------

    if standard.keywords:
        sections.append(
            "Keywords: "
            + ", ".join(standard.keywords)
        )

    # ---------------------------------------------------------
    # Technical Requirements
    # ---------------------------------------------------------

    technical = standard.technicalRequirements

    technical_lines = []

    if technical.keyRequirements:
        technical_lines.append(
            "Key Requirements: "
            + "; ".join(technical.keyRequirements)
        )

    if technical.materials:
        technical_lines.append(
            "Materials: "
            + "; ".join(technical.materials)
        )

    if technical.grades:
        technical_lines.append(
            "Grades: "
            + "; ".join(technical.grades)
        )

    if technical.dimensions:
        technical_lines.append(
            "Dimensions: "
            + "; ".join(technical.dimensions)
        )

    if technical.performanceRequirements:
        technical_lines.append(
            "Performance Requirements: "
            + "; ".join(
                technical.performanceRequirements
            )
        )

    if technical.designRequirements:
        technical_lines.append(
            "Design Requirements: "
            + "; ".join(
                technical.designRequirements
            )
        )

    if technical.specificationRequirements:
        technical_lines.append(
            "Specification Requirements: "
            + "; ".join(
                technical.specificationRequirements
            )
        )

    if technical_lines:
        sections.append(
            "Technical Requirements:\n"
            + "\n".join(technical_lines)
        )

    # ---------------------------------------------------------
    # Testing and Inspection
    # ---------------------------------------------------------

    testing = standard.testingAndInspection

    testing_lines = []

    if testing.required is not None:
        testing_lines.append(
            f"Testing Required: {testing.required}"
        )

    if testing.testMethods:
        testing_lines.append(
            "Test Methods: "
            + "; ".join(testing.testMethods)
        )

    if testing.relatedTestStandards:
        testing_lines.append(
            "Related Test Standards: "
            + "; ".join(
                testing.relatedTestStandards
            )
        )

    if testing.inspectionRequirements:
        testing_lines.append(
            "Inspection Requirements: "
            + "; ".join(
                testing.inspectionRequirements
            )
        )

    if testing_lines:
        sections.append(
            "Testing and Inspection:\n"
            + "\n".join(testing_lines)
        )

    # ---------------------------------------------------------
    # Allied Standards
    # ---------------------------------------------------------

    allied_lines = []

    for allied in standard.alliedStandards:
        line = (
            f"{allied.standardNumber} "
            f"({allied.relationshipType})"
        )

        if allied.title:
            line += f": {allied.title}"

        if allied.description:
            line += f" — {allied.description}"

        allied_lines.append(line)

    if allied_lines:
        sections.append(
            "Allied Standards:\n"
            + "\n".join(allied_lines)
        )

    # ---------------------------------------------------------
    # Edition
    # ---------------------------------------------------------

    if standard.currentEdition:
        edition = standard.currentEdition

        edition_lines = []

        if edition.edition:
            edition_lines.append(
                f"Edition: {edition.edition}"
            )

        if edition.year:
            edition_lines.append(
                f"Year: {edition.year}"
            )

        if edition.publishedDate:
            edition_lines.append(
                f"Published Date: {edition.publishedDate}"
            )

        if edition.status:
            edition_lines.append(
                f"Status: {edition.status}"
            )

        if edition_lines:
            sections.append(
                "Current Edition:\n"
                + "\n".join(edition_lines)
            )

    # ---------------------------------------------------------
    # Amendments
    # ---------------------------------------------------------

    amendment_lines = []

    for amendment in standard.amendments:
        line_parts = []

        if amendment.amendmentNumber:
            line_parts.append(
                amendment.amendmentNumber
            )

        if amendment.date:
            line_parts.append(amendment.date)

        if amendment.title:
            line_parts.append(amendment.title)

        line = " — ".join(line_parts)

        if amendment.description:
            line += f": {amendment.description}"

        if line:
            amendment_lines.append(line)

    if amendment_lines:
        sections.append(
            "Amendments:\n"
            + "\n".join(amendment_lines)
        )

    # ---------------------------------------------------------
    # Compliance
    # ---------------------------------------------------------

    compliance = standard.compliance

    compliance_lines = []

    if compliance.mandatory is not None:
        compliance_lines.append(
            f"Mandatory: {compliance.mandatory}"
        )

    if compliance.certificationRequired is not None:
        compliance_lines.append(
            "Certification Required: "
            f"{compliance.certificationRequired}"
        )

    if compliance.certificationScheme:
        compliance_lines.append(
            "Certification Scheme: "
            f"{compliance.certificationScheme}"
        )

    if compliance.schemes:
        compliance_lines.append(
            "Schemes: "
            + ", ".join(compliance.schemes)
        )

    if compliance.qualityControlOrder is not None:
        compliance_lines.append(
            "Quality Control Order: "
            f"{compliance.qualityControlOrder}"
        )

    if compliance.crsApplicability is not None:
        compliance_lines.append(
            f"CRS Applicability: "
            f"{compliance.crsApplicability}"
        )

    if compliance.hallmarkingApplicability is not None:
        compliance_lines.append(
            "Hallmarking Applicability: "
            f"{compliance.hallmarkingApplicability}"
        )

    if compliance.certificationBody:
        compliance_lines.append(
            "Certification Body: "
            f"{compliance.certificationBody}"
        )

    if compliance.notes:
        compliance_lines.append(
            f"Compliance Notes: {compliance.notes}"
        )

    if compliance_lines:
        sections.append(
            "Compliance:\n"
            + "\n".join(compliance_lines)
        )

    # ---------------------------------------------------------
    # Procurement Relevance
    # ---------------------------------------------------------

    procurement = standard.procurementRelevance

    procurement_lines = []

    if procurement.applicableToProcurement is not None:
        procurement_lines.append(
            "Applicable to Procurement: "
            f"{procurement.applicableToProcurement}"
        )

    if procurement.recommendedFor:
        procurement_lines.append(
            "Recommended For: "
            + ", ".join(
                procurement.recommendedFor
            )
        )

    if procurement.specificationPoints:
        procurement_lines.append(
            "Specification Points: "
            + "; ".join(
                procurement.specificationPoints
            )
        )

    if procurement.buyerConsiderations:
        procurement_lines.append(
            "Buyer Considerations: "
            + "; ".join(
                procurement.buyerConsiderations
            )
        )

    if procurement.procurementKeywords:
        procurement_lines.append(
            "Procurement Keywords: "
            + ", ".join(
                procurement.procurementKeywords
            )
        )

    if procurement_lines:
        sections.append(
            "Procurement Relevance:\n"
            + "\n".join(procurement_lines)
        )

    return "\n\n".join(sections)