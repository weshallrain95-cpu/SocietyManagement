from society.domain_services.payables.expense_authorization import (
    ExpenseAuthorizationEvent,
)

REQUIRED_CONTRACTS = {

    ExpenseAuthorizationEvent.ISSUE_PROCUREMENT_DOCUMENT: (
        "governance",
    ),

    ExpenseAuthorizationEvent.CONFIRM_COMPLETION: (
        "governance",
    ),

    ExpenseAuthorizationEvent.RECEIVE_INVOICE: (
        "governance",
    ),

    ExpenseAuthorizationEvent.BOOK_INVOICE: (
        "governance",
    ),

    ExpenseAuthorizationEvent.AUTHORIZE_PAYMENT: (
        "governance",
        "financial_liability",
    ),

    ExpenseAuthorizationEvent.MAKE_PAYMENT: (
        "governance",
        "financial_liability",
    ),

}

from society.domain_services.payables.vendor_bill_factory import (
    create_vendor_bill,
)

from society.domain_services.payables.vendor_payable_factory import (
    create_vendor_payable,
)

from society.domain_services.payables.account_mapping import (
    resolve_vendor_payable_account,
)

from society.finance.kernel.payables_recognition_engine import (
    recognize_vendor_bill,
)


DOWNSTREAM_PIPELINES = {

    ExpenseAuthorizationEvent.BOOK_INVOICE: (

        create_vendor_bill,

        create_vendor_payable,

        resolve_vendor_payable_account,

        recognize_vendor_bill,

    ),

}


EVENT_PERSISTENCE = {

    ExpenseAuthorizationEvent.APPROVE: (

        "approval_reference",

        "approval_date",

    ),

    ExpenseAuthorizationEvent.ISSUE_PROCUREMENT_DOCUMENT: (

        "procurement_type",

        "procurement_document_number",

        "procurement_document_date",

    ),

    ExpenseAuthorizationEvent.CONFIRM_COMPLETION: (

        "completion_date",

        "goods_receipt_reference",

        "goods_receipt_date",

    ),

    ExpenseAuthorizationEvent.AUTHORIZE_PAYMENT: (

        "payment_authorization_reference",

        "payment_authorization_date",

        "payment_authorized_by",

    ),

    ExpenseAuthorizationEvent.CANCEL: (

        "closure_notes",

    ),

}