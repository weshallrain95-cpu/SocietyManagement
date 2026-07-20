"""
==========================================================
SocietyOS
Expense Authorization Domain
==========================================================

Purpose
-------

Represents the Society's approved intent to incur
an expense before procurement or accounting begins.

This is the first legally significant business event
in the Payables lifecycle.

Everything downstream references this object.

Governance

↓

Procurement

↓

Operations

↓

Finance
"""

from __future__ import annotations

from enum import StrEnum


class ExpenseAuthorizationStatus(StrEnum):
    """
    Canonical lifecycle of an Expense Authorization.

    This represents governance and operational truth.

    Accounting begins only at INVOICE_BOOKED.
    """

    DRAFT = "DRAFT"

    PENDING_APPROVAL = "PENDING_APPROVAL"

    APPROVED = "APPROVED"

    PROCUREMENT_DOCUMENT_ISSUED = (
        "PROCUREMENT_DOCUMENT_ISSUED"
    )

    PROCUREMENT_COMPLETED = (
        "PROCUREMENT_COMPLETED"
    )

    INVOICE_RECEIVED = "INVOICE_RECEIVED"

    INVOICE_BOOKED = "INVOICE_BOOKED"

    PAYMENT_AUTHORIZED = (
        "PAYMENT_AUTHORIZED"
    )

    PAID = "PAID"

    CLOSED = "CLOSED"

    CANCELLED = "CANCELLED"

class ExpenseAuthorizationContract:
    """
    Canonical business contract for an
    Expense Authorization.

    This class documents the permanent
    business truth owned by an Expense
    Authorization.

    It is intentionally NOT a Django model.
    """

    BUSINESS_ATTRIBUTES = (

        "expense_category",

        "purpose",

        "estimated_amount",

        "funding_source",

        "budget_reference",

        "approval_required",

        "approval_authority",

        "approval_reference",

        "approval_date",

        "quotation_required",

        "selected_vendor",

        "expected_completion",

        "is_recurring",

        "recurrence_rule",

        "status",

    )

class ExpenseAuthorizationEvent(StrEnum):
    """
    Canonical business events that move an
    Expense Authorization through its lifecycle.

    Users perform these business events.

    SocietyOS advances workflow automatically.
    """

    CREATE = "CREATE"

    SUBMIT_FOR_APPROVAL = (
        "SUBMIT_FOR_APPROVAL"
    )

    APPROVE = "APPROVE"

    REJECT = "REJECT"

    ISSUE_PROCUREMENT_DOCUMENT = (
        "ISSUE_PROCUREMENT_DOCUMENT"
    )

    CONFIRM_COMPLETION = (
        "CONFIRM_COMPLETION"
    )

    RECEIVE_INVOICE = (
        "RECEIVE_INVOICE"
    )

    BOOK_INVOICE = (
        "BOOK_INVOICE"
    )

    AUTHORIZE_PAYMENT = (
        "AUTHORIZE_PAYMENT"
    )

    MAKE_PAYMENT = (
        "MAKE_PAYMENT"
    )

    CANCEL = "CANCEL"

class ExpenseAuthorizationStateMachine:
    """
    Canonical workflow transitions for an
    Expense Authorization.

    The UI never changes status directly.

    The UI emits business events.

    The backend validates and advances the
    workflow automatically.
    """

    TRANSITIONS = {

        ExpenseAuthorizationStatus.DRAFT: {

            ExpenseAuthorizationEvent.SUBMIT_FOR_APPROVAL:
                ExpenseAuthorizationStatus.PENDING_APPROVAL,

            ExpenseAuthorizationEvent.CANCEL:
                ExpenseAuthorizationStatus.CANCELLED,

        },

        ExpenseAuthorizationStatus.PENDING_APPROVAL: {

            ExpenseAuthorizationEvent.APPROVE:
                ExpenseAuthorizationStatus.APPROVED,

            ExpenseAuthorizationEvent.REJECT:
                ExpenseAuthorizationStatus.DRAFT,

        },

        ExpenseAuthorizationStatus.APPROVED: {

            ExpenseAuthorizationEvent.ISSUE_PROCUREMENT_DOCUMENT:
                ExpenseAuthorizationStatus.PROCUREMENT_DOCUMENT_ISSUED,

            ExpenseAuthorizationEvent.CANCEL:
                ExpenseAuthorizationStatus.CANCELLED,

        },

        ExpenseAuthorizationStatus.PROCUREMENT_DOCUMENT_ISSUED: {

            ExpenseAuthorizationEvent.CONFIRM_COMPLETION:
                ExpenseAuthorizationStatus.PROCUREMENT_COMPLETED,

            ExpenseAuthorizationEvent.RECEIVE_INVOICE:
                ExpenseAuthorizationStatus.INVOICE_RECEIVED,

            ExpenseAuthorizationEvent.BOOK_INVOICE:
                ExpenseAuthorizationStatus.INVOICE_BOOKED,

        },

        ExpenseAuthorizationStatus.PROCUREMENT_COMPLETED: {

            ExpenseAuthorizationEvent.RECEIVE_INVOICE:
                ExpenseAuthorizationStatus.INVOICE_RECEIVED,

        },

        ExpenseAuthorizationStatus.INVOICE_RECEIVED: {

            ExpenseAuthorizationEvent.BOOK_INVOICE:
                ExpenseAuthorizationStatus.INVOICE_BOOKED,

            ExpenseAuthorizationEvent.CONFIRM_COMPLETION:
                ExpenseAuthorizationStatus.PROCUREMENT_COMPLETED,

        },

        ExpenseAuthorizationStatus.INVOICE_BOOKED: {

            ExpenseAuthorizationEvent.BOOK_INVOICE:
                ExpenseAuthorizationStatus.INVOICE_BOOKED,

            ExpenseAuthorizationEvent.AUTHORIZE_PAYMENT:
                ExpenseAuthorizationStatus.PAYMENT_AUTHORIZED,

        },

        ExpenseAuthorizationStatus.PAYMENT_AUTHORIZED: {

            ExpenseAuthorizationEvent.MAKE_PAYMENT:
                ExpenseAuthorizationStatus.PAID,

        },

        ExpenseAuthorizationStatus.PAID: {

            ExpenseAuthorizationEvent.CREATE:
                ExpenseAuthorizationStatus.CLOSED,

        },

    }


class ExpenseAuthorizationRules:
    """
    Canonical business rule engine for
    Expense Authorizations.

    This class determines whether a
    business event is currently valid.

    It also becomes the single place
    where governance rules are enforced.
    """

    pass