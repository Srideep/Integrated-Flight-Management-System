
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
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from python_modules.flight_planning.flight_plan_manager import FlightPlanManager, FlightPlan

def test_flight_planning():
    """Test flight planning functionality"""
    print("Testing Flight Planning System...")
    
    # Test 1: FlightPlanManager initialization
    try:
        fp_manager = FlightPlanManager()
        print("✓ FlightPlanManager initialization successful")
    except Exception as e:
        print(f"✗ FlightPlanManager initialization failed: {e}")
        return False
    
    # Test 2: Create flight plan
    try:
        plan = fp_manager.create_flight_plan(
            name="TEST_SFO_OAK",
            departure="KSFO",
            arrival="KOAK",
            route=["SFO", "FAITH"]
        )
        
        if plan and plan.name == "TEST_SFO_OAK":
            print(f"✓ Flight plan creation successful: {plan.name}")
            print(f"  - Route has {len(plan.waypoints)} waypoints")
            print(f"  - Departure: {plan.departure}")
            print(f"  - Arrival: {plan.arrival}")
        else:
            print("✗ Flight plan creation failed")
            return False
            
    except Exception as e:
        print(f"✗ Flight plan creation error: {e}")
        return False
    
    # Test 3: Save flight plan
    try:
        saved = fp_manager.save_flight_plan(plan)
        if saved:
            print("✓ Flight plan saved successfully")
        else:
            print("✗ Flight plan save failed")
            return False
    except Exception as e:
        print(f"✗ Flight plan save error: {e}")
        return False
    
    # Test 4: Load flight plan
    try:
        loaded_plan = fp_manager.load_flight_plan("TEST_SFO_OAK")
        if loaded_plan and loaded_plan.name == "TEST_SFO_OAK":
            print("✓ Flight plan loaded successfully")
            print(f"  - Loaded route has {len(loaded_plan.waypoints)} waypoints")
        else:
            print("✗ Flight plan load failed")
            return False
    except Exception as e:
        print(f"✗ Flight plan load error: {e}")
        return False
    
    # Test 5: Invalid flight plan (non-existent waypoints)
    try:
        invalid_plan = fp_manager.create_flight_plan(
            name="INVALID_PLAN",
            departure="INVALID1",
            arrival="INVALID2",
            route=["INVALID3"]
        )
        
        if invalid_plan is None:
            print("✓ Invalid flight plan correctly rejected")
        else:
            print("✗ Invalid flight plan should be rejected")
            return False
    except Exception as e:
        print(f"✗ Invalid flight plan test error: {e}")
        return False
    
    print("All flight planning tests passed!")
    return True

if __name__ == "__main__":
    success = test_flight_planning()
    if not success:
        sys.exit(1)
