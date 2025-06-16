
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
