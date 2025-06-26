
#!/usr/bin/env python3
"""
FMS Integrated System - Quick Setup Script
Sets up the navigation database and creates sample flight plans
"""

import os
import sys
from python_modules.nav_database.nav_data_manager import NavigationDatabase
from python_modules.flight_planning.flight_plan_manager import FlightPlanManager

def setup_fms_project():
    """Initialize the complete FMS project"""
    print("=== FMS Integrated System Setup ===")
    print()
    
    # 1. Initialize Navigation Database
    print("1. Initializing Navigation Database...")
    try:
        nav_db = NavigationDatabase('data/nav_database/navigation.db')
        print("   ✓ Navigation database created successfully")
        
        # List available waypoints
        waypoints = nav_db.list_all_waypoints()
        print(f"   ✓ Database contains {len(waypoints)} waypoints:")
        for wp in waypoints:
            print(f"     - {wp.identifier} ({wp.waypoint_type}): {wp.latitude:.4f}, {wp.longitude:.4f}")
        nav_db.close()
    except Exception as e:
        print(f"   ✗ Navigation database setup failed: {e}")
        return False
    
    print()
    
    # 2. Create Sample Flight Plans and Test New Features
    print("2. Creating Sample Flight Plans with FlightPlanManager...")
    try:
        fp_manager = FlightPlanManager('data/nav_database/navigation.db')
        
        # Test enhanced waypoint database integration
        print("   Testing enhanced waypoint database features...")
        
        # Find alternate airports near KSFO
        alternates = fp_manager.find_alternate_airports((37.6213, -122.3790), 50)
        print(f"   ✓ Found {len(alternates)} alternate airports within 50nm of KSFO")
        
        # Find navigation aids
        navaids = fp_manager.find_navigation_aids((37.6213, -122.3790), 100, "VOR")
        print(f"   ✓ Found {len(navaids)} VOR navigation aids within 100nm")
        
        # Validate route
        test_route = ["KSFO", "SFO", "KOAK"]
        is_valid, missing = fp_manager.validate_route_waypoints(test_route)
        if is_valid:
            print("   ✓ Route validation: All waypoints found in database")
        else:
            print(f"   ⚠ Route validation: Missing waypoints {missing}")
        
        # Sample flight plan: KSFO to KOAK via SFO VOR
        plan1 = fp_manager.create_flight_plan(
            name="KSFO_KOAK_001",
            departure="KSFO",
            arrival="KOAK",
            route=["SFO"]
        )
        
        if plan1:
            fp_manager.save_flight_plan(plan1, "data/flight_plans/KSFO_KOAK_001.json")
            print("   ✓ Created flight plan: KSFO → SFO → KOAK")
        
        # Sample flight plan: KOAK to KSFO via FAITH
        plan2 = fp_manager.create_flight_plan(
            name="KOAK_KSFO_001", 
            departure="KOAK",
            arrival="KSFO",
            route=["FAITH"]
        )
        
        if plan2:
            fp_manager.save_flight_plan(plan2, "data/flight_plans/KOAK_KSFO_001.json")
            print("   ✓ Created flight plan: KOAK → FAITH → KSFO")
        
        # Test Active Plan Management
        print("   Testing active plan management...")
        fp_manager.set_active_plan(plan1)
        current_leg = fp_manager.get_current_leg()
        if current_leg:
            start, end = current_leg
            print(f"   ✓ Active plan set, current leg: {start.identifier} → {end.identifier}")
        
        # Test Flight Plan Modification
        print("   Testing flight plan modification...")
        original_count = len(fp_manager.active_plan.waypoints)
        fp_manager.insert_waypoint("FAITH", 2)
        new_count = len(fp_manager.active_plan.waypoints)
        if new_count > original_count:
            print("   ✓ Successfully inserted waypoint")
        
        # Test Navigation Sequencing
        print("   Testing navigation sequencing...")
        advances = 0
        while not fp_manager.is_end_of_route() and advances < 5:
            if fp_manager.advance_to_next_leg():
                advances += 1
        print(f"   ✓ Advanced through {advances} legs")
            
    except Exception as e:
        print(f"   ✗ Flight plan creation failed: {e}")
        return False
    
    print()
    
    # 3. Run Tests
    print("3. Running System Tests...")
    
    # Import and run test modules
    sys.path.append('tests')
    from test_nav_database import test_navigation_database
    from test_flight_planning import test_flight_planning
    
    if test_navigation_database():
        print("   ✓ Navigation database tests passed")
    else:
        print("   ✗ Navigation database tests failed")
        return False
        
    if test_flight_planning():
        print("   ✓ Flight planning tests passed")
    else:
        print("   ✗ Flight planning tests failed")
        return False
    
    print()
    print("=== FMS Setup Complete ===")
    print()
    print("Next Steps:")
    print("1. For MATLAB integration, open MATLAB and run:")
    print("   >> cd matlab_modules")
    print("   >> test_matlab_python_bridge")
    print()
    print("2. To test individual components:")
    print("   python tests/test_nav_database.py")
    print("   python tests/test_flight_planning.py")
    print()
    print("3. The navigation database is ready at: data/nav_database/navigation.db")
    print("4. Sample flight plans are saved in: data/flight_plans/")
    
    return True

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("data/nav_database", exist_ok=True)
    os.makedirs("data/flight_plans", exist_ok=True)
    
    success = setup_fms_project()
    sys.exit(0 if success else 1)
