"""
==========================================================
SocietyOS
Expense Authorization Application Service
==========================================================

Purpose
-------

Public application entry point for the
Expense Authorization workflow.

This service is responsible for:

• Creating Expense Authorizations.
• Advancing workflow through business events.
• Providing the single application boundary
  for APIs, UI and future integrations.

Business rules are NOT implemented here.

Workflow orchestration belongs to
ExpenseAuthorizationEngine.
"""

from society.domain_services.payables.expense_authorization_engine import (
    ExpenseAuthorizationEngine,
)

from society.domain_services.spend.spend_resolver import (
    resolve_spend,
)

from society.models import ExpenseAuthorization

from datetime import date

from django.db import transaction


class ExpenseAuthorizationService:
    """
    Public application service for the
    Expense Authorization subsystem.
    """
    
    @staticmethod
    def _generate_procurement_reference():

        """
        Generates the next immutable
        Procurement Reference.

        Format

            PROC-YYYY-000001
        """

        year = date.today().year

        prefix = f"PROC-{year}-"

        latest = (
            ExpenseAuthorization.objects
            .filter(
                procurement_reference__startswith=prefix,
            )
            .order_by(
                "-procurement_reference",
            )
            .first()
        )

        if latest is None:

            sequence = 1

        else:

            sequence = (
                int(
                    latest.procurement_reference.split("-")[-1]
                )
                + 1
            )

        return (
            f"{prefix}{sequence:06d}"
        )

    @staticmethod
    @transaction.atomic
    def create(
        **fields,
    ):
        """
        Creates a new Expense Authorization.
        """

        resolution = resolve_spend(
            operational_domain_code=fields[
                "operational_domain_code"
            ],
            spend_item_code=fields[
                "spend_item_code"
            ],
        )

        fields[
            "operational_domain_code"
        ] = (
            resolution.operational_domain_code
        )

        fields[
            "spend_item_code"
        ] = (
            resolution.spend_item_code
        )
        
        fields[
            "procurement_reference"
        ] = (
            ExpenseAuthorizationService
            ._generate_procurement_reference()
        )

        return ExpenseAuthorization.objects.create(
            **fields,
        )

    @staticmethod
    @transaction.atomic
    def advance(
        *,
        authorization,
        event,
        payload=None,
    ):
        """
        Advances an Expense Authorization
        through one business event.
        """

        if payload is None:
            payload = {}

        return ExpenseAuthorizationEngine.advance_workflow(
            authorization=authorization,
            event=event,
            payload=payload,
        )