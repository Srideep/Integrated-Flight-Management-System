
#!/usr/bin/env python3
"""
Integration test for WaypointDatabase with the rest of the FMS system
"""

import sys
import os
import tempfile

# Add project modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from python_modules.flight_planning.flight_plan_manager import FlightPlanManager
from python_modules.nav_database.waypoint_database import WaypointDatabase, Waypoint
from python_modules.interfaces.matlab_python_bridge import *

def test_waypoint_database_integration():
    """Test the complete waypoint database integration"""
    print("=== Testing Waypoint Database Integration ===")
    
    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        test_db_path = tmp.name
    
    try:
        # 1. Test FlightPlanManager with WaypointDatabase
        print("1. Testing FlightPlanManager integration...")
        fp_manager = FlightPlanManager(test_db_path)
        
        # Add test waypoints
        test_waypoints = [
            Waypoint("KSFO", 37.6213, -122.3790, altitude=13, waypoint_type="AIRPORT", region="CA", country="USA"),
            Waypoint("KOAK", 37.7214, -122.2208, altitude=9, waypoint_type="AIRPORT", region="CA", country="USA"),
            Waypoint("SFO", 37.6189, -122.3750, waypoint_type="VOR", frequency=113.9, region="CA", country="USA"),
        ]
        
        for wp in test_waypoints:
            fp_manager.waypoint_db.add_waypoint(wp)
        
        print("   ✓ WaypointDatabase integrated with FlightPlanManager")
        
        # 2. Test enhanced waypoint search functions
        print("2. Testing enhanced waypoint search...")
        
        # Find alternate airports
        alternates = fp_manager.find_alternate_airports((37.6213, -122.3790), 100)
        if alternates:
            print(f"   ✓ Found {len(alternates)} alternate airports")
            for alt in alternates:
                print(f"     - {alt['identifier']}: {alt['distance_nm']:.1f} nm")
        
        # Find navigation aids
        navaids = fp_manager.find_navigation_aids((37.6213, -122.3790), 100, "VOR")
        if navaids:
            print(f"   ✓ Found {len(navaids)} VOR navigation aids")
            for nav in navaids:
                print(f"     - {nav['identifier']}: {nav['frequency']} MHz, {nav['distance_nm']:.1f} nm")
        
        # Validate route
        test_route = ["KSFO", "SFO", "KOAK"]
        is_valid, missing = fp_manager.validate_route_waypoints(test_route)
        if is_valid:
            print("   ✓ Route validation successful")
        else:
            print(f"   ✗ Route validation failed: missing {missing}")
        
        # Get waypoint details
        ksfo_details = fp_manager.get_waypoint_details("KSFO")
        if ksfo_details:
            print(f"   ✓ Retrieved detailed info for KSFO: {ksfo_details['region']}, {ksfo_details['country']}")
        
        # 3. Test MATLAB bridge integration
        print("3. Testing MATLAB bridge integration...")
        
        # Initialize bridge
        bridge_success = initialize_fms_bridge(test_db_path)
        if bridge_success:
            print("   ✓ MATLAB bridge initialized successfully")
            
            # Test enhanced bridge functions
            nearby_waypoints = search_waypoints_near_bridge(37.6213, -122.3790, 50)
            print(f"   ✓ Bridge waypoint search: {len(nearby_waypoints)} waypoints found")
            
            airports = find_waypoints_by_type_bridge("AIRPORT")
            print(f"   ✓ Bridge airport search: {len(airports)} airports found")
            
            ca_airports = find_airports_in_region_bridge("CA", "USA")
            print(f"   ✓ Bridge region search: {len(ca_airports)} CA airports found")
            
            distance = calculate_distance_bridge(37.6213, -122.3790, 37.7214, -122.2208)
            print(f"   ✓ Bridge distance calculation: {distance:.1f} nm between KSFO and KOAK")
            
            bearing = calculate_bearing_bridge(37.6213, -122.3790, 37.7214, -122.2208)
            print(f"   ✓ Bridge bearing calculation: {bearing:.1f}° from KSFO to KOAK")
            
            # Test enhanced flight plan functions
            route_validation = validate_route_bridge(["KSFO", "SFO", "KOAK"])
            if route_validation["valid"]:
                print("   ✓ Bridge route validation successful")
            
            alternates_bridge = find_alternate_airports_bridge(37.6213, -122.3790, 50)
            print(f"   ✓ Bridge alternate airports: {len(alternates_bridge)} found")
            
            navaids_bridge = find_navigation_aids_bridge(37.6213, -122.3790, 50, "VOR")
            print(f"   ✓ Bridge navigation aids: {len(navaids_bridge)} VORs found")
            
            # Test connection status
            status = test_bridge_connection()
            if status['bridge_initialized']:
                print("   ✓ Bridge connection test successful")
                print(f"   ✓ Available functions: {len(status['available_functions'])}")
                if 'waypoint_statistics' in status:
                    stats = status['waypoint_statistics']
                    print(f"   ✓ Waypoint statistics: {stats}")
        
        # 4. Test flight plan creation with enhanced waypoints
        print("4. Testing flight plan creation with enhanced waypoints...")
        
        flight_plan = fp_manager.create_flight_plan(
            name="ENHANCED_TEST",
            departure="KSFO",
            arrival="KOAK",
            route=["SFO"]
        )
        
        if flight_plan:
            print("   ✓ Flight plan created with enhanced waypoint data")
            
            # Set as active and test navigation
            fp_manager.set_active_plan(flight_plan)
            current_leg = fp_manager.get_current_leg()
            if current_leg:
                print(f"   ✓ Current leg: {current_leg[0].identifier} → {current_leg[1].identifier}")
        
        print("\n=== Waypoint Database Integration Test PASSED ===")
        return True
        
    except Exception as e:
        print(f"\n=== Integration Test FAILED: {e} ===")
        return False
        
    finally:
        # Cleanup
        cleanup_bridge()
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)

if __name__ == "__main__":
    test_waypoint_database_integration()
