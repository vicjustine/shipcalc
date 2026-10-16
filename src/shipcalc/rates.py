"""Rate card lookup and quoting."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from .surcharges import fuel_surcharge, oversize_surcharge, residential_surcharge
from .zones import resolve_zone

MIN_BILLABLE_KG = Decimal("0.5")


@dataclass(frozen=True)
class Quote:
    """A priced shipment."""

    base: Decimal
    fuel: Decimal
    accessorials: Decimal
    total: Decimal
    zone_code: str
    billable_kg: Decimal


class RateCard:
    """Per-kilogram freight rates keyed by zone band and weight break."""

    def __init__(self, rows: list[dict[str, str]]) -> None:
        self._rates: dict[tuple[int, Decimal], Decimal] = {}
        self._breaks: set[Decimal] = set()
        for row in rows:
            band = int(row["band"])
            wbreak = Decimal(row["weight_break_kg"])
            self._rates[(band, wbreak)] = Decimal(row["rate_per_kg"])
            self._breaks.add(wbreak)

    @classmethod
    def from_csv(cls, path: str | Path) -> RateCard:
        """Load a rate card from a CSV file."""
        with open(path, newline="", encoding="utf-8") as fh:
            return cls(list(csv.DictReader(fh)))

    def rate_for(self, band: int, weight_kg: Decimal) -> Decimal:
        """Return the per-kg rate for a band at a given weight.

        Picks the highest weight break at or below the shipment weight.
        """
        eligible = [b for b in sorted(self._breaks) if b <= weight_kg]
        if not eligible:
            raise ValueError(f"weight {weight_kg} below the lowest weight break")
        chosen = eligible[-1]
        try:
            return self._rates[(band, chosen)]
        except KeyError as exc:
            raise ValueError(f"no rate for band {band} at break {chosen}") from exc


def billable_weight(actual_kg: Decimal, length_cm: Decimal, girth_cm: Decimal) -> Decimal:
    """Greater of actual and dimensional weight, floored at the minimum."""
    dim_kg = (length_cm * girth_cm / Decimal("5000")).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP
    )
    return max(actual_kg, dim_kg, MIN_BILLABLE_KG)


def quote(
    card: RateCard,
    origin: str,
    destination: str,
    weight_kg: Decimal,
    period: str,
    *,
    length_cm: Decimal = Decimal("0"),
    girth_cm: Decimal = Decimal("0"),
    is_residential: bool = False,
) -> Quote:
    """Price a single shipment end to end."""
    if weight_kg <= 0:
        raise ValueError("weight must be positive")

    zone = resolve_zone(origin, destination)
    billable = billable_weight(weight_kg, length_cm, girth_cm)
    base = (card.rate_for(zone.band, billable) * billable).quantize(Decimal("0.01"))

    fuel = fuel_surcharge(base, period)
    accessorials = residential_surcharge(is_residential) + oversize_surcharge(
        length_cm, girth_cm
    )

    return Quote(
        base=base,
        fuel=fuel,
        accessorials=accessorials,
        total=(base + fuel + accessorials).quantize(Decimal("0.01")),
        zone_code=zone.code,
        billable_kg=billable,
    )
