"""Convert e-Gov Japanese-era kanji dates (昭和二十六年十二月一日) to ISO 8601."""

import re
from datetime import date

_ERA_BASE = {"明治": 1867, "大正": 1911, "昭和": 1925, "平成": 1988, "令和": 2018}
_DIGITS = {c: i for i, c in enumerate("〇一二三四五六七八九")}
_UNITS = {"十": 10, "百": 100}
_WAREKI = re.compile(
    r"^(明治|大正|昭和|平成|令和)([〇一二三四五六七八九十百元]+)年([一二三四五六七八九十]+)月([一二三四五六七八九十]+)日$"
)


def kanji_to_int(s: str) -> int:
    if s == "元":
        return 1
    total, digit = 0, None
    for c in s:
        if c in _DIGITS:
            digit = _DIGITS[c]
        elif c in _UNITS:
            total += (1 if digit is None else digit) * _UNITS[c]
            digit = None
        else:
            raise ValueError(f"not a kanji numeral: {s!r}")
    return total + (digit or 0)


def wareki_to_iso(s: str | None) -> str | None:
    if s is None:
        return None
    m = _WAREKI.match(s)
    if not m:
        raise ValueError(f"not a wareki date: {s!r}")
    era, y, mo, d = m.groups()
    # date() validates the calendar day, so an impossible date raises ValueError.
    return date(_ERA_BASE[era] + kanji_to_int(y), kanji_to_int(mo), kanji_to_int(d)).isoformat()
