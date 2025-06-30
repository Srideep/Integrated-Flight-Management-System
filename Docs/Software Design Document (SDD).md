# **Software Design Document (SDD)**

## **Integrated Flight Management System (FMS)**

| Document ID: | FMS-SDD-001 |
| :---- | :---- |
| **Version:** | 1.0 |
| **Date:** | June 20, 2025 |
| **Status:** | Baseline |

### Change Log

| Date | Description |
| ---- | ----------- |
| 2025-06-30 | Updated navigation-calculation and guidance-law references. |

### **1\. Introduction**

#### **1.1 Purpose**

This document provides a detailed description of the software design and architecture for the Integrated Flight Management System (FMS). It elaborates on how the system fulfills the requirements specified in the SRS (FMS-SRS-001) and serves as a guide for developers implementing the software.

#### **1.2 Scope**

This document covers the high-level architecture, component breakdown, data flow, and detailed design of the FMS software. This includes the MATLAB/Simulink real-time components, the Python backend services, the Stateflow mode logic, and the database architecture.

### **2\. System Architecture**

The FMS employs a multi-language, layered architecture to separate concerns and enhance modularity. The system is divided into two primary environments: a MATLAB/Simulink environment for real-time simulation and control, and a Python environment for data management and complex logic.

#### **2.1 Architectural Layers**

The system is organized into four distinct layers:

1. **Interface Layer:** The matlab\_python\_bridge.py module, which serves as the exclusive entry point for MATLAB into the Python backend.  
2. **Core Logic & Managers Layer:** High-level manager classes (FlightPlanManager, NavigationDatabase) that orchestrate the system's primary functions.  
3. **Specialists Layer:** Utility modules with specific, targeted responsibilities (e.g., route\_optimizer, flight\_plan\_storage).  
4. **Data Persistence Layer:** The underlying SQLite databases and JSON flight plan files.

#### **2.2 Component Diagram**

\+-------------------------------------------------------------------+  
|                           MATLAB / Simulink                       |  
|           (Models: Dynamics, Guidance, Navigation, Display)       |  
\+-------------------------------------------------------------------+  
                                  |  
                                  v  
\+-------------------------------------------------------------------+  
|         LAYER 1: INTERFACE (matlab\_python\_bridge.py)              |  
\+-------------------------------------------------------------------+  
                                  |  
                                  v  
\+-------------------------------------------------------------------+  
|         LAYER 2: MANAGERS (flight\_plan\_manager.py, etc.)          |  
\+-------------------------------------------------------------------+  
                                  |  
                                  v  
\+-------------------------------------------------------------------+  
|         LAYER 3: SPECIALISTS (route\_optimizer.py, etc.)           |  
\+-------------------------------------------------------------------+  
                                  |  
                                  v  
\+-------------------------------------------------------------------+  
|         LAYER 4: DATA (SQLite DBs, JSON files)                    |
\+-------------------------------------------------------------------+

### Module Register

| Module No. | Description | Key Files |
| :---- | :---- | :---- |
| 1 | Interface Adapter | `matlab_python_bridge.py` |
| 2 | Flight Planning Manager | `flight_plan_manager.py` |
| 3 | Navigation Calculations | `calculate_distance_bearing.m`, `calculate_cross_track_error.m` |
| 4 | Guidance Law | `calculate_bank_angle_cmd.m` |

### **3\. Component Design**

#### **3.1 MATLAB/Simulink Environment**

* **models/**: Contains all Simulink models.  
  * **FMS\_Master\_Model.slx**: The top-level model that integrates all other Simulink components.  
  * **dynamics/**: Contains the Aircraft\_Dynamics.slx model, which simulates the aircraft's 6-DOF movement.  
  * **navigation/**: Navigation\_Calculations.slx performs real-time calculations (XTE, etc.) by calling into the Python bridge.  
  * **guidance/**: Guidance\_Law.slx computes the necessary commands to steer the aircraft based on navigation outputs.  
  * **display/**: Flight\_Data\_Display.slx visualizes the system's state.  
* **stateflow/**:  
  * **FMS\_Mode\_Logic.sfx**: A Stateflow chart that implements the hierarchical state machine for managing FMS modes as defined in the SRS (FR-4.1, FR-4.2).  
* **apps/**:  
  * Contains the MATLAB App Designer GUIs for user interaction, such as FMS\_Control\_Panel.mlapp and Flight\_Plan\_Entry.mlapp.

#### **3.2 Python Environment (python\_modules/)**

* **interfaces/matlab\_python\_bridge.py**: A procedural module that provides the adapter functions called by MATLAB. It holds global instances of the manager classes to maintain state.  
* **flight\_planning/flight\_plan\_manager.py**: A class-based module that manages the lifecycle of flight plans. It holds the active flight plan in memory, processes modifications, and coordinates with specialist modules.  
* **nav\_database/nav\_data\_manager.py**: A class-based module that abstracts all SQLite database interactions. It provides methods for querying waypoints, airways, and other navigational data. The design uses the Connection Pool pattern to manage database connections efficiently.

### **4\. Data Flow Design**

#### **4.1 Real-Time Navigation Loop**

1. **Simulink (Navigation\_Calculations.slx)** calls get\_current\_leg\_bridge() via the MATLAB Engine.  
2. **Bridge (matlab\_python\_bridge.py)** receives the call and delegates it to the get\_current\_leg() method of its FlightPlanManager instance.  
3. **Manager (flight\_plan\_manager.py)** retrieves the current start and end waypoints from its active\_plan attribute.  
4. The data (as Python Waypoint objects) is returned to the bridge.  
5. **Bridge** converts the Python objects into dictionaries.  
6. **MATLAB Engine** converts the dictionaries into MATLAB structs.  
7. **Simulink** receives the structs and uses them in its navigation calculation blocks.

**Algorithm Overview:** `calculate_distance_bearing` implements the Haversine distance and bearing equations. `calculate_cross_track_error` computes the perpendicular deviation from the leg. `calculate_bank_angle_cmd` converts cross-track error to a bank command using \(\phi_{cmd}=-K\cdot\mathrm{XTE}\) limited by \(\pm\mathrm{MAX\_BANK}\).

```
GPS LLA  -->  distance&bearing  -->  XTE  -->  bank-cmd
```

This entire sequence is designed to complete within the 20ms (50Hz) timeframe specified in the performance requirements (PR-1.1).

### **5. Configuration Parameters**

Runtime parameters for both MATLAB and Python components are centralized for ease of tuning. Key values taken from the README include `BASE_RATE` (50 Hz), `DISPLAY_RATE` (20 Hz), and `DATABASE_PATH` for the navigation database. These parameters allow the system to meet the real-time performance targets and may be adjusted as needed.

### Annex C — Requirements-to-Code Trace Matrix  (excerpt)

| Req ID | Implementation Artefact(s) | Verification Artefact(s) | Notes |
|--------|---------------------------|--------------------------|-------|
| **SYS-REQ-01** | `Navigation_Loop.slx` (sample-time = 0.2 s) | `sim_timing_profile.mlx` | Real-time loop rate ≥ 4 Hz |
| **NAV-REQ-01** | `gps_receiver.slx`  | `tGPSSensor.m` | GPS lat/lon/track ingest |
| **NAV-REQ-02** | `calculate_cross_track_error.m` <br>Simulink block **XTE Calc** | `tCrossTrack.m` | Cross-track error calc |
| **NAV-REQ-03** | `calculate_distance_bearing.m` <br>Simulink block **Dist/Bearing Calc** | `tDistanceBearing.m` | Great-circle distance & bearing |
| **NAV-REQ-04** | NavigationBus wiring in top-level model | `nav_latency_test.mlx` | Publish nav signals ≤ 50 ms |
| **GDL-REQ-01** | `calculate_bank_angle_cmd.m` <br>Simulink block **Bank Cmd** | `tBankCmd.m` | Bank-angle command ±25 deg |
| **GDL-REQ-02** | `LNAV_6DOF.slx`, `MonteCarloHarness.mlx` | `mc_XTE_results.mat` | XTE ≤ 0.3 NM (99.9-percentile) |
| **GDL-REQ-03** | Same as above | `mc_bank_results.mat` | |φ<sub>cmd</sub>| ≤ 30 deg (99.9-percentile) |
| **UI-REQ-01** | `HSI_Panel.mlapp` | `ui_render_test.mlx` | Display XTE @ 0.01 NM |
| **DOC-REQ-01** | All `+test` classes | CI coverage report | ≥ 90 % statement coverage |

*Legend – Verification Method:* **TST** (unit/integration), **AN** (analysis), **DEM** (demonstration), **INS** (inspection).  
(Methods are implicit from the artefact type; list them explicitly if your style guide requires a separate column.)


### **Appendix A – MATLAB Function Listings**

The following functions provide the core navigation algorithms referenced in Section IV‑D. Parameters `K = 5` and `MAX_BANK = 25` degrees inside `calculate_bank_angle_cmd.m` may be tuned as needed.

#### `calculate_distance_bearing.m`

```matlab
function [distance_nm, bearing_deg] = calculate_distance_bearing(lat1_deg, lon1_deg, lat2_deg, lon2_deg)
% CALCULATE_DISTANCE_BEARING Great-circle distance and initial bearing
%
% Implements the Haversine distance and bearing formulas referenced in the
% Real-Time Navigation Loop section of the SDD (FMS-SDD-001) and aligns with
% the NavigationBus definitions in the ICD (FMS-ICD-001).
%
% Inputs are geographic coordinates in degrees. Outputs are distance in
% nautical miles and bearing in degrees.

lat1 = deg2rad(lat1_deg);
lon1 = deg2rad(lon1_deg);
lat2 = deg2rad(lat2_deg);
lon2 = deg2rad(lon2_deg);

dlat = lat2 - lat1;
dlon = lon2 - lon1;
a = sin(dlat/2).^2 + cos(lat1).*cos(lat2).*sin(dlon/2).^2;
c = 2 .* atan2(sqrt(a), sqrt(1-a));

R = 3440.065;

distance_nm = R .* c;

y = sin(dlon) .* cos(lat2);
x = cos(lat1).*sin(lat2) - sin(lat1).*cos(lat2).*cos(dlon);
bearing_rad = atan2(y, x);
bearing_deg = mod(rad2deg(bearing_rad) + 360, 360);
end
```

#### `calculate_cross_track_error.m`

```matlab
function xte_nm = calculate_cross_track_error(lat_deg, lon_deg, start_lat_deg, start_lon_deg, end_lat_deg, end_lon_deg)
% CALCULATE_CROSS_TRACK_ERROR Compute perpendicular distance to a flight leg
%
% Implements the cross-track error equation referenced in the Real-Time
% Navigation Loop of the SDD (FMS-SDD-001). Output units correspond to the
% NavigationBus specification in the ICD (FMS-ICD-001).

lat = deg2rad(lat_deg);
lon = deg2rad(lon_deg);
start_lat = deg2rad(start_lat_deg);
start_lon = deg2rad(start_lon_deg);
end_lat = deg2rad(end_lat_deg);
end_lon = deg2rad(end_lon_deg);

R = 3440.065;

d13 = 2 .* asin( sqrt( sin((lat - start_lat)/2).^2 + ...
                     cos(start_lat).*cos(lat).*sin((lon - start_lon)/2).^2 ) );
bearing13 = atan2( sin(lon - start_lon).*cos(lat), ...
                   cos(start_lat).*sin(lat) - sin(start_lat).*cos(lat).*cos(lon - start_lon) );
bearing12 = atan2( sin(end_lon - start_lon).*cos(end_lat), ...
                   cos(start_lat).*sin(end_lat) - sin(start_lat).*cos(end_lat).*cos(end_lon - start_lon) );

xte_rad = asin( sin(d13) .* sin(bearing13 - bearing12) );
xte_nm = R .* xte_rad;
end
```

#### `calculate_bank_angle_cmd.m`

```matlab
function bank_angle_deg = calculate_bank_angle_cmd(xte_nm, bearing_deg)
% CALCULATE_BANK_ANGLE_CMD Generate a commanded bank angle for LNAV
%
% Converts cross-track error to a bank angle command using a simple
% proportional guidance law referenced in the Real-Time Navigation Loop of
% the SDD (FMS-SDD-001). Output units are in degrees to match the
% NavigationBus specification in the ICD (FMS-ICD-001).

K = 5;           % Gain in degrees per nautical mile
MAX_BANK = 25;   % Saturation limit in degrees

bank_angle_deg = -K .* xte_nm;
bank_angle_deg(bank_angle_deg >  MAX_BANK) =  MAX_BANK;
bank_angle_deg(bank_angle_deg < -MAX_BANK) = -MAX_BANK;
end
```
