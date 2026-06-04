# Code Descriptions

## `__init__.py`

This file marks `interruption360_repro` as a Python package and exposes the most basic shared constants for convenient imports.

## `__main__.py`

This file allows the package to be executed directly with Python and forwards execution to the main reproduction pipeline.

## `constants.py`

This file stores shared constants used across the reproduction code, including phase names, metric names, Likert mappings, and questionnaire item labels.

## `figures.py`

This file contains the plotting functions for paper-facing figures, including the phase metric boxplots and the Top-2-box burden chart.

## `head_motion.py`

This file cleans head-motion frame data, computes quaternion-based angular velocity, and aggregates trial-level and subject-level phase metrics.

## `pipeline.py`

This file is the main orchestration entry point. It runs the paper-limited reproduction workflow, saves tables and figures, and writes the scope report.

## `questionnaire.py`

This file loads the after-test questionnaire, converts Likert responses, extracts participant information, and computes the Top-2-box burden summary.

## `rating_time.py`

This file extracts UI-active intervals from available cleaned frame logs and exports handling-time summary tables as a data check.

## `statistics.py`

This file runs the repeated-measures statistical tests used by the paper-oriented reproduction workflow, including Friedman tests and Holm-corrected Wilcoxon comparisons.

## `utils.py`

This file contains small helper functions for natural sorting, user-ID extraction, directory creation, and participant label normalization.

