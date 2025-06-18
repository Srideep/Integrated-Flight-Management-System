
"""
Integration tests for the flight planning system with FlightPlanManager
"""

import sys
import os

# Add project modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from python_modules.flight_planning.flight_plan_manager import FlightPlanManager
from python_modules.nav_database.nav_data_manager import NavigationDatabase

def test_flight_planning():
    """Test the complete flight planning workflow"""
    print("\n=== Testing Flight Planning System ===")
    
    try:
        # 1. Initialize the flight plan manager
        print("1. Initializing Flight Plan Manager...")
        fp_manager = FlightPlanManager('data/nav_database/navigation.db')
        print("   ✓ Flight Plan Manager initialized")
        
        # 2. Test flight plan creation
        print("2. Testing flight plan creation...")
        plan = fp_manager.create_flight_plan(
            name="TEST_INTEGRATION",
            departure="KSFO",
            arrival="KOAK",
            route=["SFO", "FAITH"]
        )
        
        if plan:
            print(f"   ✓ Created flight plan: {plan.name}")
            print(f"   ✓ Route: {plan.departure} → {' → '.join([wp.identifier for wp in plan.waypoints[1:-1]])} → {plan.arrival}")
            print(f"   ✓ Total waypoints: {len(plan.waypoints)}")
        else:
            print("   ✗ Failed to create flight plan")
            return False
        
        # 3. Test setting active plan
        print("3. Testing active plan management...")
        result = fp_manager.set_active_plan(plan)
        if result:
            print("   ✓ Set active flight plan")
        else:
            print("   ✗ Failed to set active plan")
            return False
        
        # 4. Test navigation interface
        print("4. Testing navigation interface...")
        
        # Test current leg
        current_leg = fp_manager.get_current_leg()
        if current_leg:
            start_wp, end_wp = current_leg
            print(f"   ✓ Current leg: {start_wp.identifier} → {end_wp.identifier}")
        else:
            print("   ✗ Failed to get current leg")
            return False
        
        # Test next waypoint
        next_wp = fp_manager.get_next_waypoint()
        if next_wp:
            print(f"   ✓ Next waypoint: {next_wp.identifier}")
        else:
            print("   ✗ Failed to get next waypoint")
            return False
        
        # Test advancing legs
        print("5. Testing waypoint sequencing...")
        leg_count = 0
        while not fp_manager.is_end_of_route():
            result = fp_manager.advance_to_next_leg()
            if result:
                leg_count += 1
                next_wp = fp_manager.get_next_waypoint()
                if next_wp:
                    print(f"   ✓ Advanced to leg {leg_count}, next: {next_wp.identifier}")
                else:
                    print(f"   ✓ Advanced to leg {leg_count}, at end of route")
            else:
                break
        
        print(f"   ✓ Completed {leg_count} leg advances")
        
        # 6. Test flight plan modification
        print("6. Testing flight plan modification...")
        
        # Reset to beginning
        fp_manager.set_active_plan(plan)
        
        # Test waypoint insertion
        result = fp_manager.insert_waypoint("SFO", 1)
        if result:
            print("   ✓ Successfully inserted waypoint")
        else:
            print("   ✗ Failed to insert waypoint")
        
        # Test waypoint modification
        result = fp_manager.modify_waypoint(1, new_altitude=5000)
        if result:
            print("   ✓ Successfully modified waypoint")
        else:
            print("   ✗ Failed to modify waypoint")
        
        # 7. Test file operations
        print("7. Testing file operations...")
        
        # Save flight plan
        filename = "data/flight_plans/TEST_INTEGRATION.json"
        result = fp_manager.save_flight_plan(plan, filename)
        if result:
            print(f"   ✓ Saved flight plan to {filename}")
        else:
            print("   ✗ Failed to save flight plan")
            return False
        
        # Load flight plan
        loaded_plan = fp_manager.load_flight_plan(filename)
        if loaded_plan and loaded_plan.name == plan.name:
            print("   ✓ Successfully loaded flight plan")
        else:
            print("   ✗ Failed to load flight plan")
            return False
        
        # 8. Test status reporting
        print("8. Testing status reporting...")
        status = fp_manager.get_flight_plan_status()
        print(f"   ✓ Status: {status['status']}")
        print(f"   ✓ Plan: {status.get('plan_name', 'None')}")
        print(f"   ✓ Current leg: {status.get('current_leg_index', 'None')}")
        
        print("\n=== Flight Planning Tests PASSED ===")
        return True
        
    except Exception as e:
        print(f"\n✗ Flight planning test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_matlab_bridge_integration():
    """Test MATLAB bridge integration"""
    print("\n=== Testing MATLAB Bridge Integration ===")
    
    try:
        # Import and test the bridge
        from python_modules.interfaces.matlab_python_bridge import (
            initialize_fms_bridge, test_bridge_connection,
            create_flight_plan_bridge, set_active_flight_plan_bridge,
            get_current_leg_bridge, get_next_waypoint_bridge
        )
        
        # Initialize bridge
        print("1. Initializing MATLAB bridge...")
        result = initialize_fms_bridge('data/nav_database/navigation.db')
        if result:
            print("   ✓ Bridge initialized successfully")
        else:
            print("   ✗ Bridge initialization failed")
            return False
        
        # Test connection
        print("2. Testing bridge connection...")
        status = test_bridge_connection()
        if status['bridge_initialized']:
            print("   ✓ Bridge connection successful")
            print(f"   ✓ Available plans: {len(status['available_plans'])}")
        else:
            print("   ✗ Bridge connection failed")
            return False
        
        # Test flight plan creation via bridge
        print("3. Testing flight plan creation via bridge...")
        result = create_flight_plan_bridge(
            name="BRIDGE_TEST",
            departure="KSFO",
            arrival="KOAK",
            route_list=["SFO"]
        )
        if result:
            print("   ✓ Created flight plan via bridge")
        else:
            print("   ✗ Failed to create flight plan via bridge")
            return False
        
        # Test setting active plan via bridge
        print("4. Testing active plan management via bridge...")
        result = set_active_flight_plan_bridge("BRIDGE_TEST")
        if result:
            print("   ✓ Set active plan via bridge")
        else:
            print("   ✗ Failed to set active plan via bridge")
            return False
        
        # Test navigation via bridge
        print("5. Testing navigation via bridge...")
        
        current_leg = get_current_leg_bridge()
        if current_leg:
            print(f"   ✓ Current leg via bridge: {current_leg['start_waypoint']['identifier']} → {current_leg['end_waypoint']['identifier']}")
        else:
            print("   ✗ Failed to get current leg via bridge")
            return False
        
        next_wp = get_next_waypoint_bridge()
        if next_wp:
            print(f"   ✓ Next waypoint via bridge: {next_wp['identifier']}")
        else:
            print("   ✗ Failed to get next waypoint via bridge")
            return False
        
        print("\n=== MATLAB Bridge Tests PASSED ===")
        return True
        
    except Exception as e:
        print(f"\n✗ MATLAB bridge test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run both test suites
    fp_success = test_flight_planning()
    bridge_success = test_matlab_bridge_integration()
    
    if fp_success and bridge_success:
        print("\n🎉 ALL INTEGRATION TESTS PASSED! 🎉")
        exit(0)
    else:
        print("\n❌ SOME TESTS FAILED ❌")
        exit(1)
