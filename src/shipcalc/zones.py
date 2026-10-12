"""Zone resolution from origin/destination postal prefixes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Zone:
    """A rating zone. `band` drives the rate card lookup."""

    code: str
    band: int
    description: str


ZONES: dict[str, Zone] = {
    "METRO": Zone("METRO", 1, "Same metropolitan area"),
    "REGIONAL": Zone("REGIONAL", 2, "Within province or state"),
    "NATIONAL": Zone("NATIONAL", 3, "Cross-country domestic"),
    "REMOTE": Zone("REMOTE", 4, "Rural or limited-service area"),
}

# Postal prefixes that carriers treat as limited-service.
REMOTE_PREFIXES = frozenset({"X0", "Y0", "A0", "B0", "R0"})


def resolve_zone(origin: str, destination: str) -> Zone:
    """Resolve the rating zone for an origin/destination pair.

    Args:
        origin: Postal code of the pickup point.
        destination: Postal code of the delivery point.

    Raises:
        ValueError: If either postal code is shorter than three characters.
    """
    if len(origin) < 3 or len(destination) < 3:
        raise ValueError("postal codes must be at least three characters")

    o = origin.strip().upper()
    d = destination.strip().upper()

    if d[:2] in REMOTE_PREFIXES or o[:2] in REMOTE_PREFIXES:
        return ZONES["REMOTE"]
    if o[:3] == d[:3]:
        return ZONES["METRO"]
    if o[0] == d[0]:
        return ZONES["REGIONAL"]
    return ZONES["NATIONAL"]
