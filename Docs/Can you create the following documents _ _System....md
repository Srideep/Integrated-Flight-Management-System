# **Software Design Document (SDD)**

## **Integrated Flight Management System (FMS)**

| Document ID: | FMS-SDD-001 |
| :---- | :---- |
| **Version:** | 1.0 |
| **Date:** | June 20, 2025 |
| **Status:** | Baseline |

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

This entire sequence is designed to complete within the 20ms (50Hz) timeframe specified in the performance requirements (PR-1.1).