# Interruption360

**Interruption360** is an interruption-aware dataset for **task-oriented 360-degree video viewing**. It is designed to study how **UI-delivered interruptions** reshape immersive viewing behavior in virtual reality.

Unlike conventional 360-degree viewing datasets collected under passive-viewing settings, Interruption360 introduces **foreground UI tasks** during immersive video watching and records user behavior **before, during, and after interruption**. The dataset supports research on **interruption-aware behavior analysis**, **task-aware saliency modeling**, **viewport prediction**, and **immersive interaction design**.

---

## Overview

- **Participants:** 40
- **Videos:** 10 panoramic videos
- **Viewing device:** PICO 4
- **Tracking frequency:** 50 Hz
- **Scenario:** task-oriented 360-degree viewing with UI interruptions

In the experiment, participants watched 360-degree videos in VR while responding to **head-locked UI interruption tasks**. Each trial followed a fixed four-phase protocol:

1. **Free-viewing**
2. **Interruption**
3. **Recovery**
4. **Reset**

This design enables the study of how immersive viewing behavior changes under foreground task demands.

---

## Collected Data

The dataset includes the following information for each participant and trial:

- **Head-motion trajectories**
- **Euler-angle representations**
- **Quaternion representations**
- **Video identifiers**
- **UI display states**
- **Interaction-related annotations**
- **Phase labels** (Free-viewing / Interruption / Recovery / Reset)
- **Pre-test questionnaire data**
- **After-test questionnaire data**

The released data are **de-identified** and do not contain personally identifying information.

---

## UI Interruption Design

The experiment includes **four types of UI interruptions**:

- **Notification**
- **Weather**
- **Calculation**
- **System alert**

Each interruption appears at the center of the user’s field of view and remains visible for a fixed **5-second window**. This design allows controlled comparison of user behavior across phases while maintaining lightweight system-level task demands.

---

## What This Dataset Can Be Used For

Interruption360 can support research on:

- task-conditioned viewport behavior analysis
- interruption-aware user behavior modeling
- task-aware saliency prediction
- viewport prediction under UI interruptions
- attention allocation in immersive multimedia
- human-centered XR interface design
- subjective burden analysis in immersive task switching

---

## Main Characteristics

Interruption360 provides:

- **task-oriented** rather than passive-viewing data
- **temporally aligned** behavioral and annotation signals
- explicit **UI-state** and **phase** information
- controlled **interruption-response-recovery** structure
- subjective responses related to interruption burden

These properties make the dataset suitable for studying how foreground system tasks influence immersive media behavior.

---

## Privacy and Ethics

This dataset contains **de-identified behavioral and annotation data only**.  
All participants provided informed consent before the experiment.

---

## Citation

If you use this dataset, please cite:

```bibtex
@misc{interruption360,
  title        = {Interruption360: An Interruption-Aware Dataset for Task-Oriented 360-Degree Video Viewing},
  author       = {<AUTHOR NAMES HERE>},
  year         = {2026},
  howpublished = {\url{https://github.com/INSLabCN/Interruption360}},
  note         = {Dataset repository}
}
