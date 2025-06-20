# **System Requirements Specification (SRS)**

## **Integrated Flight Management System (FMS)**

| Document ID: | FMS-SRS-001 |
| :---- | :---- |
| **Version:** | 1.0 |
| **Date:** | June 20, 2025 |
| **Status:** | Baseline |

### **1\. Introduction**

#### **1.1 Purpose**

This document specifies the system requirements for the Integrated Flight Management System (FMS). It establishes the functional, performance, interface, and safety requirements for the system, serving as the foundation for design, development, and validation activities.

#### **1.2 Scope**

The scope of this document covers the entire FMS, including the navigation database, flight planning capabilities, real-time navigation calculations, FMS mode logic, and the flight data display interface. It details the system's integration between its MATLAB/Simulink and Python components.

### **2\. Functional Requirements**

#### **2.1 Navigation Database Management**

| Req. ID | Requirement | Verification |
| :---- | :---- | :---- |
| **FR-1.1** | The system shall use an SQLite database to store and manage navigation data, including waypoints, airways, and procedures. | Test |
| **FR-1.2** | The system shall provide a Python interface to perform Create, Read, Update, and Delete (CRUD) operations on the navigation database. | Test |
| **FR-1.3** | The system shall be capable of finding waypoints by unique identifier. | Test |
| **FR-1.4** | The system shall be capable of finding all waypoints within a specified radius (in nautical miles) of a given latitude/longitude point. | Test |

#### **2.2 Flight Planning**

| Req. ID | Requirement | Verification |
| :---- | :---- | :---- |
| **FR-2.1** | The system shall allow a user to create a flight plan by specifying a departure airport, arrival airport, and a sequence of en-route waypoints or airways. | Test |
| **FR-2.2** | The system shall validate all user-entered waypoints against the navigation database during flight plan creation. | Test |
| **FR-2.3** | The system shall provide the capability to save a created flight plan to persistent storage (JSON file). | Test |
| **FR-2.4** | The system shall provide the capability to load a flight plan from persistent storage. | Test |
| **FR-2.5** | The system shall allow for the live modification of the active flight plan, including inserting and deleting waypoints. | Test |

#### **2.3 Navigation and Guidance**

| Req. ID | Requirement | Verification |
| :---- | :---- | :---- |
| **FR-3.1** | The system shall calculate the aircraft's cross-track error (XTE) from the desired flight path. | Analysis |
| **FR-3.2** | The system shall calculate the distance and bearing to the active waypoint. | Analysis |
| **FR-3.3** | The system shall provide lateral guidance commands (e.g., target bank angle) to maintain the defined flight path. | Test |
| **FR-3.4** | The system shall automatically sequence to the next waypoint in the flight plan upon detection of waypoint passage. | Test |

#### **2.4 FMS Mode Logic**

| Req. ID | Requirement | Verification |
| :---- | :---- | :---- |
| **FR-4.1** | The system shall implement a hierarchical state machine using Stateflow to manage FMS modes. | Inspection |
| **FR-4.2** | The system shall support parallel lateral (e.g., LNAV, HDG) and vertical (e.g., VNAV, ALT) management modes. | Test |
| **FR-4.3** | The system shall manage transitions between armed and active modes based on system state and pilot inputs. | Test |

### **3\. Performance Requirements**

| Req. ID | Requirement | Verification |
| :---- | :---- | :---- |
| **PR-1.1** | The core navigation calculations and guidance loop shall execute at a rate of 50 Hz. | Test |
| **PR-1.2** | The flight data display shall update at a rate of at least 5 Hz. | Test |
| **PR-1.3** | The end-to-end latency from sensor input to guidance command output shall be less than 150 milliseconds. | Test |
| **PR-1.4** | Database queries for a single waypoint shall return in less than 10 milliseconds under normal load. | Test |

### **4\. Interface Requirements**

| Req. ID | Requirement | Verification |
| :---- | :---- | :---- |
| **IR-1.1** | The system shall provide a bridge interface allowing MATLAB/Simulink components to call functions within the Python backend. | Test |
| **IR-1.2** | The Python bridge shall expose functions for all flight planning and navigation database operations. | Inspection |
| **IR-1.3** | Data exchanged between MATLAB and Python shall be converted to compatible types (e.g., Python dict to MATLAB struct). | Test |
| **IR-1.4** | The system shall provide MATLAB App Designer GUIs for flight plan entry, system control, and data display. | Demonstration |

