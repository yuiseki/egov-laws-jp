import pytest

from egov_laws.dates import kanji_to_int, wareki_to_iso


@pytest.mark.parametrize(
    ("s", "n"),
    [
        ("一", 1),
        ("九", 9),
        ("十", 10),
        ("十一", 11),
        ("二十", 20),
        ("二十六", 26),
        ("三十一", 31),
        ("元", 1),
        ("〇", 0),
        ("百二十", 120),
    ],
)
def test_kanji_to_int(s, n):
    assert kanji_to_int(s) == n


@pytest.mark.parametrize(
    ("s", "iso"),
    [
        ("明治五年十一月九日", "1872-11-09"),
        ("昭和二十六年十二月一日", "1951-12-01"),
        ("平成元年一月八日", "1989-01-08"),
        ("令和八年九月十六日", "2026-09-16"),
        ("大正十五年十二月二十五日", "1926-12-25"),
        ("昭和六十四年一月七日", "1989-01-07"),
    ],
)
def test_wareki_to_iso(s, iso):
    assert wareki_to_iso(s) == iso


def test_wareki_to_iso_none_passthrough():
    assert wareki_to_iso(None) is None


def test_wareki_to_iso_rejects_garbage():
    with pytest.raises(ValueError):
        wareki_to_iso("西暦2020年")
