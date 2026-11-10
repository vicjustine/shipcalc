# shipcalc

Freight rate engine for regional parcel carriers. Prices a shipment from a
published rate card, resolving the rating zone from postal codes and applying
fuel, residential and oversize surcharges.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run the tests

```bash
pytest
```

## Lint

```bash
ruff check .
```

## Usage

```python
from decimal import Decimal
from shipcalc import RateCard, quote

card = RateCard.from_csv("data/rate_card_2026Q4.csv")
q = quote(card, "M5V 2T6", "V6B 1A1", Decimal("12.0"), "2026-11")
print(q.total, q.zone_code)
```

## Data

- `data/rate_card_2026Q4.csv` — per-kg rates by zone band and weight break.
- `data/shipments_fy2026.csv` — sample shipment ledger (test data only).

## Layout

| Path | What it holds |
| --- | --- |
| `src/shipcalc/zones.py` | Postal-prefix to rating-zone resolution |
| `src/shipcalc/rates.py` | Rate card lookup, billable weight, quoting |
| `src/shipcalc/surcharges.py` | Fuel, residential and oversize surcharges |
| `tests/` | pytest suite |
