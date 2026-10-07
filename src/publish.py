"""Push the table and its card to the Hugging Face Hub.

uv run src/publish.py             # dry run
uv run src/publish.py --push
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "yuiseki/egov-laws-jp"

# Declared on the card, and therefore checked before anything moves.
CONFIGS = {"laws": "parquet/laws.parquet"}
FILES = ["README.md", "LICENSE", "provenance.yaml", "parquet/laws.parquet"]


def check_card() -> None:
    card = (ROOT / "data" / "README.md").read_text(encoding="utf-8")
    for name, path in CONFIGS.items():
        if not re.search(rf"^- config_name: {re.escape(name)}$", card, re.M):
            sys.exit(f"the card declares no config named {name}")
        if not re.search(rf"^  data_files: {re.escape(path)}$", card, re.M):
            sys.exit(f"the card's data_files do not point at {path}")
    for f in FILES:
        if not (ROOT / "data" / f).exists():
            sys.exit(f"missing {f}; run scripts/02_export_parquet.py first")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()

    check_card()
    total = sum((ROOT / "data" / f).stat().st_size for f in FILES)
    print(f"{a.repo}\n  {len(FILES)} files, {total / 1e6:.1f} MB")
    if not a.push:
        print("\ndry run. pass --push to upload")
        return

    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(a.repo, repo_type="dataset", exist_ok=True)
    api.upload_folder(
        repo_id=a.repo,
        repo_type="dataset",
        folder_path=ROOT / "data",
        allow_patterns=FILES,
        commit_message="Upload e-Gov laws table",
    )
    print(f"https://huggingface.co/datasets/{a.repo}")


if __name__ == "__main__":
    main()
