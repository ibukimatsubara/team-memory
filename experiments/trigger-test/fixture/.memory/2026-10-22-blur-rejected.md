---
title: 検出前のぼかしは入れない
author: example-dev
agent: codex
date: 2026-10-22
status: current
---

ノイズ対策として検出前にガウスぼかし（5x5）を入れる方式を試したが、近接した小さな丸がつながって1つとして検出された。ぼかしは入れず、HoughCircles の minRadius で小さなノイズを除く方針にした。
