from enum import Enum


class StripeTransactionStatusResponseStatus(str, Enum):
    CANCELLED = "cancelled"
    COMPLETE = "complete"
    PENDING = "pending"

    def __str__(self) -> str:
        return str(self.value)
