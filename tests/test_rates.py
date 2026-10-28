from decimal import Decimal
from pathlib import Path

import pytest

from shipcalc.rates import RateCard, billable_weight, quote

CARD = Path(__file__).parent.parent / "data" / "rate_card_2026Q4.csv"


@pytest.fixture(scope="module")
def card():
    return RateCard.from_csv(CARD)


def test_rate_card_loads_all_bands(card):
    for band in (1, 2, 3, 4):
        assert card.rate_for(band, Decimal("5.0")) > 0


def test_weight_break_picks_highest_at_or_below(card):
    assert card.rate_for(1, Decimal("9.9")) == Decimal("4.15")
    assert card.rate_for(1, Decimal("10.0")) == Decimal("3.05")


def test_weight_below_lowest_break_raises(card):
    with pytest.raises(ValueError, match="below the lowest"):
        card.rate_for(1, Decimal("0.1"))


def test_dimensional_weight_wins_when_larger():
    assert billable_weight(Decimal("2.0"), Decimal("120"), Decimal("210")) == Decimal("5.0")


def test_minimum_billable_weight_enforced():
    assert billable_weight(Decimal("0.2"), Decimal("0"), Decimal("0")) == Decimal("0.5")


def test_quote_totals_add_up(card):
    q = quote(card, "M5V 2T6", "V6B 1A1", Decimal("12.0"), "2026-11")
    assert q.zone_code == "NATIONAL"
    assert q.total == q.base + q.fuel + q.accessorials


def test_residential_quote_is_higher(card):
    args = (card, "M5V 2T6", "M4C 1B5", Decimal("5.0"), "2026-10")
    plain = quote(*args)
    resi = quote(*args, is_residential=True)
    assert resi.total - plain.total == Decimal("4.85")


def test_zero_weight_rejected(card):
    with pytest.raises(ValueError, match="must be positive"):
        quote(card, "M5V 2T6", "M4C 1B5", Decimal("0"), "2026-11")
