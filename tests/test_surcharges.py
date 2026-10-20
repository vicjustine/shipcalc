from decimal import Decimal

import pytest

from shipcalc.surcharges import (
    fuel_surcharge,
    oversize_surcharge,
    residential_surcharge,
)


def test_fuel_surcharge_uses_published_index():
    assert fuel_surcharge(Decimal("100.00"), "2026-11") == Decimal("16.10")


def test_fuel_surcharge_rounds_to_cents():
    assert fuel_surcharge(Decimal("33.33"), "2026-10") == Decimal("5.08")


def test_unknown_period_raises():
    with pytest.raises(KeyError):
        fuel_surcharge(Decimal("100.00"), "2027-01")


def test_residential_only_when_flagged():
    assert residential_surcharge(True) == Decimal("4.85")
    assert residential_surcharge(False) == Decimal("0.00")


def test_oversize_applies_above_threshold():
    assert oversize_surcharge(Decimal("200"), Decimal("200")) == Decimal("18.50")


def test_oversize_skipped_at_threshold():
    assert oversize_surcharge(Decimal("150"), Decimal("180")) == Decimal("0.00")
