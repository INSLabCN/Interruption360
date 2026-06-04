from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

from .constants import BURDEN_ITEMS, LIKERT_MAP


@dataclass
class QuestionnaireData:
    sheet_name: str
    raw: pd.DataFrame
    valid: pd.DataFrame
    question_cols: list[str]
    name_col: str
    age_col: str | None
    gender_col: str | None
    vr_col: str | None
    sickness_col: str | None


def find_response_sheet(xlsx_path: Path) -> tuple[str, pd.DataFrame]:
    workbook = pd.ExcelFile(xlsx_path)
    for sheet in workbook.sheet_names:
        df = pd.read_excel(xlsx_path, sheet_name=sheet)
        columns = [str(c) for c in df.columns]
        if any("Name (Required)" in c for c in columns) and len(columns) >= 9:
            return sheet, df
    for sheet in workbook.sheet_names:
        df = pd.read_excel(xlsx_path, sheet_name=sheet)
        if not df.empty:
            return sheet, df
    raise ValueError(f"No usable questionnaire sheet found in {xlsx_path}")


def to_likert_score(value: object) -> float:
    if pd.isna(value):
        return pd.NA
    if isinstance(value, (int, float)) and 1 <= float(value) <= 5:
        return int(value)

    text = str(value).strip()
    if text in LIKERT_MAP:
        return LIKERT_MAP[text]

    lowered = text.lower()
    if "strongly disagree" in lowered:
        return 1
    if lowered == "disagree" or " disagree" in lowered:
        return 2
    if "neutral" in lowered or "unsure" in lowered:
        return 3
    if "strongly agree" in lowered:
        return 5
    if lowered == "agree" or " agree" in lowered:
        return 4
    return pd.NA


def _first_column_containing(columns: Iterable[object], token: str) -> str | None:
    token_lower = token.lower()
    matches = [c for c in columns if token_lower in str(c).lower()]
    return str(matches[0]) if matches else None


def load_questionnaire(xlsx_path: Path, max_users: int | None = None) -> QuestionnaireData:
    sheet, raw = find_response_sheet(xlsx_path)
    df = raw.dropna(how="all").copy()
    df.columns = [str(c) for c in df.columns]

    name_col = _first_column_containing(df.columns, "Name (Required)")
    if name_col is None:
        raise ValueError("Cannot find participant name column.")

    question_cols = list(df.columns[:9])
    for col in question_cols:
        df[f"{col}__score"] = df[col].map(to_likert_score)

    score_cols = [f"{col}__score" for col in question_cols]
    df["valid_answer_count"] = df[score_cols].notna().sum(axis=1)
    df[name_col] = df[name_col].astype(str).str.strip()

    invalid_names = {"", "nan", "name", "Name (Required)"}
    valid = df[(~df[name_col].isin(invalid_names)) & (df["valid_answer_count"] >= 5)].copy()
    if max_users is not None:
        valid = valid.head(max_users).copy()

    return QuestionnaireData(
        sheet_name=sheet,
        raw=raw,
        valid=valid,
        question_cols=question_cols,
        name_col=name_col,
        age_col=_first_column_containing(df.columns, "Age (Required)"),
        gender_col=_first_column_containing(df.columns, "Gender (Required)"),
        vr_col=_first_column_containing(df.columns, "AR/VR"),
        sickness_col=_first_column_containing(df.columns, "motion sickness"),
    )


def build_top2_burden(q: QuestionnaireData) -> pd.DataFrame:
    rows = []
    for qid, label in BURDEN_ITEMS.items():
        q_index = int(qid[1:])
        col = f"{q.question_cols[q_index - 1]}__score"
        values = pd.to_numeric(q.valid[col], errors="coerce").dropna()
        count = int((values >= 4).sum())
        total = int(len(values))
        rows.append(
            {
                "Item": qid,
                "Label": label,
                "Top2Count": count,
                "ValidN": total,
                "Top2Pct": round(100.0 * count / total, 1) if total else pd.NA,
            }
        )
    return pd.DataFrame(rows).sort_values("Top2Pct", ascending=False).reset_index(drop=True)


def build_participant_table(q: QuestionnaireData) -> pd.DataFrame:
    df = q.valid.copy()
    out = pd.DataFrame({"participant": df[q.name_col].astype(str).str.strip()})
    if q.age_col:
        out["age"] = pd.to_numeric(df[q.age_col], errors="coerce")
    if q.gender_col:
        out["gender"] = df[q.gender_col].astype(str).str.strip()
    if q.vr_col:
        out["vr_experience"] = df[q.vr_col].astype(str).str.strip()
    if q.sickness_col:
        out["motion_sickness"] = df[q.sickness_col].astype(str).str.strip()
    return out
