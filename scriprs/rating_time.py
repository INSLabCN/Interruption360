from pathlib import Path

import pandas as pd

from .utils import sorted_csv_files


def extract_rating_events(clean_dir: Path) -> pd.DataFrame:
    rows = []
    for csv_path in sorted_csv_files(clean_dir):
        df = pd.read_csv(csv_path).sort_values("GlobalTime").reset_index(drop=True)
        user_file = csv_path.stem
        start_idx = None
        for idx, row in df.iterrows():
            active = int(row["UI_Active"]) if pd.notna(row["UI_Active"]) else 0
            if active == 1 and start_idx is None:
                start_idx = idx
            elif active == 0 and start_idx is not None:
                start_time = float(df.loc[start_idx, "GlobalTime"])
                end_time = float(row["GlobalTime"])
                rows.append(
                    {
                        "user_file": user_file,
                        "user_id": df.loc[start_idx, "UserID"],
                        "video_id": df.loc[start_idx, "VideoID"],
                        "ui_type": df.loc[start_idx, "UI_Type"],
                        "start_time": start_time,
                        "end_time": end_time,
                        "rating_time_sec": round(end_time - start_time, 4),
                    }
                )
                start_idx = None
    return pd.DataFrame(rows)


def summarize_rating_events(events: pd.DataFrame) -> dict[str, pd.DataFrame]:
    by_user_ui = (
        events.groupby(["user_file", "user_id", "ui_type"])["rating_time_sec"]
        .agg(["count", "mean", "median", "min", "max"])
        .reset_index()
        .sort_values(["user_file", "ui_type"])
    )
    user_ui_matrix = (
        events.groupby(["user_file", "ui_type"])["rating_time_sec"]
        .mean()
        .unstack()
        .round(4)
        .sort_index()
    )
    by_ui_type = (
        events.groupby("ui_type")["rating_time_sec"]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .reset_index()
    )
    within_5s = (
        events.assign(clicked_within_5s=events["rating_time_sec"] < 5)
        .groupby("ui_type")
        .agg(
            total_events=("rating_time_sec", "size"),
            clicked_within_5s_count=("clicked_within_5s", "sum"),
            clicked_within_5s_ratio=("clicked_within_5s", "mean"),
        )
        .reset_index()
    )
    return {
        "rating_time_events": events,
        "rating_time_by_user_ui": by_user_ui,
        "rating_time_user_ui_matrix": user_ui_matrix,
        "rating_time_by_ui_type": by_ui_type,
        "click_disappear_ratio_within_5s": within_5s,
    }
