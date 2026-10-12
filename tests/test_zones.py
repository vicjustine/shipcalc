import pytest

from shipcalc.zones import resolve_zone


def test_same_prefix_is_metro():
    assert resolve_zone("M5V 2T6", "M5V 1A1").code == "METRO"


def test_same_first_letter_is_regional():
    assert resolve_zone("M5V 2T6", "M4C 1B5").code == "REGIONAL"


def test_different_region_is_national():
    assert resolve_zone("M5V 2T6", "V6B 1A1").code == "NATIONAL"


@pytest.mark.parametrize("dest", ["X0A 0H0", "Y0B 1K0", "A0K 1C0"])
def test_remote_prefixes_win(dest):
    assert resolve_zone("M5V 2T6", dest).code == "REMOTE"


def test_remote_origin_also_counts():
    assert resolve_zone("X0A 0H0", "M5V 2T6").code == "REMOTE"


def test_short_postal_code_rejected():
    with pytest.raises(ValueError, match="at least three"):
        resolve_zone("M5", "V6B 1A1")
