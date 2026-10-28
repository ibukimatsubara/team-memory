---
title: No blur before detection
author: example-dev
agent: codex
date: 2026-10-22
status: current
---

We tried adding a Gaussian blur (5x5) before detection to reduce noise, but nearby small circles merged and were detected as one. We do not blur; small noise is removed with HoughCircles' minRadius instead.
