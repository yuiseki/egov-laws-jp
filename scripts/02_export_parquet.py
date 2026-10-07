"""data/raw/all_xml.zip -> data/parquet/laws.parquet, one row per law revision.

usage: uv run scripts/02_export_parquet.py [--limit N] [--out PATH]
"""

import argparse
import csv
import io
import sys
import zipfile
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from egov_laws.export import SCHEMA, row_from_csv  # noqa: E402
from egov_laws.parse import extract_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BATCH_BYTES = 256 * 1024 * 1024


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", type=Path, default=ROOT / "data/raw/all_xml.zip")
    ap.add_argument("--out", type=Path, default=ROOT / "data/parquet/laws.parquet")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.zip) as z:
        with z.open("all_law_list.csv") as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))
            rows = [row_from_csv(r) for r in reader]
        by_id = {r["revision_id"]: r for r in rows}
        assert len(by_id) == len(rows), "duplicate revision_id in CSV"
        xml_names = {Path(n).stem: n for n in z.namelist() if n.endswith(".xml")}
        missing = set(by_id) ^ set(xml_names)
        assert not missing, (
            f"CSV and zip disagree on {len(missing)} revisions: {sorted(missing)[:5]}"
        )

        ids = sorted(by_id)[: args.limit]
        writer = None
        batch, size = [], 0

        def flush():
            nonlocal writer, batch, size
            if not batch:
                return
            table = pa.Table.from_pylist(batch, schema=SCHEMA)
            writer = writer or pq.ParquetWriter(args.out, SCHEMA, compression="zstd")
            writer.write_table(table)
            print(f"  wrote {len(batch)} rows", flush=True)
            batch, size = [], 0

        for rid in ids:
            xml = z.read(xml_names[rid])
            batch.append({**by_id[rid], "text": extract_text(xml), "xml": xml.decode("utf-8")})
            size += len(xml)
            if size >= BATCH_BYTES:
                flush()
        flush()
        writer.close()
    print(f"{len(ids)} rows -> {args.out}")


if __name__ == "__main__":
    main()
