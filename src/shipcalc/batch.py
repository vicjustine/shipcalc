"""Batch pricing of a shipment ledger.

Known rough edges, flagged in review:
  * `price_file` does CSV parsing, coercion, pricing and reporting in one pass.
  * Rows that fail validation are counted but the reason is lost.
  * Totals are accumulated as floats. Money should not round-trip through
    binary floating point: the running sum carries error (visible in the raw
    value) even when it happens to round to the right cents today.
"""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

from .rates import RateCard, quote


def price_file(card_path, ledger_path, period_override=None, verbose=False):
    """Price every row of a shipment ledger and print a summary."""
    card = RateCard.from_csv(card_path)

    total = 0.0
    priced = 0
    skipped = 0
    by_zone = {}

    with open(ledger_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            try:
                w = Decimal(row["actual_weight_kg"])
                length = Decimal(row["length_cm"])
                girth = Decimal(row["girth_cm"])
                period = period_override or row["billing_period"]
                res = row["residential"].strip().lower() == "true"

                q = quote(
                    card,
                    row["origin_postal"],
                    row["dest_postal"],
                    w,
                    period,
                    length_cm=length,
                    girth_cm=girth,
                    is_residential=res,
                )
            except Exception:
                skipped += 1
                continue

            total += float(q.total)
            priced += 1
            by_zone[q.zone_code] = by_zone.get(q.zone_code, 0) + 1

            if verbose:
                print(f"{row['shipment_id']}: {q.zone_code} {q.total}")

    print(f"priced={priced} skipped={skipped} total={total:.2f}")
    for z in sorted(by_zone):
        print(f"  {z}: {by_zone[z]}")

    return total


if __name__ == "__main__":
    price_file(
        Path(__file__).parent.parent.parent / "data" / "rate_card_2026Q4.csv",
        Path(__file__).parent.parent.parent / "data" / "shipments_fy2026.csv",
    )
