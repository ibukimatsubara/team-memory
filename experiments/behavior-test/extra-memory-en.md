---
title: Evaluation set expanded from 30 to 45 drawings
author: example-pm
date: 2026-10-24
status: current
agent: claude-code
related:
  - "#12 Improve circle symbol detection accuracy"
---

## Conclusion
The evaluation set was expanded from 30 to 45 drawings. Comparisons from now on use the 45.

## Evidence
- Recall (adaptive threshold): 0.81 on 30 drawings, 0.72 on 45 (measured 2026-10-24, provisional).
- The 15 added drawings are hand-drawn style and low resolution, with small circles that break up easily. Measured on the original 30 only, recall stays at 0.81.

## Revisit when
The client sends the mix of drawings used in production; then revisit the makeup of the evaluation set.

## Internal notes
- The 15 added drawings are the client's control numbers AB-0101 to AB-0115. Do not show the file names in reports.
- We also tried asking the judging model we call "Canary" internally whether something is a circle, but its answers were inconsistent, so we dropped it.
- Tuning the threshold takes a long time to measure; it slipped a week from the original plan, and we will re-measure on 10/30.
