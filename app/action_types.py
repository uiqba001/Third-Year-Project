from enum import Enum


class BudgetActions(Enum):
    CREATED_BUDGET = "CREATED BUDGET"
    EDITED_BUDGET = "EDITED BUDGET"
    DELETE_BUDGET = "DELETED BUDGET"
    SPENT_MONEY = "MONEY SPENT"
    REMOVE_MONEY = "REMOVED MONEY"


class SavingsActions(Enum):
    CREATED_SAVINGS_POT = "CREATED SAVINGS POT"
    EDITED_SAVINGS_POT = "EDITED SAVINGS POT"
    DELETED_SAVINGS_POT = "DELETED SAVINGS POT"
    SAVED_MONEY = "MONEY SAVED"
    REMOVE_SAVED_MONEY = "SAVED MONEY REMOVED"
