# egov-laws-jp

Dataset: https://huggingface.co/datasets/yuiseki/egov-laws-jp

The laws of Japan from the e-Gov 法令検索 bulk download, one row per law
revision, and the code that builds the table. This repository holds the code;
the data is on the Hub.

## Where things are

```
src/egov_laws/parse.py        XML -> text (ruby readings removed), revision id
src/egov_laws/dates.py        era-calendar kanji dates -> ISO 8601
src/egov_laws/export.py       CSV row -> table row, and the schema
scripts/02_export_parquet.py  all_xml.zip -> data/parquet/laws.parquet
src/publish.py                pushes the table and its card to the Hub
tests/                        parse, dates, export

data/README.md                the dataset card. Uploaded as-is
data/LICENSE                  the CC BY notice and the modification statement
data/provenance.yaml          where the archive came from, and what was done to it
data/raw/                     not in git: all_xml.zip from e-Gov
data/parquet/                 not in git: the table
```

## Running it

```sh
uv sync
# put all_xml.zip from the bulk download into data/raw/
uv run scripts/02_export_parquet.py
uv run pytest
uv run src/publish.py          # dry run; --push to upload
```

The export took about a minute here, under an 8 GB memory cap.
