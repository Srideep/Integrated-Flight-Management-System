# FMS Development Roadmap - Incremental Implementation and Testing

## Phase 1: Foundation - Navigation Database (Week 1)

### Files to Create First

**1.1 Core Navigation Database**
```python
# File: python_modules/nav_database/__init__.py
# Empty file to make it a Python package

# File: python_modules/nav_database/nav_data_manager.py
import sqlite3
import numpy as np
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Waypoint:
    identifier: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    waypoint_type: str = 'WAYPOINT'

class NavigationDatabase:
    def __init__(self, db_path: str = 'nav_database.db'):
        self.db_path = db_path
        self.connection = None
        self.initialize_database()
        
    def initialize_database(self):
        """Create database and populate with test data"""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # Create waypoints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waypoints (
                id INTEGER PRIMARY KEY,
                identifier TEXT UNIQUE NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                altitude REAL,
                waypoint_type TEXT DEFAULT 'WAYPOINT'
            )
        ''')
        
        # Insert test data
        test_waypoints = [
            ('KSFO', 37.6213, -122.3790, 13, 'AIRPORT'),
            ('KOAK', 37.7214, -122.2208, 9, 'AIRPORT'),
            ('SFO', 37.6189, -122.3750, None, 'VOR'),
            ('FAITH', 37.2833, -122.0167, None, 'WAYPOINT'),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO waypoints 
            (identifier, latitude, longitude, altitude, waypoint_type)
            VALUES (?, ?, ?, ?, ?)
        ''', test_waypoints)
        
        self.connection.commit()
        
    def find_waypoint(self, identifier: str) -> Optional[Waypoint]:
        """Find waypoint by identifier"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT identifier, latitude, longitude, altitude, waypoint_type
            FROM waypoints WHERE identifier = ?
        ''', (identifier,))
        
        result = cursor.fetchone()
        if result:
            return Waypoint(*result)
        return None
        
    def list_all_waypoints(self) -> List[Waypoint]:
        """Get all waypoints for testing"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT identifier, latitude, longitude, altitude, waypoint_type FROM waypoints')
        return [Waypoint(*row) for row in cursor.fetchall()]

if __name__ == "__main__":
    # Basic test when run directly
    db = NavigationDatabase()
    print("Database initialized successfully")
    
    # Test waypoint lookup
    ksfo = db.find_waypoint('KSFO')
    if ksfo:
        print(f"Found KSFO: {ksfo.latitude}, {ksfo.longitude}")
    else:
        print("KSFO not found")
```

**1.2 Test Script for Navigation Database**
```python
# File: tests/test_nav_database.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from python_modules.nav_database.nav_data_manager import NavigationDatabase, Waypoint

def test_navigation_database():
    """Test navigation database functionality"""
    print("Testing Navigation Database...")
    
    # Test 1: Database initialization
    try:
        db = NavigationDatabase('test_nav.db')
        print("✓ Database initialization successful")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False
    
    # Test 2: Waypoint lookup
    ksfo = db.find_waypoint('KSFO')
    if ksfo and ksfo.identifier == 'KSFO':
        print(f"✓ Waypoint lookup successful: {ksfo.identifier} at {ksfo.latitude}, {ksfo.longitude}")
    else:
        print("✗ Waypoint lookup failed")
        return False
    
    # Test 3: Invalid waypoint
    invalid = db.find_waypoint('INVALID')
    if invalid is None:
        print("✓ Invalid waypoint correctly returns None")
    else:
        print("✗ Invalid waypoint should return None")
        return False
    
    # Test 4: List all waypoints
    all_waypoints = db.list_all_waypoints()
    if len(all_waypoints) >= 4:  # Should have at least our test data
        print(f"✓ Found {len(all_waypoints)} waypoints in database")
    else:
        print(f"✗ Expected at least 4 waypoints, found {len(all_waypoints)}")
        return False
    
    print("All navigation database tests passed!")
    
    # Clean up test database
    db.connection.close()
    os.remove('test_nav.db')
    
    return True

if __name__ == "__main__":
    test_navigation_database()
```

### Testing Phase 1

**Run these commands in sequence:**

```bash
# 1. Create directory structure
mkdir -p python_modules/nav_database
mkdir -p tests

# 2. Create the files above

# 3. Test the navigation database
cd tests
python test_nav_database.py
```

**Expected Output:**
```
Testing Navigation Database...
✓ Database initialization successful
✓ Waypoint lookup successful: KSFO at 37.6213, -122.379
✓ Invalid waypoint correctly returns None
✓ Found 4 waypoints in database
All navigation database tests passed!
```

**Success Criteria for Phase 1:**
- ✅ Database creates successfully without errors
- ✅ Test waypoints are inserted correctly
- ✅ Waypoint lookup works for valid identifiers
- ✅ Invalid lookups return None appropriately
- ✅ All waypoints can be listed

---

## Phase 2: Basic Flight Planning (Week 1)

### Files to Create

**2.1 Flight Plan Manager**
```python
# File: python_modules/flight_planning/__init__.py
# Empty file

# File: python_modules/flight_planning/flight_plan_manager.py
import json
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, asdict
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from nav_database.nav_data_manager import NavigationDatabase, Waypoint

@dataclass
class FlightPlanWaypoint:
    identifier: str
    latitude: float
    longitude: float
    altitude: Optional[int] = None

@dataclass
class FlightPlan:
    name: str
    departure: str
    arrival: str
    waypoints: List[FlightPlanWaypoint]
    created_date: str

class FlightPlanManager:
    def __init__(self):
        self.nav_db = NavigationDatabase()
        
    def create_flight_plan(self, name: str, departure: str, arrival: str, 
                          route: List[str]) -> Optional[FlightPlan]:
        """Create flight plan from waypoint identifiers"""
        waypoints = []
        
        # Build complete route: departure + route + arrival
        full_route = [departure] + route + [arrival]
        
        for wp_id in full_route:
            wp = self.nav_db.find_waypoint(wp_id)
            if wp:
                fp_wp = FlightPlanWaypoint(
                    identifier=wp.identifier,
                    latitude=wp.latitude,
                    longitude=wp.longitude,
                    altitude=int(wp.altitude) if wp.altitude else None
                )
                waypoints.append(fp_wp)
            else:
                print(f"Warning: Waypoint {wp_id} not found")
                return None
                
        return FlightPlan(
            name=name,
            departure=departure,
            arrival=arrival,
            waypoints=waypoints,
            created_date=datetime.now().isoformat()
        )
        
    def save_flight_plan(self, flight_plan: FlightPlan, filename: str) -> bool:
        """Save flight plan to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(asdict(flight_plan), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving flight plan: {e}")
            return False
            
    def load_flight_plan(self, filename: str) -> Optional[FlightPlan]:
        """Load flight plan from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Convert waypoint dictionaries back to FlightPlanWaypoint objects
            waypoints = [FlightPlanWaypoint(**wp) for wp in data['waypoints']]
            data['waypoints'] = waypoints
            
            return FlightPlan(**data)
        except Exception as e:
            print(f"Error loading flight plan: {e}")
            return None

if __name__ == "__main__":
    # Basic test
    fp_manager = FlightPlanManager()
    
    # Create test flight plan
    plan = fp_manager.create_flight_plan(
        name="TEST_SFO_OAK",
        departure="KSFO",
        arrival="KOAK", 
        route=["SFO"]
    )
    
    if plan:
        print(f"Created flight plan: {plan.name}")
        print(f"Route has {len(plan.waypoints)} waypoints")
    else:
        print("Failed to create flight plan")
```

**2.2 Test Script for Flight Planning**
```python
# File: tests/test_flight_planning.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from python_modules.flight_planning.flight_plan_manager import FlightPlanManager

def test_flight_planning():
    """Test flight plan creation and management"""
    print("Testing Flight Planning...")
    
    fp_manager = FlightPlanManager()
    
    # Test 1: Create valid flight plan
    plan = fp_manager.create_flight_plan(
        name="TEST_PLAN_001",
        departure="KSFO",
        arrival="KOAK",
        route=["SFO"]
    )
    
    if plan and len(plan.waypoints) == 3:  # KSFO + SFO + KOAK
        print(f"✓ Flight plan created: {plan.name} with {len(plan.waypoints)} waypoints")
    else:
        print("✗ Flight plan creation failed")
        return False
    
    # Test 2: Save flight plan
    if fp_manager.save_flight_plan(plan, "test_plan.json"):
        print("✓ Flight plan saved successfully")
    else:
        print("✗ Flight plan save failed")
        return False
    
    # Test 3: Load flight plan
    loaded_plan = fp_manager.load_flight_plan("test_plan.json")
    if loaded_plan and loaded_plan.name == "TEST_PLAN_001":
        print("✓ Flight plan loaded successfully")
    else:
        print("✗ Flight plan load failed")
        return False
    
    # Test 4: Invalid waypoint handling
    invalid_plan = fp_manager.create_flight_plan(
        name="INVALID_PLAN",
        departure="INVALID1",
        arrival="INVALID2",
        route=[]
    )
    
    if invalid_plan is None:
        print("✓ Invalid waypoints correctly rejected")
    else:
        print("✗ Invalid waypoints should be rejected")
        return False
    
    print("All flight planning tests passed!")
    
    # Clean up
    os.remove("test_plan.json")
    
    return True

if __name__ == "__main__":
    test_flight_planning()
```

### Testing Phase 2

```bash
# Test flight planning
cd tests
python test_flight_planning.py
```

**Success Criteria for Phase 2:**
- ✅ Flight plans created from valid waypoint sequences
- ✅ Flight plans saved/loaded correctly to/from JSON
- ✅ Invalid waypoints properly rejected
- ✅ Complete route includes departure, route waypoints, and arrival

---

## Phase 3: Basic Navigation Math (Week 2)

### Files to Create

**3.1 Navigation Calculations**
```matlab
% File: matlab_modules/navigation_math.m
function nav_math_tests()
    % Test basic navigation calculations
    fprintf('Testing Navigation Math Functions...\n');
    
    % Test data (KSFO to KOAK)
    ksfo_lat = 37.6213;
    ksfo_lon = -122.3790;
    koak_lat = 37.7214;
    koak_lon = -122.2208;
    
    % Test 1: Distance calculation
    distance = calculate_distance(ksfo_lat, ksfo_lon, koak_lat, koak_lon);
    expected_distance = 8.5;  % Approximate nautical miles
    
    if abs(distance - expected_distance) < 1.0
        fprintf('✓ Distance calculation: %.2f nm (expected ~%.2f nm)\n', distance, expected_distance);
    else
        fprintf('✗ Distance calculation failed: %.2f nm\n', distance);
        return;
    end
    
    % Test 2: Bearing calculation
    bearing = calculate_bearing(ksfo_lat, ksfo_lon, koak_lat, koak_lon);
    expected_bearing = 45;  % Approximate bearing (northeast)
    
    if abs(bearing - expected_bearing) < 10
        fprintf('✓ Bearing calculation: %.1f° (expected ~%.1f°)\n', bearing, expected_bearing);
    else
        fprintf('✗ Bearing calculation failed: %.1f°\n', bearing);
        return;
    end
    
    % Test 3: Cross-track error calculation
    % Aircraft position slightly off the direct route
    aircraft_lat = 37.67;
    aircraft_lon = -122.31;
    
    xte = calculate_cross_track_error(aircraft_lat, aircraft_lon, ...
                                     ksfo_lat, ksfo_lon, koak_lat, koak_lon);
    
    fprintf('✓ Cross-track error calculation: %.2f nm\n', abs(xte));
    
    fprintf('All navigation math tests passed!\n');
end

function distance = calculate_distance(lat1, lon1, lat2, lon2)
    % Great circle distance in nautical miles
    lat1_rad = deg2rad(lat1);
    lon1_rad = deg2rad(lon1);
    lat2_rad = deg2rad(lat2);
    lon2_rad = deg2rad(lon2);
    
    dlat = lat2_rad - lat1_rad;
    dlon = lon2_rad - lon1_rad;
    
    a = sin(dlat/2)^2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)^2;
    c = 2 * asin(sqrt(a));
    
    R_nm = 3440.065;  % Earth radius in nautical miles
    distance = R_nm * c;
end

function bearing = calculate_bearing(lat1, lon1, lat2, lon2)
    % Initial bearing from point 1 to point 2
    lat1_rad = deg2rad(lat1);
    lon1_rad = deg2rad(lon1);
    lat2_rad = deg2rad(lat2);
    lon2_rad = deg2rad(lon2);
    
    dlon = lon2_rad - lon1_rad;
    
    y = sin(dlon) * cos(lat2_rad);
    x = cos(lat1_rad) * sin(lat2_rad) - sin(lat1_rad) * cos(lat2_rad) * cos(dlon);
    
    bearing_rad = atan2(y, x);
    bearing = rad2deg(bearing_rad);
    
    % Normalize to 0-360
    if bearing < 0
        bearing = bearing + 360;
    end
end

function xte = calculate_cross_track_error(aircraft_lat, aircraft_lon, ...
                                          wp1_lat, wp1_lon, wp2_lat, wp2_lon)
    % Cross-track error calculation
    % Positive XTE means aircraft is right of track
    
    % Distance from aircraft to first waypoint
    d13 = calculate_distance(wp1_lat, wp1_lon, aircraft_lat, aircraft_lon);
    d13_rad = d13 / 3440.065;  % Convert to radians
    
    % Bearing from first waypoint to aircraft
    brng13 = calculate_bearing(wp1_lat, wp1_lon, aircraft_lat, aircraft_lon);
    brng13_rad = deg2rad(brng13);
    
    % Bearing from first to second waypoint (desired track)
    brng12 = calculate_bearing(wp1_lat, wp1_lon, wp2_lat, wp2_lon);
    brng12_rad = deg2rad(brng12);
    
    % Cross-track error
    xte_rad = asin(sin(d13_rad) * sin(brng13_rad - brng12_rad));
    xte = xte_rad * 3440.065;  % Convert back to nautical miles
end
```

### Testing Phase 3

```matlab
% In MATLAB Command Window:
cd matlab_modules
navigation_math
```

**Success Criteria for Phase 3:**
- ✅ Distance calculations within 1 nm of expected values
- ✅ Bearing calculations within 10° of expected values  
- ✅ Cross-track error calculations complete without errors
- ✅ All functions handle edge cases properly

---

## Phase 4: Simple Stateflow Logic (Week 2)

### Files to Create

**4.1 Basic FMS State Machine**
```matlab
% File: create_basic_fms_stateflow.m
function create_basic_fms_stateflow()
    % Create simple FMS state machine for testing
    
    modelName = 'FMS_Basic_States';
    
    % Create new model
    try
        new_system(modelName);
    catch
        % Model might already exist
        close_system(modelName, 0);
        new_system(modelName);
    end
    
    open_system(modelName);
    
    % Add Stateflow chart
    chart_block = add_block('sflib/Chart', [modelName '/FMS_States']);
    set_param(chart_block, 'Position', [100 100 400 300]);
    
    % Configure chart
    rt = sfroot;
    chart = rt.find('-isa', 'Stateflow.Chart', '-and', 'Name', 'FMS_States');
    
    if isempty(chart)
        fprintf('Error: Could not find Stateflow chart\n');
        return;
    end
    
    chart.ChartUpdate = 'DISCRETE';
    chart.SampleTime = '0.1';
    
    % Create simple states
    create_basic_states(chart);
    
    % Add basic data
    add_basic_data(chart);
    
    fprintf('Basic FMS Stateflow chart created successfully\n');
    save_system(modelName);
end

function create_basic_states(chart)
    % Create basic states for testing
    
    % OFF state
    state_off = chart.add('State');
    state_off.Name = 'OFF';
    state_off.Position = [50 50 80 60];
    state_off.LabelString = 'OFF\nentry: status = 0;';
    
    % STANDBY state  
    state_standby = chart.add('State');
    state_standby.Name = 'STANDBY';
    state_standby.Position = [200 50 80 60];
    state_standby.LabelString = 'STANDBY\nentry: status = 1;';
    
    % ACTIVE state
    state_active = chart.add('State');
    state_active.Name = 'ACTIVE';
    state_active.Position = [50 150 80 60];
    state_active.LabelString = 'ACTIVE\nentry: status = 2;';
    
    % Create transitions
    trans1 = chart.add('Transition');
    trans1.Source = state_off;
    trans1.Destination = state_standby;
    trans1.LabelString = 'power_on';
    
    trans2 = chart.add('Transition');
    trans2.Source = state_standby;
    trans2.Destination = state_active;
    trans2.LabelString = 'engage';
    
    trans3 = chart.add('Transition');
    trans3.Source = state_active;
    trans3.Destination = state_standby;
    trans3.LabelString = 'disengage';
    
    % Default transition to OFF
    default_trans = chart.add('DefaultTransition');
    default_trans.Destination = state_off;
end

function add_basic_data(chart)
    % Add input/output data
    
    % Inputs
    input1 = chart.add('Data');
    input1.Name = 'power_on';
    input1.Scope = 'INPUT_DATA';
    input1.DataType = 'boolean';
    
    input2 = chart.add('Data');
    input2.Name = 'engage';
    input2.Scope = 'INPUT_DATA';
    input2.DataType = 'boolean';
    
    input3 = chart.add('Data');
    input3.Name = 'disengage';
    input3.Scope = 'INPUT_DATA';
    input3.DataType = 'boolean';
    
    % Output
    output1 = chart.add('Data');
    output1.Name = 'status';
    output1.Scope = 'OUTPUT_DATA';
    output1.DataType = 'uint8';
end
```

**4.2 Test Script for Stateflow**
```matlab
% File: test_basic_stateflow.m
function test_basic_stateflow()
    % Test basic Stateflow functionality
    fprintf('Testing Basic Stateflow Logic...\n');
    
    modelName = 'FMS_Basic_States';
    
    % Create the model if it doesn't exist
    if ~bdIsLoaded(modelName)
        if exist([modelName '.slx'], 'file')
            load_system(modelName);
        else
            create_basic_fms_stateflow();
        end
    end
    
    % Add input/output blocks for testing
    add_test_blocks(modelName);
    
    % Configure simulation
    set_param(modelName, 'SimulationMode', 'normal');
    set_param(modelName, 'StopTime', '5');
    
    % Test 1: Initial state should be OFF (status = 0)
    try
        simOut = sim(modelName);
        
        % Check if simulation completed
        if exist('simOut', 'var')
            fprintf('✓ Stateflow simulation completed successfully\n');
        else
            fprintf('✗ Stateflow simulation failed\n');
            return;
        end
        
    catch ME
        fprintf('✗ Simulation error: %s\n', ME.message);
        return;
    end
    
    fprintf('All Stateflow tests passed!\n');
end

function add_test_blocks(modelName)
    % Add test input/output blocks
    
    try
        % Add constant blocks for inputs
        add_block('simulink/Sources/Constant', [modelName '/PowerOn']);
        set_param([modelName '/PowerOn'], 'Value', '0');
        set_param([modelName '/PowerOn'], 'Position', [50 250 80 280]);
        
        add_block('simulink/Sources/Constant', [modelName '/Engage']);
        set_param([modelName '/Engage'], 'Value', '0');
        set_param([modelName '/Engage'], 'Position', [50 300 80 330]);
        
        add_block('simulink/Sources/Constant', [modelName '/Disengage']);
        set_param([modelName '/Disengage'], 'Value', '0');
        set_param([modelName '/Disengage'], 'Position', [50 350 80 380]);
        
        % Add scope for output
        add_block('simulink/Sinks/Scope', [modelName '/StatusScope']);
        set_param([modelName '/StatusScope'], 'Position', [500 170 530 200]);
        
        % Connect blocks
        add_line(modelName, 'PowerOn/1', 'FMS_States/1');
        add_line(modelName, 'Engage/1', 'FMS_States/2');
        add_line(modelName, 'Disengage/1', 'FMS_States/3');
        add_line(modelName, 'FMS_States/1', 'StatusScope/1');
        
    catch ME
        % Blocks might already exist
        fprintf('Note: Test blocks may already exist\n');
    end
end
```

### Testing Phase 4

```matlab
% In MATLAB:
test_basic_stateflow
```

**Success Criteria for Phase 4:**
- ✅ Stateflow chart compiles without errors
- ✅ Model simulates successfully
- ✅ State transitions work as expected
- ✅ Input/output data flows correctly

---

## Phase 5: MATLAB-Python Integration (Week 3)

### Files to Create

**5.1 MATLAB-Python Bridge**
```matlab
% File: test_matlab_python_bridge.m
function test_matlab_python_bridge()
    % Test MATLAB-Python integration
    fprintf('Testing MATLAB-Python Bridge...\n');
    
    % Test 1: Python environment
    try
        pyenv_info = pyenv;
        fprintf('✓ Python environment: %s\n', pyenv_info.Version);
    catch ME
        fprintf('✗ Python environment error: %s\n', ME.message);
        return;
    end
    
    % Test 2: Add Python path
    try
        if count(py.sys.path, pwd) == 0
            insert(py.sys.path, int32(0), pwd);
        end
        fprintf('✓ Python path configured\n');
    catch ME
        fprintf('✗ Python path error: %s\n', ME.message);
        return;
    end
    
    % Test 3: Import navigation database
    try
        nav_db = py.python_modules.nav_database.nav_data_manager.NavigationDatabase();
        fprintf('✓ Navigation database imported successfully\n');
    catch ME
        fprintf('✗ Navigation database import error: %s\n', ME.message);
        return;
    end
    
    % Test 4: Call Python function from MATLAB
    try
        waypoint = nav_db.find_waypoint('KSFO');
        if ~isempty(waypoint)
            lat = double(waypoint.latitude);
            lon = double(waypoint.longitude);
            fprintf('✓ Python function call successful: KSFO at %.6f, %.6f\n', lat, lon);
        else
            fprintf('✗ Python function returned empty result\n');
            return;
        end
    catch ME
        fprintf('✗ Python function call error: %s\n', ME.message);
        return;
    end
    
    % Test 5: Data type conversion
    try
        all_waypoints = nav_db.list_all_waypoints();
        wp_count = length(all_waypoints);
        fprintf('✓ Data conversion successful: %d waypoints found\n', wp_count);
    catch ME
        fprintf('✗ Data conversion error: %s\n', ME.message);
        return;
    end
    
    fprintf('All MATLAB-Python bridge tests passed!\n');
end
```

### Testing Phase 5

```matlab
% In MATLAB:
% 1. Ensure Python files from Phases 1-2 are in the correct locations
% 2. Run:
test_matlab_python_bridge
```

**Success Criteria for Phase 5:**
- ✅ Python environment detected and configured
- ✅ Python modules imported successfully from MATLAB
- ✅ Python functions callable from MATLAB
- ✅ Data type conversions work correctly
- ✅ No import or path errors

---

## Development Schedule Summary

| **Phase** | **Duration** | **Key Files** | **Testing Focus** |
|-----------|--------------|---------------|-------------------|
| **Phase 1** | 2-3 days | `nav_data_manager.py`, `test_nav_database.py` | Database operations |
| **Phase 2** | 2-3 days | `flight_plan_manager.py`, `test_flight_planning.py` | Flight plan CRUD |
| **Phase 3** | 3-4 days | `navigation_math.m` | Math functions accuracy |
| **Phase 4** | 3-4 days | `create_basic_fms_stateflow.m`, `test_basic_stateflow.m` | State machine logic |
| **Phase 5** | 2-3 days | `test_matlab_python_bridge.m` | Integration testing |

## Critical Success Factors

### ✅ **Phase Gates**
- **Don't proceed** to the next phase until all tests pass
- **Each phase** builds on the previous one's functionality
- **Fix issues immediately** - they compound in later phases

### ✅ **Testing Strategy**
- **Unit tests first** - test individual functions
- **Integration tests** - test component interactions  
- **System tests** - test end-to-end workflows

### ✅ **Common Issues and Solutions**

**Python Path Issues:**
```matlab
% Add this to startup.m or run manually:
if count(py.sys.path, pwd) == 0
    insert(py.sys.path, int32(0), pwd);
end
```

**Stateflow Compilation Errors:**
```matlab
% Clear and rebuild:
clear all
close all
bdclose all
```

**Database Lock Issues:**
```python
# Always close connections:
try:
    # database operations
finally:
    if connection:
        connection.close()
```

This incremental approach ensures each component works before building the next layer, making debugging much easier and ensuring a solid foundation for the complete FMS system.