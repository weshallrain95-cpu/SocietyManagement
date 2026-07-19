"""
==========================================================
SocietyOS
Expense Authorization Engine
==========================================================

Purpose
-------

Orchestrates the complete lifecycle of an
Expense Authorization.

This engine owns workflow.

It does NOT own:

- Accounting
- Procurement
- Payments
- Journals

Those are delegated to their respective engines.

Responsibilities

• Create Expense Authorization
• Advance workflow
• Validate business rules
• Invoke downstream engines
• Publish workflow state
"""
from __future__ import annotations

"""
Engine Contract
---------------

PUBLIC ENTRY POINT

ExpenseAuthorizationEngine.advance_workflow()

This is the ONLY method external callers
should invoke.

------------------------------------------------

THIS ENGINE MAY CALL

• ExpenseAuthorizationStateMachine
• ExpenseAuthorizationRules
• account_mapping.py
• payables_recognition_engine.py
• posting_engine.py
• notification engines
• audit engines

------------------------------------------------

THIS ENGINE MUST NEVER

• Post journals directly

• Resolve Chart Of Accounts directly

• Perform database queries unrelated to
  Expense Authorization

• Implement accounting rules

• Implement procurement rules

• Duplicate workflow intelligence

------------------------------------------------

Single Responsibility

Coordinate business workflow.

Delegate everything else.
"""




from society.domain_services.payables.expense_authorization import (
    ExpenseAuthorizationEvent,
)

from society.finance.kernel.payables_recognition_engine import (
    recognize_vendor_bill,
)

from society.domain_services.payables.account_mapping import (
    resolve_vendor_payable_account,
)

from society.models import (
    ChartOfAccount,
    VendorBill,
    VendorPayable,
)

from society.domain_services.payables.vendor_bill_factory import (
    create_vendor_bill,
)

from society.domain_services.payables.vendor_payable_factory import (
    create_vendor_payable,
)

from society.domain_services.payables.workflow_policy import (
    REQUIRED_CONTRACTS,
    DOWNSTREAM_PIPELINES,
    EVENT_PERSISTENCE,
)

from datetime import date

from society.domain_services.payables.procurement_document_number import (
    generate_procurement_document_number,
)

class ExpenseAuthorizationWorkflowError(Exception):
    """
    Raised when an Expense Authorization
    workflow cannot proceed because a
    business contract has been violated.
    """

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ContractEvaluation:
    """
    Immutable evaluation of a single
    business contract.
    """

    satisfied: bool

    reason: str | None = None

    evidence: dict[str, Any] = field(
        default_factory=dict,
    )

class ExpenseAuthorizationEngine:
    
    """
    Orchestrates the complete Expense
    Authorization workflow.

    The UI never manipulates workflow.

    It submits business events.

    The engine performs orchestration.
    """

    # ======================================================
    # Internal Pipeline
    #
    # Validate Event
    #        ↓
    # Validate Business Rules
    #        ↓
    # Resolve Next Status
    #        ↓
    # Persist Workflow
    #        ↓
    # Invoke Downstream Engine(s)
    #        ↓
    # Record Audit Event
    #        ↓
    # Publish Notifications
    #        ↓
    # Return Updated Authorization
    # ======================================================

    @staticmethod
    def advance_workflow(
        *,
        authorization,
        event: ExpenseAuthorizationEvent,
        payload: dict | None = None,
    ):
        
        if payload is None:
            payload = {}
        
        """
        Advances an Expense Authorization by
        processing a business event.

        This is the ONLY public entry point
        into the Expense Authorization Engine.
        """

        ExpenseAuthorizationEngine._validate_event(
            authorization,
            event,
        )

        ExpenseAuthorizationEngine._validate_business_rules(
            authorization,
            event,
        )

        next_status = (
            ExpenseAuthorizationEngine._resolve_next_status(
                authorization,
                event,
            )
        )

        if (
            event
            == ExpenseAuthorizationEvent.ISSUE_PROCUREMENT_DOCUMENT
        ):

            if payload is None:

                payload = {}

            payload.setdefault(
                "procurement_document_number",
                generate_procurement_document_number(),
            )

            payload.setdefault(
                "procurement_document_date",
                date.today(),
            )

        if (
            event
            == ExpenseAuthorizationEvent.CONFIRM_COMPLETION
        ):

            if payload is None:

                payload = {}

            payload.setdefault(
                "completion_date",
                date.today(),
            )

            payload.setdefault(
                "goods_receipt_date",
                date.today(),
            )

        ExpenseAuthorizationEngine._persist_workflow(
            authorization,
            next_status,
            event,
            payload,
        )

        ExpenseAuthorizationEngine._invoke_downstream_engines(
            authorization,
            event,
            payload,
        )

        ExpenseAuthorizationEngine._record_audit_event(
            authorization,
            event,
        )

        ExpenseAuthorizationEngine._publish_notifications(
            authorization,
            event,
        )

        return authorization
    
    @staticmethod
    def _validate_event(
        authorization,
        event,
    ):
        if event is None:
            raise ExpenseAuthorizationWorkflowError(
                "Workflow event is required."
            )

        if not isinstance(
            event,
            ExpenseAuthorizationEvent,
        ):
            raise ExpenseAuthorizationWorkflowError(
                "Invalid workflow event."
            )


    @staticmethod
    def _validate_business_rules(
        authorization,
        event,
    ):
        """
        Validates whether the requested
        business event is permitted by the
        current Business Contract state.
        """

        contracts = (
            ExpenseAuthorizationEngine
            ._evaluate_business_contracts(
                authorization,
            )
        )

        required_contracts = REQUIRED_CONTRACTS.get(
            event,
            (),
        )

        for contract_name in required_contracts:

            evaluation = contracts[
                contract_name
            ]

            if evaluation.satisfied:
                continue

            raise ExpenseAuthorizationWorkflowError(

                evaluation.reason
                or (
                    f"{contract_name} "
                    "contract not satisfied."
                )

            )


    @staticmethod
    def _evaluate_business_contracts(
        authorization,
    ):
        """
        Evaluates which mandatory business
        contracts have currently been
        satisfied.

        This method performs no workflow
        transitions.

        It performs no persistence.

        It invokes no downstream engines.
        """

        vendor_bill = (
            VendorBill.objects
            .filter(
                expense_authorization=authorization,
            )
            .first()
        )

        vendor_payable = (
            getattr(
                vendor_bill,
                "payable",
                None,
            )
            if vendor_bill
            else None
        )

        execution_completed = getattr(
            authorization,
            "work_completed",
            False,
        )

        settlement_completed = (
            vendor_payable is not None
            and
            vendor_payable.outstanding_amount == 0
        )

        return {

            "governance": ContractEvaluation(

                satisfied=(
                    authorization.status != "DRAFT"
                ),

                reason=(
                    None
                    if authorization.status != "DRAFT"
                    else "Expense Authorization has not been approved."
                ),

                evidence={

                    "authorization_id": authorization.id,

                    "current_status": authorization.status,

                },

            ),

            "financial_liability": ContractEvaluation(

                satisfied=(
                    vendor_bill is not None
                ),

                reason=(
                    None
                    if vendor_bill
                    else "Vendor Invoice has not been booked."
                ),

                evidence={

                    "vendor_bill_id": (
                        vendor_bill.id
                        if vendor_bill
                        else None
                    ),

                    "bill_number": (
                        vendor_bill.bill_number
                        if vendor_bill
                        else None
                    ),

                    "bill_amount": (
                        vendor_bill.amount
                        if vendor_bill
                        else None
                    ),

                },

            ),

            "execution": ContractEvaluation(

                satisfied=execution_completed,

                reason=(
                    None
                    if execution_completed
                    else (
                        "Work completion / Goods Receipt "
                        "has not been recorded."
                    )
                ),

                evidence={

                    "work_completed": execution_completed,

                },

            ),

            "settlement": ContractEvaluation(

                satisfied=settlement_completed,

                reason=(
                    None
                    if settlement_completed
                    else "Vendor payable remains outstanding."
                ),

                evidence={

                    "vendor_payable_id": (
                        vendor_payable.id
                        if vendor_payable
                        else None
                    ),

                    "outstanding_amount": (
                        vendor_payable.outstanding_amount
                        if vendor_payable
                        else None
                    ),

                },

            ),

        }

    @staticmethod
    def _resolve_next_status(
        authorization,
        event,
    ):
        """
        Resolves the next workflow state
        using the canonical Expense
        Authorization State Machine.

        Business validation has already
        been performed before this method
        is invoked.

        This method only determines the
        next status.
        """

        from society.domain_services.payables.expense_authorization import (
            ExpenseAuthorizationStateMachine,
        )

        transitions = (
            ExpenseAuthorizationStateMachine
            .TRANSITIONS
        )

        current_status = authorization.status

        next_status = (
            transitions
            .get(
                current_status,
                {},
            )
            .get(
                event,
            )
        )

        if next_status is None:

            raise ExpenseAuthorizationWorkflowError(
                f"No workflow transition defined for "
                f"status '{current_status}' "
                f"using event '{event}'."
            )

        return next_status
    
    @staticmethod
    def _persist_workflow(
        authorization,
        next_status,
        event,
        payload=None,
    ):
        """
        Persists workflow state together with
        the permanent business truth produced
        by the business event.
        """

        if payload is None:
            payload = {}

        authorization.status = next_status

        update_fields = [
            "status",
        ]

        for field_name in EVENT_PERSISTENCE.get(
            event,
            (),
        ):

            if field_name not in payload:
                continue

            setattr(
                authorization,
                field_name,
                payload[field_name],
            )

            update_fields.append(
                field_name,
            )

        authorization.save(
            update_fields=update_fields,
        )


    @staticmethod
    def _invoke_downstream_engines(
        authorization,
        event,
        payload,
    ):
        """
        Executes the configured downstream
        processing pipeline for the given
        business event.
        """

        pipeline = DOWNSTREAM_PIPELINES.get(
            event,
        )

        if not pipeline:
            return

        context = {

            "authorization": authorization,

            "payload": payload,

        }

        for step in pipeline:

            if step is create_vendor_bill:

                context["vendor_bill"] = step(
                    authorization=context[
                        "authorization"
                    ],
                    payload=context[
                        "payload"
                    ],
                )

            elif step is create_vendor_payable:

                context[
                    "vendor_payable"
                ] = step(
                    vendor_bill=context[
                        "vendor_bill"
                    ],
                )

            elif step is resolve_vendor_payable_account:

                context[
                    "vendor_payable_account"
                ] = step(
                    society=context[
                        "authorization"
                    ].society,
                )

            elif step is recognize_vendor_bill:

                step(
                    vendor_bill=context[
                        "vendor_bill"
                    ],
                    vendor_payable_account=context[
                        "vendor_payable_account"
                    ],
                )


    @staticmethod
    def _record_audit_event(
        authorization,
        event,
    ):
        """
        Audit subsystem not yet commissioned.

        This hook intentionally performs
        no operation until the Audit
        Engine is introduced.
        """

        return


    @staticmethod
    def _publish_notifications(
        authorization,
        event,
    ):
        """
        Notification subsystem not yet
        commissioned.

        This hook intentionally performs
        no operation until the Notification
        Engine is introduced.
        """

        return

