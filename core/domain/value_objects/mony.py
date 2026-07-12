from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Union

from core.domain.constants import (
    DEFAULT_MONEY_PRECISION,
    DEFAULT_ROUNDING,
)
from core.domain.utils import to_decimal
from .currency_code import CurrencyCode


MoneyInput = Union[str, int, Decimal]


@dataclass(frozen=True, slots=True)
class Money:

    amount: Decimal

    currency: CurrencyCode

    def __post_init__(self):

        value = to_decimal(self.amount)

        value = value.quantize(
            DEFAULT_MONEY_PRECISION,
            rounding=DEFAULT_ROUNDING,
        )

        object.__setattr__(
            self,
            "amount",
            value,
        )

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented

        return (
                self.currency == other.currency
                and
                self.amount == other.amount
        )

    def _ensure_same_currency(self, other):

        if self.currency != other.currency:
            raise CurrencyMismatchError(
                ...
            )

    def __add__(self, other):

        self._ensure_same_currency(other)

        return Money(
            self.amount + other.amount,
            self.currency,
        )

    def __sub__(self, other):

        self._ensure_same_currency(other)

        return Money(
            self.amount - other.amount,
            self.currency,
        )

    def __bool__(self):

        return self.amount != 0