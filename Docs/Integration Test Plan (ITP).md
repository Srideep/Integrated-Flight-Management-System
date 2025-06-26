# **Integration Test Plan (ITP)**

## **Integrated Flight Management System (FMS)**

| Document ID: | FMS-ITP-001 |
| :---- | :---- |
| **Version:** | 1.0 |
| **Date:** | June 20, 2025 |
| **Status:** | Baseline |

### **1\. Introduction**

#### **1.1 Purpose**

This document describes the plan and procedures for conducting integration testing on the Integrated Flight Management System (FMS). The goal of integration testing is to verify the correct functionality of the interfaces between software components and to ensure the system operates as a cohesive whole.

#### **1.2 Scope**

This test plan covers the integration between the MATLAB/Simulink environment and the Python backend. It includes tests for the MATLAB-Python bridge, data flow from the database to the simulation, and the end-to-end flight planning and execution workflow.

### **2\. Test Strategy**

#### **2.1 Approach**

Integration testing will be performed in a bottom-up fashion.

1. **Bridge Interface Testing:** First, the individual functions of the matlab\_python\_bridge will be tested from MATLAB to ensure basic connectivity and data type compatibility.  
2. **Component Interaction Testing:** Next, tests will be conducted to verify the interaction between high-level components (e.g., verifying that the FlightPlanManager can correctly query the NavigationDatabase).  
3. **End-to-End Scenario Testing:** Finally, full workflow scenarios will be executed, simulating a complete flight from planning to landing to validate the entire integrated system.

#### **2.2 Test Environment**

* **Hardware:** A host computer meeting the system requirements specified in the SRS.  
* **Software:** MATLAB R2021b (or later), Python 3.8+, and all required libraries.  
* **Test Scripts:** A combination of MATLAB .m scripts and Python pytest files located in the tests/integration\_tests/ directory.

### **3\. Test Cases**

#### **3.1 Bridge Connectivity and Data Type Tests**

| Test Case ID | Test Description | Expected Result |
| :---- | :---- | :---- |
| **IT-01** | From MATLAB, call initialize\_fms\_bridge(). | The function returns true. Subsequent calls to test\_bridge\_connection() show an initialized state. |
| **IT-02** | From MATLAB, call find\_waypoint\_bridge() for a known waypoint. | A MATLAB struct is returned with the correct waypoint data. |
| **IT-03** | From MATLAB, call get\_current\_leg\_bridge() when no active plan is set. | The function returns an empty value (e.g., \[\] or None). |

#### **3.2 Data Flow and Workflow Tests**

| Test Case ID | Test Description | Expected Result |
| :---- | :---- | :---- |
| **IT-04** | **Create and Activate Plan:** From MATLAB, create a simple flight plan (KSFO-SFO-KOAK). Set it as the active plan. Call get\_current\_leg\_bridge(). | The returned struct shows "KSFO" as the start waypoint and "SFO" as the end waypoint. |
| **IT-05** | **Waypoint Sequencing:** Building on IT-04, call advance\_to\_next\_leg\_bridge(). Then call get\_current\_leg\_bridge() again. | The returned struct now shows "SFO" as the start waypoint and "KOAK" as the end waypoint. |
| **IT-06** | **Live Modification:** Building on IT-05, call insert\_waypoint\_bridge() to insert "WESLA" between SFO and KOAK. Call get\_current\_leg\_bridge(). | The returned struct now shows "SFO" as the start waypoint and "WESLA" as the end waypoint. |

#### **3.3 End-to-End Scenario Tests**

| Test Case ID | Test Description | Expected Result |
| :---- | :---- | :---- |
| **IT-07** | **Full Flight Scenario:** |  |

1. Use the Flight\_Plan\_Entry.mlapp GUI to create a 5-waypoint flight plan.  
2. Save the flight plan to a file.  
3. Clear the system, then load the plan from the file.  
4. Activate the plan.  
5. Run the FMS\_Master\_Model.slx simulation. | 1\. The aircraft correctly sequences through all 5 waypoints.  
6. The Flight\_Data\_Display accurately shows the aircraft's position relative to the flight plan track.  
7. The simulation completes without errors. |

### **4\. Entry and Exit Criteria**

#### **4.1 Entry Criteria**

* All components must have passed their individual unit tests.  
* The test environment must be correctly configured.  
* The software must be built and deployed to the test environment.

#### **4.2 Exit Criteria**

* 100% of all planned integration test cases must be executed.  
* A minimum of 95% of test cases must pass.  
* There shall be no open "Blocker" or "Critical" priority defects.
### **5. Test Automation**

Integration tests are executed using the `run_fms_integration_tests()` script referenced in the README. This harness invokes all MATLAB and Python test components, ensuring the full workflow operates within the performance limits specified.
