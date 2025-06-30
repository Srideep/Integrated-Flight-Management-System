# Interface Control Document (ICD)

> **Document ID:** FMS-ICD-001  **Version:** 1.0  **Date:** 2025-06-30

This document defines the published buses, message topics and timing
budgets for the Integrated Flight Management System.  The interfaces
implement the requirements traced in the RTM (FMS-RTM-001) and are
referenced throughout the SDD and DDD.

## 1. NavigationBus signal list

| Signal        | Type   | Min | Nom | Max | Units | Notes |
|---------------|--------|-----|-----|-----|-------|-------|
| `DistanceNM`  | double | 0   | —   | 20000 | NM | distance to active WP |
| `BearingDeg`  | double | 0   | —   | 360 | deg (true) | bearing to WP |
| `XTE_NM`      | double | -10 | 0   | 10 | NM | + = right of course |
| `BankCmdDeg`  | double | -25 | 0   | 25 | deg | commanded bank angle |

## 2. DatabaseBus (NEW)

Bus carrying on-board database I/O as mapped in the DDD §3.2 channel diagram.
Fields sizes derive from SRS Fig. 6‑3.

| Field        | Type                      | Description |
|--------------|---------------------------|-------------|
| `CVE_Record` | `struct` (ID, score, text) | Common vulnerability entry |
| `SummaryTxt` | `string` ≤ 2 kB           | textual summary in UTF‑8 |
| `QueryStatus`| `enum` {IDLE, BUSY, DONE, ERR} | query state |

## 3. GuidanceBus topic

The former `GuidanceCmd` topic is renamed **GuidanceBus** and contains:

- `BankCmdDeg` – same signal as in NavigationBus
- `TurnRateCmd` (`double`, deg s⁻¹, optional per RTM GDL-REQ-05)

Caller/Callee table:

| Source (caller) | Sink (callee) |
|-----------------|---------------|
| Guidance Law block | AFCS actuator node |

## 4. HSI/EFIS Display lines

One-way publish at 10 Hz of:

- `XTE_NM` with 0.01 NM resolution (RTM UI-REQ-01)
- `BearingDeg` rounded to 1 deg

Documented in Display Interface §4.7.

## 5. Timing budget

| Bus/Topic    | End‑to‑End Budget |
|--------------|------------------|
| NavigationBus| < 50 ms |
| DatabaseBus  | < 50 ms |

## 6. Units & Frames

- Distances expressed in nautical miles with Earth sphere radius
  3440.065 NM.
- Bearings/headings are **true**.
- Bank angle is body‑axis roll, right positive.
- All database text uses UTF‑8.

## 7. Message & topic diagram

- Add **Database Manager** block with its **DatabaseBus** path within the
  Navigation module as shown in the SDD Fig. 5‑4.
- Show **NavigationBus → GuidanceBus → AFCS** as bus names.
- Include HSI subscribed topics.

## 8. Verification cross‑references

| Interface                | ITP Test Case |
|--------------------------|---------------|
| NavigationBus latency    | ITP‑NAV‑05 (`nav_latency_test.mlx`) |
| DatabaseBus overload     | ITP‑DB‑02 (`db_burst_sim.slx`) |

