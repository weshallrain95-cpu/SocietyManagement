"""
===============================================================================
Society Spend Domain Exceptions
-------------------------------------------------------------------------------

Business exceptions exposed by the Society Spend domain.

These exceptions form the public contract of the Spend Catalog.
Consumers should never depend on raw Python exceptions such as KeyError.
===============================================================================
"""


class SpendDomainError(Exception):
    """
    Base exception for all Spend Domain errors.
    """


class UnknownSpendItem(SpendDomainError):
    """
    Raised when a Spend Item code cannot be found.
    """