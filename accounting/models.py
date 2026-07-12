from django.db import models
from core.models import AbstractCommModel


class Currency(AbstractCommModel):

    name = models.CharField(
        max_length=64,
        verbose_name="Currency Name",
    )

    code = models.CharField(
        max_length=3,
        unique=True,
        db_index=True,
        verbose_name="ISO 4217 Code",
    )

    symbol = models.CharField(
        max_length=8,
        blank=True,
        default="",
        verbose_name="Currency Symbol",
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ("code",)

        indexes = [
            models.Index(fields=("code",)),
            models.Index(fields=("is_active",)),
        ]

    def __str__(self):
        return f"{self.code}"


class CurrencyRate(AbstractCommModel):

    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="rates",
    )

    rate = models.DecimalField(
        max_digits=25,
        decimal_places=4,
    )

    class Meta:

        ordering = (
            "-created_at",
        )

        indexes = [
            models.Index(
                fields=(
                    "currency",
                    "-created_at",
                )
            )
        ]