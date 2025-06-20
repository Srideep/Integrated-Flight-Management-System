
#!/usr/bin/env python3
"""
Interactive test script for MATLAB Python Bridge
"""

import sys
import os

# Add project modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_modules'))

from interfaces.matlab_python_bridge import *

def test_bridge_initialization():
    """Test bridge initialization"""
    print("=== Testing Bridge Initialization ===")
    
    # Initialize bridge
    success = initialize_fms_bridge('data/nav_database/navigation.db')
    if success:
        print("✓ Bridge initialized successfully")
        
        # Test connection
        status = test_bridge_connection()
        print(f"✓ Bridge status: {status['bridge_initialized']}")
        print(f"✓ Available functions: {len(status['available_functions'])}")
        return True
    else:
        print("✗ Bridge initialization failed")
        return False

def test_waypoint_functions():
    """Test waypoint-related functions"""
    print("\n=== Testing Waypoint Functions ===")
    
    # Find specific waypoint
    ksfo = find_waypoint_bridge("KSFO")
    if ksfo:
        print(f"✓ Found KSFO: {ksfo['latitude']}, {ksfo['longitude']}")
    
    # Search waypoints near KSFO
    nearby = search_waypoints_near_bridge(37.6213, -122.3790, 50)
    print(f"✓ Found {len(nearby)} waypoints near KSFO")
    
    # Find airports
    airports = find_waypoints_by_type_bridge("AIRPORT")
    print(f"✓ Found {len(airports)} airports")
    
    # Calculate distance
    distance = calculate_distance_bridge(37.6213, -122.3790, 37.7214, -122.2208)
    print(f"✓ Distance KSFO to KOAK: {distance:.1f} nm")

def test_flight_plan_functions():
    """Test flight plan functions"""
    print("\n=== Testing Flight Plan Functions ===")
    
    # Create flight plan
    success = create_flight_plan_bridge(
        name="TEST_BRIDGE",
        departure="KSFO",
        arrival="KOAK",
        route_list=["SFO"],
        cruise_alt=10000
    )
    
    if success:
        print("✓ Created flight plan TEST_BRIDGE")
        
        # Set as active
        if set_active_flight_plan_bridge("TEST_BRIDGE"):
            print("✓ Set TEST_BRIDGE as active")
            
            # Get current leg
            leg = get_current_leg_bridge()
            if leg:
                print(f"✓ Current leg: {leg['start_waypoint']['identifier']} → {leg['end_waypoint']['identifier']}")
            
            # Get next waypoint
            next_wp = get_next_waypoint_bridge()
            if next_wp:
                print(f"✓ Next waypoint: {next_wp['identifier']}")
        
        # List all plans
        plans = get_all_flight_plans_bridge()
        print(f"✓ Available plans: {plans}")

def test_navigation_aids():
    """Test navigation aid functions"""
    print("\n=== Testing Navigation Aids ===")
    
    # Find alternate airports
    alternates = find_alternate_airports_bridge(37.6213, -122.3790, 50)
    print(f"✓ Found {len(alternates)} alternate airports")
    
    # Find navigation aids
    navaids = find_navigation_aids_bridge(37.6213, -122.3790, 100, "VOR")
    print(f"✓ Found {len(navaids)} VOR stations")
    
    # Validate route
    validation = validate_route_bridge(["KSFO", "SFO", "KOAK"])
    print(f"✓ Route validation: {validation['valid']}")

def run_all_tests():
    """Run all bridge tests"""
    print("Starting MATLAB Python Bridge Tests...\n")
    
    try:
        if not test_bridge_initialization():
            return False
        
        test_waypoint_functions()
        test_flight_plan_functions()
        test_navigation_aids()
        
        print("\n=== All Bridge Tests Completed Successfully ===")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        cleanup_bridge()
        print("Bridge cleaned up")

if __name__ == "__main__":
    run_all_tests()
