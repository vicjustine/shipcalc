"""Accessorial surcharges applied on top of base freight."""

from __future__ import annotations

from decimal import Decimal

# Published fuel index. Carriers revise this monthly.
FUEL_INDEX: dict[str, Decimal] = {
    "2026-09": Decimal("0.1450"),
    "2026-10": Decimal("0.1525"),
    "2026-11": Decimal("0.1610"),
}

RESIDENTIAL_FLAT = Decimal("4.85")
OVERSIZE_FLAT = Decimal("18.50")
OVERSIZE_GIRTH_CM = Decimal("330")


def fuel_surcharge(base: Decimal, period: str) -> Decimal:
    """Percentage fuel surcharge on the base freight for a billing period.

    Raises:
        KeyError: If the period is not in the published index.
    """
    if period not in FUEL_INDEX:
        raise KeyError(f"no published fuel index for period {period!r}")
    return (base * FUEL_INDEX[period]).quantize(Decimal("0.01"))


def residential_surcharge(is_residential: bool) -> Decimal:
    """Flat fee for delivery to a residential address."""
    return RESIDENTIAL_FLAT if is_residential else Decimal("0.00")


def oversize_surcharge(length_cm: Decimal, girth_cm: Decimal) -> Decimal:
    """Flat fee when length plus girth exceeds the carrier maximum."""
    if length_cm + girth_cm > OVERSIZE_GIRTH_CM:
        return OVERSIZE_FLAT
    return Decimal("0.00")
