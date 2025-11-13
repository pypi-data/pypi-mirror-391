from enum import Enum


class NewPasswordRequestAuthnType(str, Enum):
    INITIAL_SETUP = "INITIAL_SETUP"
    PIN = "PIN"
    TOKEN = "TOKEN"

    def __str__(self) -> str:
        return str(self.value)
