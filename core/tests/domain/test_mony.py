import pytest
from decimal import Decimal

from core.domain.value_objects.money import Money


def test_create_money_from_decimal():
    money = Money(
        Decimal("125.75"),
        "USD",
    )

    assert money.amount == Decimal("125.7500")
    assert money.currency == "USD"


def test_create_money_from_string():
    money = Money(
        "150.25",
        "USD",
    )

    assert money.amount == Decimal("150.2500")


def test_create_money_from_int():
    money = Money(
        250,
        "USD",
    )

    assert money.amount == Decimal("250.0000")


def test_float_is_not_allowed():

    with pytest.raises(TypeError):

        Money(
            15.2,
            "USD",
        )