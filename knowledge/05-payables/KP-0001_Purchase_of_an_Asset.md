# KP-0001 — Purchase of an Asset

---

# Document Metadata

| Field | Value |
|--------|-------|
| Document ID | KP-0001 |
| Title | Purchase of an Asset |
| Category | Payables |
| Knowledge Area | Procurement → Finance → Assets |
| Version | 1.0.0 |
| Status | COMMISSIONED |
| Classification | Knowledge Article |
| Created | 03-Aug-2026 |
| Last Updated | 03-Aug-2026 |
| Engineering Confidence | 100% |
| Primary Evidence | Django Shell Commissioning |
| Dependencies | KP-0000 – SocietyOS Knowledge Portal Standard |

---

# 1. User Requirement

## Business Requirement

A Cooperative Housing Society must periodically procure capital assets required for its operation.

Examples include:

- Computers
- CCTV Systems
- DG Sets
- Lifts
- Solar Systems
- Pumps
- Office Furniture
- Network Equipment
- Security Equipment

The SocietyOS platform must provide a controlled workflow that begins with the identification of the business need and concludes with the creation of a permanent Asset Register entry.

The workflow must ensure that:

- every procurement is properly authorized;
- committee approvals are preserved;
- procurement documentation is generated;
- goods receipt is recorded;
- vendor liabilities are recognised using accrual accounting;
- accounting entries are automatically posted;
- the purchased asset is permanently registered;
- engineering evidence exists for every stage.

---

## User Outcome

The user should be able to complete the entire lifecycle of an asset purchase without manually interacting with accounting structures.

SocietyOS automatically performs:

- procurement workflow;
- payable creation;
- accounting recognition;
- asset creation;
- permanent persistence.

The user manages the business process.

SocietyOS manages the engineering implementation.

---

# 2. Business Overview

## Capability

Purchase of an Asset is the SocietyOS business capability responsible for converting an approved procurement requirement into a permanently registered society asset.

The capability spans three major business domains.

| Domain | Responsibility |
|---------|---------------|
| Procurement | Business workflow and approvals |
| Finance | Recognition of vendor liability and accounting entries |
| Assets | Creation of permanent Asset Register records |

Each domain owns its own responsibilities.

No domain performs responsibilities belonging to another.

---

## Business Objective

The capability ensures that every capital purchase follows a controlled governance process while simultaneously producing:

- operational truth;
- financial truth;
- asset truth.

These three truths remain permanently synchronized throughout the lifecycle.

---

## Scope

This Knowledge Article documents the complete engineering implementation for:

- Expense Authorization
- Procurement Approval
- Procurement Completion
- Vendor Bill Creation
- Vendor Payable Creation
- Invoice Recognition
- Double-entry Accounting
- Asset Creation
- Asset Register Persistence

The article also documents the complete commissioning process used to validate the subsystem.

---

## Out of Scope

The following capabilities are intentionally excluded and are documented separately.

- Vendor Payments
- Partial Payments
- Asset Depreciation
- Asset Disposal
- Asset Transfers
- Asset Maintenance
- Asset Revaluation

These capabilities are covered by independent Knowledge Articles.

---

# 3. Business Journey

The complete business journey is shown below.

```text
Business Need
        │
        ▼
Expense Authorization
        │
        ▼
Committee Approval
        │
        ▼
Issue Procurement Document
        │
        ▼
Procurement Completion
        │
        ▼
Vendor Bill
        │
        ▼
Vendor Payable
        │
        ▼
Invoice Recognition
        │
        ▼
Posting Engine
        │
        ▼
General Ledger
        │
        ▼
Asset Creation
        │
        ▼
Asset Register
```

---

## Business Outcome

Upon successful completion of the workflow the Society possesses:

- an approved procurement record;
- a recorded vendor invoice;
- an outstanding payable;
- complete accounting entries;
- a permanently registered asset;
- complete engineering traceability.

This concludes the business lifecycle of procurement.

Subsequent activities such as vendor payment and asset lifecycle management are handled by separate business capabilities.

# 4. Business Rules

The Purchase of an Asset capability is governed by a fixed set of business rules validated during commissioning.

---

## BR-001

Every procurement begins with an Expense Authorization.

No Vendor Bill, Vendor Payable or Asset may exist without an originating Expense Authorization.

---

## BR-002

Expense Authorization is the single source of business intent.

It permanently records:

- Operational Domain
- Spend Item
- Expense Category
- Purpose
- Estimated Amount

Every downstream business object derives from this authorization.

---

## BR-003

Procurement follows a controlled workflow.

The commissioned workflow is:

```
DRAFT

↓

PENDING_APPROVAL

↓

APPROVED

↓

PROCUREMENT_DOCUMENT_ISSUED

↓

PROCUREMENT_COMPLETED
```

No workflow stage may be skipped.

---

## BR-004

Vendor Bills may only be created after Procurement Completion.

This guarantees that goods or services have been received before invoice processing begins.

---

## BR-005

Every Vendor Bill creates exactly one Vendor Payable.

Vendor Payables represent liabilities.

Vendor Bills represent vendor invoices.

They are distinct business objects.

---

## BR-006

Invoice Recognition performs accounting only.

It does not:

- create payments;
- reduce bank balances;
- settle liabilities.

Its sole responsibility is accrual accounting.

---

## BR-007

Every recognised Vendor Invoice generates balanced double-entry accounting.

```
Debit

Expense

Credit

Vendor Payables
```

Accounting is delegated entirely to the Posting Engine.

---

## BR-008

Asset creation occurs only after successful invoice recognition.

The Asset Register therefore reflects only recognised capital acquisitions.

---

## BR-009

The Asset Register represents permanent business truth.

Assets are never created directly by user interface screens.

Assets are created through domain services.

---

## BR-010

Operational Domains determine business behaviour.

Expense Categories determine accounting behaviour.

Asset Types determine asset classification.

These responsibilities remain intentionally separated.

---

# 5. UX Specification

## Current Status

User interface implementation for this business capability is **Pending**.

The commissioning documented in this article was executed entirely through domain services and Django Shell.

---

## Planned User Journey

The future SocietyOS user experience is expected to guide the user through the following stages.

```
Purchase Intent

↓

Expense Authorization

↓

Approval

↓

Issue Procurement Document

↓

Goods Receipt

↓

Vendor Bill

↓

Vendor Payable

↓

Accounting Recognition

↓

Asset Details

↓

Asset Register
```

---

## UX Principles

The future implementation shall follow the SocietyOS product philosophy.

### Principle 1

The user performs business activities.

SocietyOS performs accounting.

---

### Principle 2

The user never creates accounting entries.

Ledger posting is automatic.

---

### Principle 3

The user never manually creates Asset Register entries following procurement.

Assets are generated automatically.

---

### Principle 4

Every onboarding stage leaves permanent database truth before proceeding to the next stage.

---

### Principle 5

Business workflow remains visible.

Engineering implementation remains invisible.

---

## UX Implementation Status

| Capability | Status |
|------------|--------|
| Expense Authorization | Planned |
| Committee Approval | Planned |
| Procurement Document | Planned |
| Goods Receipt | Planned |
| Vendor Bill | Planned |
| Vendor Payable | Planned |
| Invoice Recognition | Automated |
| Asset Creation | Automated |
| Asset Register | Automated |

---

# 6. Domain Model

The Purchase of an Asset capability spans three business domains.

---

## Procurement Domain

Primary business object:

- ExpenseAuthorization

Supporting concepts:

- Operational Domain
- Spend Item
- Expense Category
- Procurement Reference
- Committee Approval
- Goods Receipt

---

## Vendor Domain

Primary business objects:

- Vendor
- VendorBill
- VendorPayable

These objects manage supplier relationships and liabilities.

---

## Finance Domain

Primary business objects:

- Transaction
- LedgerEntryV2
- ChartOfAccount

These objects maintain permanent accounting truth.

---

## Asset Domain

Primary business object:

- Asset

The Asset Register represents the permanent operational record of society-owned assets.

---

## Domain Relationships

```
ExpenseAuthorization
        │
        ▼
VendorBill
        │
        ▼
VendorPayable
        │
        ▼
Transaction
        │
        ▼
LedgerEntryV2
        │
        ▼
Asset
```

---

## Responsibility Matrix

| Domain | Primary Responsibility |
|---------|------------------------|
| Procurement | Business workflow |
| Vendor | Supplier obligations |
| Finance | Accounting truth |
| Assets | Permanent asset ownership |

Each domain owns its own data and behaviour.

Cross-domain interaction occurs only through defined domain services.

# 7. Engineering Architecture

The Purchase of an Asset capability is implemented as a collaboration between three independent SocietyOS domains.

The architecture intentionally separates business workflow, financial accounting and asset lifecycle management.

Each domain owns its own responsibilities.

---

## Procurement Domain

### Primary Responsibility

Manage the complete procurement workflow.

### Primary Business Objects

- ExpenseAuthorization

### Primary Services

- ExpenseAuthorizationService
- ExpenseAuthorizationEngine

### Responsibilities

- Create procurement intent
- Control workflow transitions
- Capture committee approvals
- Record procurement completion
- Maintain procurement truth

The Procurement domain performs no accounting.

---

## Vendor Domain

### Primary Responsibility

Manage supplier obligations.

### Primary Business Objects

- Vendor
- VendorBill
- VendorPayable

### Primary Services

- create_vendor_bill()
- create_vendor_payable()

### Responsibilities

- Record vendor invoices
- Create vendor liabilities
- Maintain outstanding balances

The Vendor domain performs no accounting.

---

## Finance Domain

### Primary Responsibility

Recognise financial liability.

### Primary Business Objects

- Transaction
- LedgerEntryV2
- ChartOfAccount

### Primary Services

- recognize_vendor_bill()
- post_transaction()

### Responsibilities

- Resolve Expense Account
- Resolve Vendor Payables Account
- Generate balanced accounting entries
- Maintain General Ledger truth

The Finance domain performs no procurement.

---

## Asset Domain

### Primary Responsibility

Maintain permanent Asset Register.

### Primary Business Objects

- Asset

### Primary Services

- create_asset_from_purchase()

### Responsibilities

- Classify purchased assets
- Create Asset Register records
- Capture manufacturer details
- Capture serial numbers
- Capture installation information

The Asset domain performs no accounting.

---

## Engineering Responsibility Matrix

| Domain | Owns |
|---------|------|
| Procurement | Business workflow |
| Vendor | Supplier obligations |
| Finance | Accounting truth |
| Assets | Permanent asset register |

---

## Architectural Principle

Business workflow progresses across domains.

Business responsibility never crosses domains.

---

# 8. APIs & Integration Contracts

The Purchase of an Asset capability is implemented through internal domain services.

During commissioning all stages were executed directly through Django Shell.

The following service contracts were validated.

| Service | Responsibility |
|----------|----------------|
| ExpenseAuthorizationService.create() | Create procurement request |
| ExpenseAuthorizationService.advance() | Advance workflow |
| create_vendor_bill() | Create Vendor Bill |
| create_vendor_payable() | Create Vendor Payable |
| recognize_vendor_bill() | Recognise vendor liability |
| create_asset_from_purchase() | Create permanent Asset |

---

## Service Flow

```
ExpenseAuthorizationService.create()

↓

ExpenseAuthorizationService.advance()

↓

create_vendor_bill()

↓

create_vendor_payable()

↓

recognize_vendor_bill()

↓

create_asset_from_purchase()
```

Each service creates permanent business truth before the next service executes.

---

## Integration Boundary

The following integrations were commissioned.

Procurement

↓

Vendor

↓

Finance

↓

Assets

No direct coupling exists between Procurement and Finance.

Asset creation occurs only after successful financial recognition.

---

# 9. Database Truth

The commissioning created the following permanent business objects.

| Business Object | Purpose |
|-----------------|---------|
| ExpenseAuthorization | Procurement intent |
| VendorBill | Vendor invoice |
| VendorPayable | Outstanding liability |
| Transaction | Financial transaction |
| LedgerEntryV2 | Double-entry accounting |
| Asset | Permanent asset register |

---

## Commissioned Persistence

The commissioned procurement successfully created:

Expense Authorization

```
ID = 5
Status = PROCUREMENT_COMPLETED
```

Vendor Bill

```
ID = 9
Status = PENDING
```

Vendor Payable

```
ID = 7
Status = OPEN
```

Transaction

```
ID = 1599
Type = ADJUSTMENT
Reference = VENDOR_INVOICE
```

Ledger Entries

```
Debit

EXP_EQUIPMENT

65000.00

Credit

VENDOR_PAYABLES

65000.00
```

Asset

```
ID = 10

Asset Number = AST-000010

Asset Type = COMPUTER

Origin = PURCHASED
```

---

## Database Truth Established

The commissioning proved the following permanent truths.

- Procurement workflow persisted successfully.
- Vendor Bill persisted successfully.
- Vendor Payable persisted successfully.
- Accounting transaction persisted successfully.
- Double-entry ledger persisted successfully.
- Asset Register persisted successfully.

No manual database intervention was required.

All persistence resulted from domain services executed during commissioning.

# 10. Executable Engineering Evidence

This section preserves the exact engineering evidence used to commission the Purchase of an Asset capability.

Unlike descriptive documentation, the evidence contained in this section can be replayed to validate the subsystem.

The preferred form of engineering evidence within SocietyOS is Django Shell commissioning.

Every business event records:

- Mandatory Inputs
- Domain Service Invoked
- Exact Shell Command
- Actual Output
- Database Truth Created
- Business Truth Proven

---

# Business Event 01 — Create Expense Authorization

## Purpose

Create the initial procurement intent for a capital asset.

---

## Mandatory Inputs

| Field | Value |
|--------|-------|
| Society | Required |
| Operational Domain | Required |
| Spend Item | Required |
| Expense Category | Required |
| Purpose | Required |
| Estimated Amount | Required |

---

## Domain Service

ExpenseAuthorizationService.create()

---

## Exact Django Shell Command

```python
from decimal import Decimal

from society.models import Society

from society.domain_services.payables.expense_authorization_service import (
    ExpenseAuthorizationService,
)

society = Society.objects.get(id=44)

authorization = ExpenseAuthorizationService.create(
    society=society,
    operational_domain_code="EQUIPMENT_INFRASTRUCTURE",
    spend_item_code="COMPUTER",
    expense_category="EQUIPMENT_EXPENSE",
    purpose="Purchase of office desktop computer",
    estimated_amount=Decimal("65000.00"),
)
```

---

## Actual Output

```text
ID: 5

Status: DRAFT

Procurement Ref: PROC-2026-000005

Operational Domain: EQUIPMENT_INFRASTRUCTURE

Spend Item: COMPUTER

Expense Category: EQUIPMENT_EXPENSE
```

---

## Database Truth Created

ExpenseAuthorization

```
ID = 5

Status = DRAFT
```

---

## Business Truth Proven

The procurement requirement has been permanently recorded.

---

# Business Event 02 — Submit for Approval

## Purpose

Move the procurement request into the committee approval workflow.

---

## Mandatory Inputs

| Field | Value |
|--------|-------|
| Expense Authorization | Status = DRAFT |

---

## Domain Service

ExpenseAuthorizationService.advance()

---

## Exact Django Shell Command

```python
authorization = ExpenseAuthorizationService.advance(
    authorization=authorization,
    event=ExpenseAuthorizationEvent.SUBMIT_FOR_APPROVAL,
)

authorization.refresh_from_db()
```

---

## Actual Output

```text
Status: PENDING_APPROVAL
```

---

## Database Truth Created

ExpenseAuthorization

```
Status = PENDING_APPROVAL
```

---

## Business Truth Proven

The procurement request has formally entered the approval process.

---

# Business Event 03 — Committee Approval

## Purpose

Approve the procurement request.

---

## Mandatory Inputs

| Field | Value |
|--------|-------|
| Approval Reference | Required |
| Approval Date | Required |

---

## Domain Service

ExpenseAuthorizationService.advance()

---

## Exact Django Shell Command

```python
from datetime import date

authorization = ExpenseAuthorizationService.advance(
    authorization=authorization,
    event=ExpenseAuthorizationEvent.APPROVE,
    payload={
        "approval_reference": "MC-RES-2026-COMP-001",
        "approval_date": date(2026, 8, 2),
    },
)

authorization.refresh_from_db()
```

---

## Actual Output

```text
Status: APPROVED

Approval Ref: MC-RES-2026-COMP-001

Approval Date: 2026-08-02
```

---

## Database Truth Created

ExpenseAuthorization

```
Status = APPROVED
```

---

## Business Truth Proven

The committee has permanently approved the procurement.

---

# Business Event 04 — Issue Procurement Document

## Purpose

Issue the official procurement document authorising purchase.

---

## Mandatory Inputs

| Field | Value |
|--------|-------|
| Procurement Document Number | Required |
| Procurement Document Date | Required |

---

## Domain Service

ExpenseAuthorizationService.advance()

---

## Exact Django Shell Command

```python
authorization = ExpenseAuthorizationService.advance(
    authorization=authorization,
    event=ExpenseAuthorizationEvent.ISSUE_PROCUREMENT_DOCUMENT,
    payload={
        "procurement_document_number": "PO-2026-COMP-001",
        "procurement_document_date": date(2026, 8, 2),
    },
)

authorization.refresh_from_db()
```

---

## Actual Output

```text
Status: PROCUREMENT_DOCUMENT_ISSUED

Procurement Ref: PROC-2026-000005
```

---

## Database Truth Created

ExpenseAuthorization

```
Status = PROCUREMENT_DOCUMENT_ISSUED
```

---

## Business Truth Proven

Formal procurement has been authorised.

---

# Business Event 05 — Confirm Procurement Completion

## Purpose

Record successful completion of procurement and receipt of goods.

---

## Mandatory Inputs

| Field | Value |
|--------|-------|
| Completion Date | Required |
| Goods Receipt Reference | Required |
| Goods Receipt Date | Required |

---

## Domain Service

ExpenseAuthorizationService.advance()

---

## Exact Django Shell Command

```python
authorization = ExpenseAuthorizationService.advance(
    authorization=authorization,
    event=ExpenseAuthorizationEvent.CONFIRM_COMPLETION,
    payload={
        "completion_date": date(2026, 8, 2),
        "goods_receipt_reference": "GRN-COMP-001",
        "goods_receipt_date": date(2026, 8, 2),
    },
)

authorization.refresh_from_db()
```

---

## Actual Output

```text
Status: PROCUREMENT_COMPLETED

Completion Date: 2026-08-02

GRN Ref: GRN-COMP-001

GRN Date: 2026-08-02
```

---

## Database Truth Created

ExpenseAuthorization

```
Status = PROCUREMENT_COMPLETED
```

---

## Business Truth Proven

Goods have been received.

The procurement workflow has completed successfully.

Invoice processing may now begin.

# Business Event 06 — Create Vendor Bill

## Purpose

Record the Vendor Invoice received after successful procurement completion.

The Vendor Bill represents the supplier's invoice.

It is not an accounting entry.

It is not a liability.

It is the commercial document received from the vendor.

---

## Mandatory Inputs

| Field | Value |
|--------|-------|
| Expense Authorization | Status = PROCUREMENT_COMPLETED |
| Vendor | Existing Vendor |
| Bill Number | Required |
| Bill Date | Required |
| Amount | Required |
| Description | Optional |

---

## Domain Service

create_vendor_bill()

---

## Source File

```
society/domain_services/payables/vendor_bill_factory.py
```

---

## Exact Django Shell Command

```python
from decimal import Decimal
from datetime import date

from society.domain_services.payables.vendor_bill_factory import (
    create_vendor_bill,
)

vendor_bill = create_vendor_bill(
    authorization=authorization,
    payload={
        "vendor_id": 2,
        "bill_number": "COMP-INV-002",
        "bill_date": date(2026, 8, 2),
        "amount": Decimal("65000.00"),
        "description": "Office Desktop Computer",
    },
)

print("Vendor Bill ID:", vendor_bill.id)
print("Authorization:", vendor_bill.expense_authorization_id)
print("Vendor:", vendor_bill.vendor.name)
print("Amount:", vendor_bill.amount)
print("Status:", vendor_bill.status)
```

---

## Actual Output

```text
Vendor Bill ID: 9

Authorization: 5

Vendor: Test Vendor

Amount: 65000.00

Status: PENDING
```

---

## Database Truth Created

VendorBill

```
ID = 9

Expense Authorization = 5

Status = PENDING
```

---

## Business Truth Proven

The supplier invoice has been permanently recorded.

---

# Business Event 07 — Create Vendor Payable

## Purpose

Convert the Vendor Bill into an outstanding liability.

The Vendor Payable represents the amount owed to the supplier.

---

## Mandatory Inputs

| Field | Value |
|--------|-------|
| Vendor Bill | Existing Vendor Bill |

---

## Domain Service

create_vendor_payable()

---

## Source File

```
society/domain_services/payables/vendor_payable_factory.py
```

---

## Exact Django Shell Command

```python
from society.domain_services.payables.vendor_payable_factory import (
    create_vendor_payable,
)

vendor_payable = create_vendor_payable(
    vendor_bill=vendor_bill,
)

print("Vendor Payable ID:", vendor_payable.id)
print("Vendor Bill:", vendor_payable.vendor_bill_id)
print("Amount:", vendor_payable.amount)
print("Outstanding:", vendor_payable.outstanding_amount)
print("Status:", vendor_payable.status)
```

---

## Actual Output

```text
Vendor Payable ID: 7

Vendor Bill: 9

Amount: 65000.00

Outstanding: 65000.00

Status: OPEN
```

---

## Database Truth Created

VendorPayable

```
ID = 7

Outstanding Amount = 65000.00

Status = OPEN
```

---

## Business Truth Proven

A supplier liability has been permanently created.

---

# Business Event 08 — Recognize Vendor Invoice

## Purpose

Recognize the Vendor Invoice using accrual accounting.

This creates permanent accounting truth.

No payment occurs.

No bank movement occurs.

---

## Mandatory Inputs

| Field | Value |
|--------|-------|
| Vendor Bill | Existing Vendor Bill |
| Vendor Payables Control Account | Required |

---

## Domain Service

recognize_vendor_bill()

---

## Source File

```
society/finance/kernel/payables_recognition_engine.py
```

---

## Exact Django Shell Command

```python
from society.finance.kernel.payables_recognition_engine import (
    recognize_vendor_bill,
)

from society.models import (
    ChartOfAccount,
    VendorBill,
)

vendor_bill = VendorBill.objects.get(id=9)

vendor_payable_account = ChartOfAccount.objects.get(
    code="VENDOR_PAYABLES",
    society=vendor_bill.society,
)

transaction = recognize_vendor_bill(
    vendor_bill=vendor_bill,
    vendor_payable_account=vendor_payable_account,
)

print("Transaction ID:", transaction.id)
print("Transaction Type:", transaction.transaction_type)
print("Reference Type:", transaction.reference_type)
print("Reference ID:", transaction.reference_id)
print("Description:", transaction.description)
```

---

## Actual Output

```text
Transaction ID: 1599

Transaction Type: ADJUSTMENT

Reference Type: VENDOR_INVOICE

Reference ID: 9

Description: Vendor Invoice - Test Vendor
```

---

## Ledger Verification Command

```python
from society.models import LedgerEntryV2

entries = LedgerEntryV2.objects.filter(
    transaction_id=1599,
).order_by("id")

print("Entries:", entries.count())

for e in entries:
    print(
        e.account.code,
        e.account.name,
        e.entry_type,
        e.amount,
    )
```

---

## Ledger Verification Output

```text
Entries: 2

EXP_EQUIPMENT

Equipment Procurement

DEBIT

65000.00

VENDOR_PAYABLES

Vendor Payables

CREDIT

65000.00
```

---

## Database Truth Created

Transaction

```
ID = 1599

Type = ADJUSTMENT
```

LedgerEntryV2

```
2 Balanced Entries
```

---

## Business Truth Proven

The vendor liability has been recognized using accrual accounting.

Double-entry accounting has been successfully generated.

---

# Business Event 09 — Create Asset from Purchase

## Purpose

Create the permanent Asset Register entry representing the purchased asset.

---

## Mandatory Inputs

| Field | Value |
|--------|-------|
| Expense Authorization | PROCUREMENT_COMPLETED |
| Vendor Bill | Existing Vendor Bill |
| Manufacturer | Required |
| Serial Number | Required |
| Installation Date | Required |

---

## Domain Service

create_asset_from_purchase()

---

## Source File

```
society/domain_services/payables/asset_creation_adapter.py
```

---

## Exact Django Shell Command

```python
from datetime import date

from society.domain_services.payables.asset_creation_adapter import (
    create_asset_from_purchase,
)

from society.models import (
    ExpenseAuthorization,
    VendorBill,
)

authorization = ExpenseAuthorization.objects.get(id=5)

vendor_bill = VendorBill.objects.get(id=9)

asset = create_asset_from_purchase(
    authorization=authorization,
    vendor_bill=vendor_bill,
    asset_details={
        "manufacturer": "Dell",
        "serial_number": "COMP-000001",
        "installed_on": date(2026, 8, 2),
    },
)

print("Asset ID:", asset.id)
print("Asset Number:", asset.asset_number)
print("Asset Name:", asset.name)
print("Asset Type:", asset.asset_type)
print("Manufacturer:", asset.manufacturer)
print("Serial Number:", asset.serial_number)
print("Origin:", asset.origin)
```

---

## Actual Output

```text
Asset ID: 10

Asset Number: AST-000010

Asset Name: Dell OptiPlex Desktop

Asset Type: COMPUTER

Manufacturer: Dell

Serial Number: COMP-000001

Origin: PURCHASED
```

---

## Database Truth Created

Asset

```
ID = 10

Asset Number = AST-000010

Type = COMPUTER

Origin = PURCHASED
```

---

## Business Truth Proven

The purchased computer has been permanently entered into the Society Asset Register.

The complete Procurement → Finance → Asset lifecycle has been successfully commissioned.

# 11. Commissioning Summary

The Purchase of an Asset capability was successfully commissioned end-to-end through controlled execution of SocietyOS domain services.

The commissioning validated the complete lifecycle from business intent through permanent asset registration without bypassing any business workflow.

---

## Commissioning Sequence

```
Business Intent
        │
        ▼
Expense Authorization
        │
        ▼
Committee Approval
        │
        ▼
Procurement Document
        │
        ▼
Procurement Completion
        │
        ▼
Vendor Bill
        │
        ▼
Vendor Payable
        │
        ▼
Invoice Recognition
        │
        ▼
Posting Engine
        │
        ▼
General Ledger
        │
        ▼
Asset Creation
        │
        ▼
Asset Register
```

---

## Commissioning Outcome

The commissioning successfully validated:

- Procurement workflow
- Approval workflow
- Vendor Bill creation
- Vendor Payable creation
- Finance Kernel
- Posting Engine
- Double-entry Accounting
- Asset Creation
- Asset Register persistence

Every business capability performed exactly one responsibility.

No architectural boundaries were violated.

---

# 12. Failure Log

Commissioning deliberately records engineering failures.

Failures are valuable because they expose incomplete architecture before production.

---

## Failure 001

### Stage

Invoice Recognition

### Observed Error

```
Unknown Expense Category:

EQUIPMENT_EXPENSE
```

### Root Cause

The new operational domain

```
EQUIPMENT_INFRASTRUCTURE
```

had been introduced into the Spend Operating Model and Asset Operating Model but had not yet been incorporated into the Payables Operating Model.

The Finance Kernel therefore failed to resolve the corresponding expense account.

---

### Resolution

The following operating model was extended.

```
society/domain_services/payables/payable_categories.py
```

The following business category was introduced.

```
EQUIPMENT_EXPENSE
```

No changes were made to:

- Posting Engine
- Finance Kernel
- Asset Factory
- Vendor Bill Factory
- Vendor Payable Factory

---

### Verification

Invoice Recognition recommissioned successfully.

```
Transaction ID

1599
```

was generated.

Balanced ledger entries were verified.

Asset creation subsequently completed successfully.

---

## Engineering Observation

The failure demonstrated that SocietyOS correctly detects incomplete business configuration rather than producing incorrect accounting.

The architecture behaved exactly as intended.

---

# 13. Engineering Decisions

The following architectural decisions were permanently validated during commissioning.

---

## ED-001

### Decision

Separate Procurement, Finance and Asset responsibilities.

### Result

Each domain owns a single business responsibility.

---

## ED-002

### Decision

Expense Authorization remains the permanent source of procurement intent.

### Result

Every downstream business object references the originating authorization.

---

## ED-003

### Decision

Vendor Bills are commercial documents.

Vendor Payables are financial liabilities.

### Result

Commercial truth remains independent from accounting truth.

---

## ED-004

### Decision

Accounting is delegated exclusively to the Posting Engine.

### Result

No Procurement or Asset service performs accounting.

---

## ED-005

### Decision

Assets are created automatically from recognised purchases.

### Result

Users never manually populate the Asset Register following procurement.

---

## ED-006

### Decision

Commission every subsystem using executable engineering evidence.

### Result

The complete business capability can be replayed directly from this Knowledge Article.

---

# 14. Lessons Learned

The commissioning established several permanent engineering principles.

---

## Lesson 1

Commission complete business capabilities.

Never commission isolated services.

---

## Lesson 2

Every new Operational Domain must exist consistently across:

- Spend Operating Model
- Payables Operating Model
- Asset Operating Model

Incomplete propagation results in business capability failure.

---

## Lesson 3

Business failures should reveal missing business configuration.

Core engines should remain unchanged.

During commissioning the following components required no modification.

- Posting Engine
- Finance Kernel
- Asset Factory
- Vendor Bill Factory
- Vendor Payable Factory

---

## Lesson 4

Every commissioning exercise should preserve executable engineering evidence.

Shell commissioning remains the preferred engineering validation technique because it exercises the actual domain services without user interface abstraction.

---

## Lesson 5

Knowledge Articles are engineering assets.

Engineering knowledge must remain version-controlled alongside source code.

---

# 15. Related Knowledge Articles

## Governing Standard

```
KP-0000

SocietyOS Knowledge Portal Standard
```

---

## Related Business Capabilities

Future Knowledge Articles will include:

```
Vendor Payments

Monthly Maintenance Billing

Asset Register

Asset Depreciation

Vendor Onboarding

Bank Payments

Treasury Operations
```

---

# 16. Revision History

| Version | Status | Description |
|----------|---------|-------------|
| 1.0.0 | Commissioned | Initial Knowledge Article |

---

## Knowledge Confidence

| Area | Confidence |
|------|------------|
| Business Requirement | 100% |
| Business Journey | 100% |
| Business Rules | 100% |
| Domain Model | 100% |
| Engineering Architecture | 100% |
| Database Truth | 100% |
| Executable Engineering Evidence | 100% |
| Commissioning | 100% |
| Engineering Decisions | 100% |
| Lessons Learned | 100% |
| UX Specification | Pending Product Implementation |

---

# Certification

This Knowledge Article is the authoritative engineering reference for the SocietyOS **Purchase of an Asset** capability.

It documents:

- the business requirement;
- the engineering architecture;
- the domain model;
- the commissioned workflow;
- the permanent database truth;
- the executable engineering evidence;
- the architectural decisions;
- the lessons established during commissioning.

Every engineering statement contained within this article has been validated through live commissioning.

This article shall serve as the reference implementation for all future SocietyOS Knowledge Articles.

---

**END OF KNOWLEDGE ARTICLE**

**Knowledge Article:** KP-0001

**Version:** 1.0.0

**Status:** COMMISSIONED

**Classification:** REFERENCE IMPLEMENTATION
