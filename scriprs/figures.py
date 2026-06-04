from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .constants import PHASE_ORDER, PHASE_SHORT_LABELS, PHASE_STATS_METRICS


PHASE_PALETTE = {
    "Free-viewing Phase": "#D7EEF4",
    "Interaction Phase": "#3F6FA8",
    "Recovery Phase": "#9DC6DA",
}


def plot_phase_metric_boxplots(subject_df: pd.DataFrame, output_pdf: Path) -> None:
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="white", context="talk")
    fig, axes = plt.subplots(2, 2, figsize=(14, 11), constrained_layout=True)
    axes = axes.ravel()
    labels = {
        "Normalized_Velocity_Pct": "Normalized angular velocity (%)",
        "MedianAngularVelocity": "Median angular velocity (deg/s)",
        "FTR": "Fixation time ratio (%)",
        "SER": "Spatial exploration range (deg)",
    }
    for ax, metric in zip(axes, PHASE_STATS_METRICS):
        sns.boxplot(
            data=subject_df,
            x="Phase",
            y=metric,
            hue="Phase",
            order=PHASE_ORDER,
            hue_order=PHASE_ORDER,
            palette=PHASE_PALETTE,
            width=0.25,
            fliersize=0,
            linewidth=1.1,
            dodge=False,
            legend=False,
            ax=ax,
        )
        sns.stripplot(
            data=subject_df,
            x="Phase",
            y=metric,
            order=PHASE_ORDER,
            color="#222222",
            size=3.2,
            alpha=0.45,
            jitter=0.08,
            ax=ax,
        )
        ax.set_xlabel("")
        ax.set_ylabel(labels[metric])
        ax.set_xticks(range(3), [PHASE_SHORT_LABELS[p] for p in PHASE_ORDER])
        ax.grid(axis="y", color="#D8DEE9", linewidth=0.7)
        ax.grid(axis="x", visible=False)
        sns.despine(ax=ax, top=True, right=True)
    fig.savefig(output_pdf, dpi=300, bbox_inches="tight")
    fig.savefig(output_pdf.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_top2_burden(top2_df: pd.DataFrame, output_pdf: Path) -> None:
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10.0, 5.8), facecolor="white")
    bars = ax.barh(
        top2_df["Label"],
        top2_df["Top2Pct"],
        color="#4C78A8",
        edgecolor="#35516F",
        linewidth=0.8,
    )
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("Top-2-box percentage (%)")
    ax.set_title("Most frequently reported interruption-related burden items")
    ax.axvline(50, color="#9AA3AF", linestyle="--", linewidth=1.0, zorder=0)
    ax.grid(axis="x", color="#E6EAF0", linewidth=0.8)
    ax.grid(axis="y", visible=False)
    for bar, value in zip(bars, top2_df["Top2Pct"]):
        ax.text(min(value + 1.2, 98.0), bar.get_y() + bar.get_height() / 2, f"{value:.1f}%", va="center")
    ax.text(0.98, 0.04, f"N = {int(top2_df['ValidN'].max())}", transform=ax.transAxes, ha="right")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(output_pdf, dpi=300, bbox_inches="tight")
    fig.savefig(output_pdf.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

