# society/legal/constitution/ontology/domains.py

from enum import Enum


# ============================
# Legal Domains
# ============================

class LegalDomain(str, Enum):
    GOVERNANCE = "GOVERNANCE"
    PROPERTY = "PROPERTY"
    FINANCIAL = "FINANCIAL"
    SAFETY = "SAFETY"
    DISCIPLINE = "DISCIPLINE"
    MEMBERSHIP = "MEMBERSHIP"
    DATA = "DATA"
    PRIVACY = "PRIVACY"
    ACCESS = "ACCESS"
    COMMUNICATION = "COMMUNICATION"
    COMPLIANCE = "COMPLIANCE"
    SECURITY = "SECURITY"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    OPERATIONS = "OPERATIONS"
    ADMINISTRATION = "ADMINISTRATION"
    JUDICIARY = "JUDICIARY"
    EXECUTION = "EXECUTION"


# ============================
# Domain Semantics
# ============================

DOMAIN_DESCRIPTIONS = {
    LegalDomain.GOVERNANCE: "Governance and constitutional law",
    LegalDomain.PROPERTY: "Property ownership and usage",
    LegalDomain.FINANCIAL: "Financial rules and obligations",
    LegalDomain.SAFETY: "Safety and risk management",
    LegalDomain.DISCIPLINE: "Disciplinary governance",
    LegalDomain.MEMBERSHIP: "Membership rights and duties",
    LegalDomain.DATA: "Data governance",
    LegalDomain.PRIVACY: "Privacy protection",
    LegalDomain.ACCESS: "Access control",
    LegalDomain.COMMUNICATION: "Communications governance",
    LegalDomain.COMPLIANCE: "Compliance and regulatory law",
    LegalDomain.SECURITY: "Security governance",
    LegalDomain.INFRASTRUCTURE: "Infrastructure law",
    LegalDomain.OPERATIONS: "Operational law",
    LegalDomain.ADMINISTRATION: "Administrative law",
    LegalDomain.JUDICIARY: "Judicial governance",
    LegalDomain.EXECUTION: "Executive governance",
}
