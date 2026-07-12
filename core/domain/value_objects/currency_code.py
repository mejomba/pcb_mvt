from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CurrencyCode:

    value: str