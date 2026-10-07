---
license: cc-by-4.0
language:
- ja
task_categories:
- text-generation
tags:
- japan
- law
- legal
- statutes
- xml
- digital-agency
- pretraining
size_categories:
- 10K<n<100K
configs:
- config_name: laws
  data_files: parquet/laws.parquet
  default: true
---

# egov-laws-jp

The statutes, cabinet orders, ministerial ordinances and rules of Japan that
e-Gov 法令検索 distributes as its bulk download, one row per law revision, with
the original XML and a plain-text extraction side by side.

CC BY 4.0. The text of a statute is not a copyrightable work under Article 13
of the Copyright Act, and what the Digital Agency adds (titles' readings,
categories, the revision history) is published under PDL1.0, which is
compatible with CC BY 4.0.

## What is here

One table, `laws`, 10,679 rows.

| | |
|---|---:|
| rows (law revisions) | 10,679 |
| distinct laws (`law_id`) | 8,997 |
| revisions not yet in force (`is_unenforced`) | 1,676 |
| characters of `text` | 573,048,356 |
| characters of `xml` | 2,476,643,432 |

By `law_type`:

| law_type | revisions | laws |
|---|---:|---:|
| 府省令 (ministerial ordinance) | 4,452 | 4,098 |
| 法律 (act) | 3,225 | 2,101 |
| 政令 (cabinet order) | 2,518 | 2,324 |
| 規則 (rule) | 416 | 407 |
| 勅令 (imperial order) | 67 | 66 |
| 憲法 (constitution) | 1 | 1 |

Columns:

| column | |
|---|---|
| `revision_id` | `{law_id}_{enforcement date}_{amending law id}`, unique per row |
| `law_id` | the law's id, shared by all of its revisions |
| `law_type` | 憲法 / 法律 / 政令 / 勅令 / 府省令 / 規則 |
| `law_num`, `law_title`, `law_title_kana`, `old_law_title` | as in the publisher's list. `old_law_title` is null for most rows |
| `promulgation_date`, `amendment_promulgation_date`, `enforcement_date` | the publisher's own text, in the era calendar with kanji numerals |
| `*_iso` | the same three dates as `YYYY-MM-DD` |
| `amendment_law_title`, `amendment_law_num` | the law that produced this revision. Null for a law's first revision |
| `enforcement_note` | the publisher's remark on the enforcement date |
| `is_unenforced` | true when the revision is promulgated but not yet in force |
| `source_url` | the page for this revision on laws.e-gov.go.jp |
| `xml` | the revision's XML, exactly as distributed |
| `text` | every text node of the XML, one per line, with ruby readings removed |

## The thing to know before training on it

Every revision is a full copy of the law. A law amended thirty times appears
thirty times, and the copies differ in a handful of articles. The most
revised law here has 33 revisions. If the table is used as a corpus as it
stands, the large laws dominate it.

Keeping one revision per law (the latest one in force) leaves 8,997 rows, 163
million characters of `text` against 573 million for the whole table:

```sql
-- DuckDB, straight off the Parquet
WITH r AS (
  SELECT *, row_number() OVER (PARTITION BY law_id
                               ORDER BY enforcement_date_iso DESC) AS rn
  FROM read_parquet('parquet/laws.parquet')
  WHERE NOT is_unenforced
)
SELECT law_id, law_title, text FROM r WHERE rn = 1;
```

Every law has at least one revision in force, so this keeps all 8,997 laws.

The history only reaches back to 2015-08-01 for acts, orders and imperial
orders, and to 2016-10-01 for ministerial ordinances and rules, because that
is where e-Gov started keeping revisions. Before those dates only the version
in force on that day exists.

## What `text` is and is not

It is the text nodes of the XML joined with newlines. Article and paragraph
boundaries, and the boundary between the main provisions and the
supplementary provisions, are lines and nothing more. Read `xml` when the
structure matters.

Two things are in it that a reader may not want:

- Tables are split cell by cell, so a schedule appears as a column of word
  fragments. A few laws are mostly schedules (the customs tariff, the income
  tax tables) and their `text` is mostly such fragments.
- Formulas are split the same way.

The 27,808 ruby readings are removed from `text` and kept in `xml`.

Images are not here. `<Fig src="./pict/...">` refers to a picture that the bulk
download does not contain, so 42,233 figures are references to nothing.

## Reading it

```python
import pyarrow.parquet as pq

# the rows are heavy (the XML of the largest law is 17 MB); read the columns you need
t = pq.read_table("parquet/laws.parquet", columns=["revision_id", "law_title", "text"])
```

## What is not here

- Repealed and lapsed laws. The bulk download carries only laws in force or
  coming into force. The API lists 559 more, which are not in this table.
- Laws before e-Gov's start dates above, and any revision before them.
- 告示, 訓令, 通達, 条例, 規程. e-Gov does not carry them.
- Images and attachments.

## Reproducing it

```bash
git clone https://github.com/yuiseki/egov-laws-jp
cd egov-laws-jp
uv sync
# data/raw/all_xml.zip from https://laws.e-gov.go.jp/bulkdownload?file_section=1&only_xml_flag=true
uv run scripts/02_export_parquet.py
```

`data/provenance.yaml` records the md5 and size of the archive this table was
made from.

## Licence

CC BY 4.0.

    出典：e-Gov法令検索（デジタル庁）
    https://laws.e-gov.go.jp/
    （2026年9月16日時点のデータを加工）

The publisher applies PDL1.0, 公共データ利用規約（第1.0版）, whose clause
1.7(3) states that it is compatible with CC BY 4.0.

PDL1.0 asks that a modification be declared apart from the attribution. The
modifications are listed in `LICENSE` beside this file, in Japanese as the
terms ask. None of them changes a value in `xml`.
