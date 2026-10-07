from egov_laws.export import row_from_csv

CSV_ROW = {
    "法令種別": "法律",
    "法令番号": "昭和二十六年法律第二百八十五号",
    "法令名": "博物館法",
    "法令名読み": "はくぶつかんほう",
    "旧法令名": "",
    "公布日": "昭和二十六年十二月一日",
    "改正法令名": "地方自治法の一部を改正する法律",
    "改正法令番号": "令和四年法律第四十九号",
    "改正法令公布日": "令和四年四月十五日",
    "施行日": "令和五年四月一日",
    "施行日備考": "",
    "法令ID": "326AC1000000285",
    "本文URL": "https://laws.e-gov.go.jp/law/326AC1000000285/20230401_504AC0000000024",
    "未施行": "",
}


def test_row_from_csv_renames_and_derives_revision_id():
    row = row_from_csv(CSV_ROW)
    assert row["revision_id"] == "326AC1000000285_20230401_504AC0000000024"
    assert row["law_id"] == "326AC1000000285"
    assert row["law_title"] == "博物館法"
    assert row["law_num"] == "昭和二十六年法律第二百八十五号"
    assert row["enforcement_date"] == "令和五年四月一日"
    assert row["source_url"] == CSV_ROW["本文URL"]


def test_row_from_csv_unenforced_flag():
    assert row_from_csv(CSV_ROW)["is_unenforced"] is False
    assert row_from_csv({**CSV_ROW, "未施行": "○"})["is_unenforced"] is True


def test_row_from_csv_empty_strings_become_none():
    row = row_from_csv(CSV_ROW)
    assert row["old_law_title"] is None
    assert row["enforcement_note"] is None


def test_schema_matches_row_keys():
    from egov_laws.export import SCHEMA

    assert set(SCHEMA.names) == set(row_from_csv(CSV_ROW)) | {"text", "xml"}


def test_row_from_csv_iso_dates():
    row = row_from_csv(CSV_ROW)
    assert row["promulgation_date_iso"] == "1951-12-01"
    assert row["amendment_promulgation_date_iso"] == "2022-04-15"
    assert row["enforcement_date_iso"] == "2023-04-01"


def test_enforcement_date_iso_matches_revision_id():
    row = row_from_csv(CSV_ROW)
    assert row["revision_id"].split("_")[1] == row["enforcement_date_iso"].replace("-", "")
