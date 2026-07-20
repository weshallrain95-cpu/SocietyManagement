"""
==========================================================
SocietyOS Finance Kernel
Treasury Engine
==========================================================

Purpose
-------

Owns movement of liquid treasury assets.

Treasury operations include:

• Bank → Cash
• Cash → Bank
• Bank → Bank
• Cash → Expense

This engine NEVER performs accounting directly.

Its responsibilities are:

    Validate
        ↓
    Resolve Accounts
        ↓
    Verify Funds
        ↓
    Delegate to Posting Engine

The Posting Engine remains the single accounting authority.

==========================================================
"""

from decimal import Decimal

from django.utils import timezone

from django.db.models import Sum
from django.db.models.functions import Coalesce

from society.finance.kernel.posting_engine import post_transaction
from society.finance.kernel.expense_account_factory import get_expense_account

from society.models import (
    BankAccount,
    ChartOfAccount,
    LedgerEntryV2,
)


# ==========================================================
# Treasury Exceptions
# ==========================================================

class TreasuryError(Exception):
    """Base exception for Treasury operations."""
    pass


class TreasuryValidationError(TreasuryError):
    """Raised when Treasury input validation fails."""
    pass


class InsufficientFundsError(TreasuryError):
    """Raised when available funds are insufficient."""
    pass


# ==========================================================
# Validation Helpers
# ==========================================================

def _validate_amount(amount):
    """
    Ensure amount is positive.
    """

    amount = Decimal(amount)

    if amount <= 0:
        raise TreasuryValidationError(
            "Amount must be greater than zero."
        )

    return amount


def _validate_reference(reference_id):
    """
    Ensure every treasury transaction
    has an idempotent reference.
    """

    if not reference_id:
        raise TreasuryValidationError(
            "reference_id is required."
        )

    return reference_id


def _validate_distinct_accounts(source_id, destination_id):
    """
    Prevent meaningless self-transfers.
    """

    if source_id == destination_id:
        raise TreasuryValidationError(
            "Source and destination accounts must differ."
        )

# ==========================================================
# Account Resolution Helpers
# ==========================================================

def _get_bank_chart_account(
    *,
    society,
    bank_account_id,
):
    """
    Resolve a BankAccount into its ChartOfAccount.
    """

    try:
        bank = BankAccount.objects.get(
            id=bank_account_id,
            society=society,
        )
    except BankAccount.DoesNotExist:
        raise TreasuryValidationError(
            "Invalid bank account."
        )

    if not bank.is_active:
        raise TreasuryValidationError(
            "Bank account is inactive."
        )

    if bank.chart_account is None:
        raise TreasuryValidationError(
            "Bank account is not mapped to a Chart of Account."
        )

    return bank.chart_account


def _get_cash_chart_account(
    *,
    society,
):
    """
    Returns the Society Cash in Hand account.

    Current implementation assumes a
    single treasury cash account.
    """

    try:
        return ChartOfAccount.objects.get(
            society=society,
            code="CASH_MAIN",
        )
    except ChartOfAccount.DoesNotExist:
        raise TreasuryValidationError(
            "Cash account (CASH_MAIN) is not configured."
        )

# ==========================================================
# Treasury Balance Helpers
# ==========================================================

def _get_account_balance(account):
    """
    Calculates the current balance of a
    ChartOfAccount directly from LedgerEntryV2.

    Asset accounts naturally calculate as:

        Debits
        -
        Credits
    """

    debits = (
        LedgerEntryV2.objects.filter(
            account=account,
            entry_type="DEBIT",
        )
        .aggregate(
            total=Coalesce(Sum("amount"), Decimal("0.00"))
        )["total"]
    )

    credits = (
        LedgerEntryV2.objects.filter(
            account=account,
            entry_type="CREDIT",
        )
        .aggregate(
            total=Coalesce(Sum("amount"), Decimal("0.00"))
        )["total"]
    )

    return debits - credits


def _validate_available_balance(
    *,
    account,
    amount,
):
    """
    Ensures an asset account has
    sufficient available balance.
    """

    balance = _get_account_balance(account)

    if balance < amount:
        raise InsufficientFundsError(
            f"Available balance is {balance}, "
            f"required {amount}."
        )

    return balance

# ==========================================================
# Posting Helper
# ==========================================================


def _post_treasury_transaction(
    *,
    society,
    transaction_type,
    reference_type,
    reference_id,
    description,
    debit_account,
    credit_account,
    amount,
):
    """
    Centralized Posting Engine wrapper for all
    Treasury transactions.

    Every Treasury operation eventually delegates
    here after validation and account resolution.
    """

    amount = Decimal(amount)

    if debit_account == credit_account:
        raise TreasuryValidationError(
            "Debit and credit accounts must be different."
        )

    return post_transaction(
        society=society,

        transaction_type=transaction_type,

        reference_type=reference_type,

        reference_id=reference_id,

        description=description,

        transaction_date=timezone.now().date(),

        entries=[
            {
                "account": debit_account,
                "type": "DEBIT",
                "amount": amount,
            },
            {
                "account": credit_account,
                "type": "CREDIT",
                "amount": amount,
            },
        ],
    )

# ==========================================================
# Treasury Operations
# ==========================================================

def record_bank_withdrawal(
    *,
    society,
    bank_account_id,
    amount,
    reference_id,
    description="",
):
    """
    Records withdrawal of cash from a bank account.

    Accounting

        Dr Cash in Hand

        Cr Bank
    """

    amount = _validate_amount(amount)
    _validate_reference(reference_id)

    bank_account = _get_bank_chart_account(
        society=society,
        bank_account_id=bank_account_id,
    )

    cash_account = _get_cash_chart_account(
        society=society,
    )

    _validate_available_balance(
        account=bank_account,
        amount=amount,
    )

    return _post_treasury_transaction(
        society=society,

        transaction_type="PAYMENT",

        reference_type="BANK_WITHDRAWAL",

        reference_id=reference_id,

        description=(
            description
            or f"Cash withdrawal from bank account #{bank_account_id}"
        ),

        debit_account=cash_account,

        credit_account=bank_account,

        amount=amount,
    )

def record_cash_deposit(
    *,
    society,
    bank_account_id,
    amount,
    reference_id,
    description="",
):
    """
    Records deposit of cash into a bank account.

    Accounting

        Dr Bank

        Cr Cash in Hand
    """

    amount = _validate_amount(amount)
    _validate_reference(reference_id)

    bank_account = _get_bank_chart_account(
        society=society,
        bank_account_id=bank_account_id,
    )

    cash_account = _get_cash_chart_account(
        society=society,
    )

    _validate_available_balance(
        account=cash_account,
        amount=amount,
    )

    return _post_treasury_transaction(
        society=society,

        transaction_type="PAYMENT",

        reference_type="BANK_DEPOSIT",

        reference_id=reference_id,

        description=(
            description
            or f"Cash deposited into bank account #{bank_account_id}"
        ),

        debit_account=bank_account,

        credit_account=cash_account,

        amount=amount,
    )

def record_bank_transfer(
    *,
    society,
    source_bank_account_id,
    destination_bank_account_id,
    amount,
    reference_id,
    description="",
):
    """
    Records transfer of funds between
    two Society bank accounts.

    Accounting

        Dr Destination Bank

        Cr Source Bank
    """

    amount = _validate_amount(amount)
    _validate_reference(reference_id)


    source_bank = _get_bank_chart_account(
        society=society,
        bank_account_id=source_bank_account_id,
    )

    destination_bank = _get_bank_chart_account(
        society=society,
        bank_account_id=destination_bank_account_id,
    )

    if source_bank == destination_bank:
        raise TreasuryValidationError(
            "Source and destination bank accounts must differ."
        )
        
    _validate_available_balance(
        account=source_bank,
        amount=amount,
    )

    return _post_treasury_transaction(
        society=society,

        transaction_type="PAYMENT",

        reference_type="BANK_TRANSFER",

        reference_id=reference_id,

        description=(
            description
            or (
                f"Transfer from bank #{source_bank_account_id} "
                f"to bank #{destination_bank_account_id}"
            )
        ),

        debit_account=destination_bank,

        credit_account=source_bank,

        amount=amount,
    )

def record_cash_expense(
    *,
    society,
    subtype,
    amount,
    reference_id,
    description="",
):
    """
    Records an immediate expense paid directly
    from Society Cash.

    Accounting

        Dr Expense

        Cr Cash in Hand
    """

    amount = _validate_amount(amount)
    _validate_reference(reference_id)

    expense_account = get_expense_account(
        society=society,
        subtype=subtype,
    )

    cash_account = _get_cash_chart_account(
        society=society,
    )

    _validate_available_balance(
        account=cash_account,
        amount=amount,
    )

    return _post_treasury_transaction(
        society=society,

        transaction_type="PAYMENT",

        reference_type="CASH_EXPENSE",

        reference_id=reference_id,

        description=(
            description
            or f"{subtype} paid using Society Cash"
        ),

        debit_account=expense_account,

        credit_account=cash_account,

        amount=amount,
    )