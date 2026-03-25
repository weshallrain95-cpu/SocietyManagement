"""
Opening Balance Parser

Purpose:
Convert society Balance Sheet PDFs into structured
opening balances usable by the finance initialization engine.

Flow:

PDF → Extract Text → Detect Account Balances → Return Dict

Returned structure:

{
    "BANK": 1200000,
    "CASH": 5000,
    "FD": 800000,
    "SINK": 200000,
    "ADVANCE": -15000
}

Positive = Debit
Negative = Credit
"""

import re
from decimal import Decimal

import pdfplumber


# ---------------------------------------------------------
# 1. PDF TEXT EXTRACTION
# ---------------------------------------------------------

def extract_text_from_pdf(pdf_path):
    """
    Extract all text from a PDF file.
    """

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


# ---------------------------------------------------------
# 2. BALANCE PATTERN DEFINITIONS
# ---------------------------------------------------------

ACCOUNT_PATTERNS = {

    # Assets

    "BANK": r"Bank\s+Balance\s+([\d,]+\.\d+)",
    "CASH": r"Cash\s+in\s+Hand\s+([\d,]+\.\d+)",
    "FD": r"Fixed\s+Deposit[s]?\s+([\d,]+\.\d+)",

    # Receivables

    "MAINT_RECEIVABLE": r"Maintenance\s+Receivable\s+([\d,]+\.\d+)",
    "INTEREST_RECEIVABLE": r"Interest\s+Receivable\s+([\d,]+\.\d+)",

    # Funds / Liabilities

    "SINK": r"Sinking\s+Fund\s+([\d,]+\.\d+)",
    "REPAIR_FUND": r"Repair\s+Fund\s+([\d,]+\.\d+)",
    "BUILDING_FUND": r"Building\s+Fund\s+([\d,]+\.\d+)",

    "ADVANCE": r"Advance\s+from\s+Members\s+([\d,]+\.\d+)",
    "PAYABLE": r"Maintenance\s+Payable\s+([\d,]+\.\d+)",

}


# ---------------------------------------------------------
# 3. TEXT PARSING ENGINE
# ---------------------------------------------------------

def parse_balance_sheet_text(text):
    """
    Detects known accounts and extracts balances.

    Returns:
        dict {account_code: Decimal}
    """

    balances = {}

    for account_code, pattern in ACCOUNT_PATTERNS.items():

        match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            continue

        value = match.group(1)

        value = value.replace(",", "")

        balances[account_code] = Decimal(value)

    return balances


# ---------------------------------------------------------
# 4. MAIN ENTRY FUNCTION
# ---------------------------------------------------------

def parse_opening_balances_from_pdf(pdf_path):
    """
    High-level parser.

    Returns:
        dictionary usable by initialize_finance()
    """

    text = extract_text_from_pdf(pdf_path)

    balances = parse_balance_sheet_text(text)

    return balances


# ---------------------------------------------------------
# 5. DEBUG HELPER
# ---------------------------------------------------------

def preview_pdf_accounts(pdf_path):
    """
    Helper used during onboarding.

    Prints detected balances before posting to ledger.
    """

    balances = parse_opening_balances_from_pdf(pdf_path)

    print("\nDetected Opening Balances\n")

    for account, amount in balances.items():

        print(f"{account:25} {amount}")

    print("\nTotal accounts detected:", len(balances))

    return balances
    