# Data Assumptions

## Purpose

This file documents the data assumptions behind the Trash Pandas Connected Reporting Pilot.

The project uses public data where available and synthetic internal-style data where real team system data would normally be required.

The goal is not to claim access to internal Trash Pandas data.

The goal is to show how separate business reports can be connected in Snowflake to support better decisions around game value, promotion performance, fan value, group sales, and follow-up opportunities.

---

## Core Data Principle

This project separates data into three categories:

| Category | Meaning |
|---|---|
| Public | Data collected from public sources |
| Synthetic | Data generated with Python to represent internal-style business records |
| Derived | Metrics created from public and synthetic data through SQL logic |

Every internal-style field must be treated as synthetic unless it comes from a public source.

---

## Public Data Assumptions

Public data can include:

- season
- game date
- opponent
- home/away status
- day of week
- scheduled start time when available
- promotion name
- promotion description
- announced attendance when available

Public data will be used as the external anchor for the project.

---

## Public Data Limitations

Public data is not assumed to be complete, perfectly accurate, or formatted consistently.

Specific limitations:

- Promotion names may change across sources.
- Promotion details may be incomplete.
- Announced attendance does not equal scanned attendance.
- Public attendance may reflect announced attendance, tickets distributed, or another public reporting convention.
- Public sources may not include full game-level revenue, scan, buyer, or fan behavior data.

For this project, public data provides the schedule and context layer. It does not provide the full business performance layer.

---

## Announced Attendance Assumption

Announced attendance is used as a public attendance anchor.

It is not treated as true scanned attendance.

For modeling purposes:

| Field | Meaning |
|---|---|
| announced_attendance | Public attendance figure |
| tickets_sold | Synthetic ticket demand field anchored near public attendance |
| scanned_attendance | Synthetic attendance conversion field |
| no_show_count | Synthetic tickets sold minus synthetic scanned attendance |
| no_show_rate | Synthetic no-show count divided by synthetic tickets sold |

This distinction matters because a game can sell well but still underperform on actual attendance conversion.

---

## Home Game Scope

The current build focuses on Trash Pandas home games only.

Away games are excluded from the main reporting layer because the project is focused on:

- home ticket sales
- home scan behavior
- ballpark attendance
- in-park merch behavior
- in-park concession behavior
- home promotions
- group sales
- follow-up opportunities

Away games do not support the core business questions for this current build.

---

## Season Scope

The current build covers the 2023, 2024, and 2025 seasons.

This multi-season scope supports:

- promotion comparison
- homestand comparison
- repeat fan behavior
- lapsed fan logic
- group account history
- fan value segmentation
- year-over-year context

---

## Homestand Assumption

A homestand is defined as a consecutive block of home games.

Each homestand will receive a manually assigned `homestand_id`.

Example format:

```text
2023_HS_01
2023_HS_02
2024_HS_01
2025_HS_01