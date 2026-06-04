import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, shapiro, wilcoxon

from .constants import PHASE_ORDER, PHASE_STATS_METRICS


PAIRWISE_PHASES = [
    ("Free-viewing Phase", "Interaction Phase"),
    ("Interaction Phase", "Recovery Phase"),
    ("Free-viewing Phase", "Recovery Phase"),
]


def p_to_stars(p_value: float) -> str:
    if p_value < 0.001:
        return "***"
    if p_value < 0.01:
        return "**"
    if p_value < 0.05:
        return "*"
    return "ns"


def _safe_shapiro(values: np.ndarray) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 3 or np.allclose(values, values[0]):
        return np.nan, np.nan
    stat, p_value = shapiro(values)
    return float(stat), float(p_value)


def _add_holm_adjustment(rows: list[dict]) -> list[dict]:
    if not rows:
        return rows
    ordered = sorted(enumerate(rows), key=lambda item: item[1]["p_raw"])
    adjusted_by_index = {}
    running_max = 0.0
    m = len(rows)
    for rank, (original_index, row) in enumerate(ordered, start=1):
        adjusted = min((m - rank + 1) * float(row["p_raw"]), 1.0)
        running_max = max(running_max, adjusted)
        adjusted_by_index[original_index] = running_max
    for idx, row in enumerate(rows):
        row["p_holm"] = adjusted_by_index[idx]
        row["Stars_by_p_holm"] = p_to_stars(row["p_holm"])
    return rows


def run_phase_statistics(subject_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    normality_rows = []
    global_rows = []
    pairwise_rows = []

    for metric in PHASE_STATS_METRICS:
        pivot = subject_df.pivot(index="UserID", columns="Phase", values=metric).dropna()
        pivot = pivot[PHASE_ORDER]
        n_users = len(pivot)

        for phase in PHASE_ORDER:
            values = pivot[phase].to_numpy(dtype=float)
            stat, p_value = _safe_shapiro(values)
            normality_rows.append(
                {
                    "Metric": metric,
                    "Phase": phase,
                    "N": len(values),
                    "Shapiro_W": stat,
                    "Shapiro_p": p_value,
                    "Mean": float(np.mean(values)),
                    "SD": float(np.std(values, ddof=1)),
                }
            )

        fried_stat, fried_p = friedmanchisquare(*(pivot[phase].to_numpy(dtype=float) for phase in PHASE_ORDER))
        kendall_w = float(fried_stat / (n_users * (len(PHASE_ORDER) - 1))) if n_users else np.nan
        global_rows.append(
            {
                "Metric": metric,
                "Global_Test": "Friedman",
                "Statistic_Label": "Q",
                "Statistic": float(fried_stat),
                "DF": len(PHASE_ORDER) - 1,
                "N": n_users,
                "p_value": float(fried_p),
                "Effect_Size_Type": "Kendall_W",
                "Effect_Size": kendall_w,
            }
        )

        metric_pairwise_rows = []
        for phase_a, phase_b in PAIRWISE_PHASES:
            x = pivot[phase_a].to_numpy(dtype=float)
            y = pivot[phase_b].to_numpy(dtype=float)
            diff = y - x
            _, diff_normal_p = _safe_shapiro(diff)
            stat, raw_p = wilcoxon(x, y, alternative="two-sided", method="auto")
            metric_pairwise_rows.append(
                {
                    "Metric": metric,
                    "Phase_A": phase_a,
                    "Phase_B": phase_b,
                    "Pairwise_Test": "wilcoxon_signed_rank_two_sided",
                    "Diff_Shapiro_p": diff_normal_p,
                    "Statistic": float(stat),
                    "p_raw": float(raw_p),
                    "Mean_A": float(np.mean(x)),
                    "Mean_B": float(np.mean(y)),
                    "Mean_Diff_B_minus_A": float(np.mean(diff)),
                }
            )
        pairwise_rows.extend(_add_holm_adjustment(metric_pairwise_rows))

    return pd.DataFrame(normality_rows), pd.DataFrame(global_rows), pd.DataFrame(pairwise_rows)
