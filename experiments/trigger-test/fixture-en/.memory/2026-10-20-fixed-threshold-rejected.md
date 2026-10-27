---
title: Fixed-threshold binarization rejected
author: example-dev
agent: claude-code
date: 2026-10-20
status: current
---

Binarizing with a fixed threshold (128) broke up circles in faint drawings and detected text as circles in dark ones, because scan darkness differs between drawings.
Recall was 0.62 on 30 evaluation images. Switching to an adaptive threshold (blockSize 31, C 5) gave 0.81. The speed difference is 4 ms per image, which does not matter.
