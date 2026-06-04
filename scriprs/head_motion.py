from pathlib import Path

import numpy as np
import pandas as pd

from .constants import FIXATION_THRESHOLD_DPS, PHASE_ORDER, PHASE_STATS_METRICS
from .utils import ensure_dir, sorted_csv_files, user_tag_from_file


def clean_head_motion_frame(df: pd.DataFrame) -> pd.DataFrame:
    required = {"FrameIdx", "UI_Active", "VideoTime"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns for cleaning: {missing}")

    out = df[df["FrameIdx"] >= 0].copy()
    conditions = [
        out["UI_Active"].fillna(0).astype(int) == 1,
        (out["UI_Active"].fillna(0).astype(int) == 0) & (out["VideoTime"] < 8.0),
        (out["UI_Active"].fillna(0).astype(int) == 0) & (out["VideoTime"] >= 8.0),
    ]
    out["Phase"] = np.select(conditions, PHASE_ORDER, default="Unknown")
    return out


def clean_head_motion_directory(raw_dir: Path, clean_dir: Path) -> list[Path]:
    ensure_dir(clean_dir)
    written = []
    for csv_path in sorted_csv_files(raw_dir):
        df = pd.read_csv(csv_path)
        cleaned = clean_head_motion_frame(df)
        out_path = clean_dir / f"{csv_path.stem}c.csv"
        cleaned.to_csv(out_path, index=False)
        written.append(out_path)
    return written


def add_angular_velocity(df: pd.DataFrame) -> pd.DataFrame:
    required = ["VideoID", "GlobalTime", "Qx", "Qy", "Qz", "Qw", "Phase"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = df.sort_values(["VideoID", "GlobalTime"], kind="mergesort").copy()
    group = out.groupby("VideoID", sort=False)
    prev_time = group["GlobalTime"].shift(1)
    prev_qx = group["Qx"].shift(1)
    prev_qy = group["Qy"].shift(1)
    prev_qz = group["Qz"].shift(1)
    prev_qw = group["Qw"].shift(1)

    dot = out["Qx"] * prev_qx + out["Qy"] * prev_qy + out["Qz"] * prev_qz + out["Qw"] * prev_qw
    dot = dot.abs().clip(0.0, 1.0)
    dt = out["GlobalTime"] - prev_time
    out["AngularVelocity"] = np.degrees(2.0 * np.arccos(dot)) / dt
    out["AngularVelocity"] = out["AngularVelocity"].where((dt > 0) & dot.notna())
    return out


def compute_phase_metrics(detail_df: pd.DataFrame) -> pd.DataFrame:
    phase_df = detail_df[detail_df["Phase"].isin(PHASE_ORDER)].copy()
    phase_df["IsFixation"] = (phase_df["AngularVelocity"] < FIXATION_THRESHOLD_DPS).fillna(False)

    group = phase_df.groupby(["UserID", "VideoID", "Phase"], sort=False)
    q0x = group["Qx"].transform("first")
    q0y = group["Qy"].transform("first")
    q0z = group["Qz"].transform("first")
    q0w = group["Qw"].transform("first")
    dot_anchor = phase_df["Qx"] * q0x + phase_df["Qy"] * q0y + phase_df["Qz"] * q0z + phase_df["Qw"] * q0w
    phase_df["DeviationAngle"] = np.degrees(2.0 * np.arccos(dot_anchor.abs().clip(0.0, 1.0)))

    metrics = (
        group.agg(
            GlobalTime_Start=("GlobalTime", "min"),
            GlobalTime_End=("GlobalTime", "max"),
            MeanAngularVelocity=("AngularVelocity", "mean"),
            MedianAngularVelocity=("AngularVelocity", "median"),
            FTR=("IsFixation", "mean"),
            SER=("DeviationAngle", lambda x: x.quantile(0.95)),
        )
        .reset_index()
    )
    metrics["FTR"] = metrics["FTR"] * 100.0
    metrics["Phase"] = pd.Categorical(metrics["Phase"], categories=PHASE_ORDER, ordered=True)
    return metrics.sort_values(["UserID", "VideoID", "Phase"], kind="mergesort").reset_index(drop=True)


def compute_phase_metrics_from_clean_dir(clean_dir: Path) -> pd.DataFrame:
    details = []
    csv_files = sorted_csv_files(clean_dir)
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {clean_dir}")

    for csv_path in csv_files:
        df = pd.read_csv(csv_path)
        df["UserID"] = user_tag_from_file(csv_path)
        with_velocity = add_angular_velocity(df)
        details.append(
            with_velocity[
                ["UserID", "VideoID", "GlobalTime", "Phase", "AngularVelocity", "Qx", "Qy", "Qz", "Qw"]
            ]
        )
    return compute_phase_metrics(pd.concat(details, ignore_index=True))


def add_normalized_velocity(phase_metrics: pd.DataFrame) -> pd.DataFrame:
    out = phase_metrics.copy()
    baseline = (
        out[out["Phase"] == "Free-viewing Phase"][["UserID", "VideoID", "MeanAngularVelocity"]]
        .rename(columns={"MeanAngularVelocity": "BaselineMeanAngularVelocity"})
    )
    out = out.merge(baseline, on=["UserID", "VideoID"], how="left", validate="many_to_one")
    out["Normalized_Velocity_Pct"] = (
        out["MeanAngularVelocity"] / out["BaselineMeanAngularVelocity"] * 100.0
    )
    return out


def aggregate_subject_level(phase_metrics: pd.DataFrame) -> pd.DataFrame:
    prepared = add_normalized_velocity(phase_metrics)
    prepared["Phase"] = pd.Categorical(prepared["Phase"], categories=PHASE_ORDER, ordered=True)
    subject = (
        prepared.groupby(["UserID", "Phase"], observed=False, as_index=False)[PHASE_STATS_METRICS]
        .mean()
        .sort_values(["UserID", "Phase"], kind="mergesort")
    )
    return subject

