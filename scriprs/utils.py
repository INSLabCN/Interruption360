import re
from pathlib import Path


def natural_id(text: object) -> int:
    match = re.search(r"(\d+)", str(text))
    return int(match.group(1)) if match else 10**9


def sorted_csv_files(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.csv"), key=lambda path: natural_id(path.stem))


def user_tag_from_file(path: Path) -> str:
    stem = path.stem
    if stem.endswith("_c"):
        stem = stem[:-2]
    elif stem.endswith("c") and len(stem) > 1:
        stem = stem[:-1]
    match = re.search(r"(\d+)", stem)
    return f"U{int(match.group(1))}" if match else stem


def normalize_user_label(value: object) -> str:
    match = re.search(r"(\d+)", str(value))
    if match:
        return f"user{int(match.group(1))}"
    return str(value).strip().lower()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
