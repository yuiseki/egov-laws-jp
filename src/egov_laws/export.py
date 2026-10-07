"""Build parquet rows (one per law revision) from the e-Gov bulk download."""

import pyarrow as pa

from egov_laws.dates import wareki_to_iso
from egov_laws.parse import revision_id_from_url

_COLUMNS = {
    "法令種別": "law_type",
    "法令番号": "law_num",
    "法令名": "law_title",
    "法令名読み": "law_title_kana",
    "旧法令名": "old_law_title",
    "公布日": "promulgation_date",
    "改正法令名": "amendment_law_title",
    "改正法令番号": "amendment_law_num",
    "改正法令公布日": "amendment_promulgation_date",
    "施行日": "enforcement_date",
    "施行日備考": "enforcement_note",
    "法令ID": "law_id",
    "本文URL": "source_url",
}

_DATE_COLUMNS = ["promulgation_date", "amendment_promulgation_date", "enforcement_date"]


def row_from_csv(csv_row: dict[str, str]) -> dict:
    row = {"revision_id": revision_id_from_url(csv_row["本文URL"])}
    for ja, en in _COLUMNS.items():
        row[en] = csv_row[ja] or None
    for col in _DATE_COLUMNS:
        row[f"{col}_iso"] = wareki_to_iso(row[col])
    row["is_unenforced"] = csv_row["未施行"] == "○"
    return row


SCHEMA = pa.schema(
    [(en, pa.string()) for en in ["revision_id", *_COLUMNS.values()]]
    + [(f"{c}_iso", pa.string()) for c in _DATE_COLUMNS]
    + [("is_unenforced", pa.bool_()), ("text", pa.string()), ("xml", pa.string())]
)
