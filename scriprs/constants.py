from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
ROOT = PACKAGE_DIR.parents[0]
DEFAULT_QUESTIONNAIRE = PACKAGE_DIR / "Questionnaire.xlsx"

PHASE_ORDER = [
    "Free-viewing Phase",
    "Interaction Phase",
    "Recovery Phase",
]

PHASE_SHORT_LABELS = {
    "Free-viewing Phase": "Free\nViewing",
    "Interaction Phase": "Interruption",
    "Recovery Phase": "Recovery",
}

FIXATION_THRESHOLD_DPS = 15.0

LIKERT_MAP = {
    "Strongly disagree": 1,
    "Disagree": 2,
    "Neutral / unsure": 3,
    "Neutral": 3,
    "Agree": 4,
    "Strongly agree": 5,
    "None": 1,
    "Slight": 2,
    "Moderate": 3,
    "Severe": 4,
    "Very severe": 5,
}

BURDEN_ITEMS = {
    "Q4": "Attention lock",
    "Q5": "Missed background events",
    "Q6": "Fear of missing content",
    "Q7": "Post-task disorientation",
    "Q8": "Compensatory scanning",
}

HEAD_METRICS = [
    "MeanAngularVelocity",
    "MedianAngularVelocity",
    "FTR",
    "SER",
]

PHASE_STATS_METRICS = [
    "Normalized_Velocity_Pct",
    "MedianAngularVelocity",
    "FTR",
    "SER",
]
