# **Interface Control Document (ICD)**

## **Integrated Flight Management System (FMS)**

| Document ID: | FMS-ICD-001 |
| :---- | :---- |
| **Version:** | 1.0 |
| **Date:** | June 20, 2025 |
| **Status:** | Baseline |

### **1\. Introduction**

#### **1.1 Purpose**

This Interface Control Document (ICD) defines the interface between the MATLAB/Simulink environment and the Python backend of the Integrated Flight Management System (FMS). It provides a precise contract for data exchange, function signatures, and data structures, ensuring stable and reliable communication between the two components.

#### **1.2 Scope**

This document details every function exposed by the matlab\_python\_bridge.py module, including its input parameters, return values, and their corresponding data types in both Python and MATLAB. It also defines the structure of key Simulink Buses used for data transmission.

### **2\. MATLAB-to-Python Interface**

This section details the functions available in matlab\_python\_bridge.py that can be called from the MATLAB environment.

#### **2.1 Initialization**

**initialize\_fms\_bridge()**

* **Description:** Initializes the bridge, creating instances of the Python managers. Must be called before any other bridge function.  
* **Python Signature:** initialize\_fms\_bridge() \-\> bool  
* **MATLAB Call:** status \= py.interfaces.matlab\_python\_bridge.initialize\_fms\_bridge();  
* **Return (MATLAB):** logical (true on success, false on failure).

#### **2.2 Flight Plan Management**

**create\_flight\_plan\_bridge()**

* **Description:** Creates a new flight plan from a list of waypoint identifiers.  
* **Python Signature:** create\_flight\_plan\_bridge(name: str, departure: str, arrival: str, route\_list: List\[str\]) \-\> bool  
* **MATLAB Call:** status \= py.interfaces.matlab\_python\_bridge.create\_flight\_plan\_bridge('MyPlan', 'KSFO', 'KOAK', {'SFO'});  
* **Return (MATLAB):** logical (true on success).

**get\_current\_leg\_bridge()**

* **Description:** Retrieves the start and end waypoints of the currently active flight leg. Called every simulation step.  
* **Python Signature:** get\_current\_leg\_bridge() \-\> Optional\[Dict\[str, Any\]\]  
* **MATLAB Call:** leg\_struct \= py.interfaces.matlab\_python\_bridge.get\_current\_leg\_bridge();  
* **Return (MATLAB):** struct with the following fields:  
  * start\_waypoint (struct: identifier, latitude, longitude, altitude)  
  * end\_waypoint (struct: identifier, latitude, longitude, altitude)  
  * leg\_index (double)

**advance\_to\_next\_leg\_bridge()**

* **Description:** Instructs the flight plan manager to sequence to the next leg.  
* **Python Signature:** advance\_to\_next\_leg\_bridge() \-\> bool  
* **MATLAB Call:** status \= py.interfaces.matlab\_python\_bridge.advance\_to\_next\_leg\_bridge();  
* **Return (MATLAB):** logical (true if successful, false if at end of route).

*(This section would continue for all 21+ functions in the bridge, detailing each one explicitly.)*

### **3\. Simulink Bus Definitions**

This section defines the structure of the primary Simulink buses used to pass data within the simulation models.

#### **3.1 PositionBus**

* **Description:** Contains the aircraft's current position information.  
* **Source:** Aircraft\_Dynamics.slx  
* Elements:  
  | Element Name | Data Type | Units | Description |  
  | :--- | :--- | :--- | :--- |  
  | Latitude | double | degrees | Geodetic Latitude |  
  | Longitude | double | degrees | Geodetic Longitude |  
  | Altitude | double | feet | Altitude above mean sea level |

#### **3.2 NavigationBus**

* **Description:** Contains the output of the navigation and guidance calculations.  
* **Source:** Navigation\_Calculations.slx  
* Elements:  
  | Element Name | Data Type | Units | Description |  
  | :--- | :--- | :--- | :--- |  
  | CrossTrackError | double | nautical miles | Perpendicular distance from track |  
  | DistanceToGo | double | nautical miles | Distance to active waypoint |  
  | DesiredCourse | double | degrees | Bearing to active waypoint |  
  | BankAngleCmd | double | degrees | Commanded bank angle for LNAV |

#### **3.3 FMSModeBus**

* **Description:** Contains the current status of the FMS modes.  
* **Source:** FMS\_Mode\_Logic.sfx  
* Elements:  
  | Element Name | Data Type | Units | Description |  
  | :--- | :--- | :--- | :--- |  
  | ActiveLateralMode | Enum: FMSLatMode | N/A | (e.g., LNAV, HDG, NAV) |  
  | ActiveVerticalMode | Enum: FMSVertMode | N/A | (e.g., VNAV, ALT, VS) |  
  | ArmedLateralMode | Enum: FMSLatMode | N/A | Armed lateral mode |