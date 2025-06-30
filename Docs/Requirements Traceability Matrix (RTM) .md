# Flight-Management System — Requirements Traceability Matrix (RTM)

| Req ID | Requirement Statement | Design / Doc Reference | Implementation Artefact(s) | Verification Artefact(s) | Verification Method |
|--------|-----------------------|------------------------|----------------------------|--------------------------|---------------------|
| **SYS-REQ-01** | The system shall run the real-time navigation loop at ≥ 4 Hz. | SDD §IV-A, Timing Budget Fig. 4-2 | `Navigation_Loop.slx` (sample rate 0.2 s) | `sim_timing_profile.mlx` | **AN** |
| **NAV-REQ-01** | The system shall ingest GPS latitude, longitude and track angle. | ICD §2.1 (NavigationBus) | `gps_receiver.slx` | `tGPSSensor.m` | **TST** |
| **NAV-REQ-02** | The system shall compute cross-track error (XTE) to the active leg. | SDD §IV-D.2 | `calculate_cross_track_error.m`<br>Simulink block *XTE Calc* | `tCrossTrack.m` | **TST** |
| **NAV-REQ-03** | The system shall compute great-circle distance and initial bearing between two waypoints. | SDD §IV-D.1 | `calculate_distance_bearing.m`<br>Simulink block *Dist/Bearing Calc* | `tDistanceBearing.m` | **TST** |
| **NAV-REQ-04** | The NavigationBus shall publish DistanceNM, BearingDeg, and XTE_NM within 50 ms of input arrival. | ICD §2.2, Signal Timing Table | NavigationBus Simulink lines | `nav_latency_test.mlx` | **DEM** |
| **GDL-REQ-01** | The system shall generate a bank-angle command limited to ±25 deg. | SDD §IV-E | `calculate_bank_angle_cmd.m`<br>Simulink block *Bank Cmd* | `tBankCmd.m` | **TST** |
| **GDL-REQ-02** | With nominal sensors, the closed-loop XTE 99.9-percentile shall be ≤ 0.3 NM (RNP 0.3). | SDD §V-B | `MonteCarloHarness.mlx`<br>`LNAV_6DOF.slx` | `mc_XTE_results.mat` | **AN/TST** |
| **GDL-REQ-03** | Commanded bank angle shall not exceed 30 deg in 99.9 % of Monte-Carlo cases. | SDD §V-B, Fig. 5-3 | Same as above | Same as above | **AN/TST** |
| **UI-REQ-01** | The pilot display shall show XTE with 0.01 NM resolution. | HSI Requirements Doc §3.4 | `HSI_Panel.mlapp` | `ui_render_test.mlx` | **INS** |
| **DOC-REQ-01** | All critical code shall be covered by ≥ 90 % statement coverage via unit tests. | Dev Process Plan §6.3 | All `+test` classes | CI coverage report | **INS** |

**Legend** – Verification Method  
* **AN** – Analysis  * **TST** – Test (unit, integration, HIL, Monte-Carlo, etc.)  
* **DEM** – Demonstration / timing capture  * **INS** – Inspection / review
