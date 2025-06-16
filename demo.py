
#!/usr/bin/env python3
"""
FMS Demo Script - Demonstrates the integrated FMS functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from python_modules.nav_database.nav_data_manager import NavigationDatabase
from python_modules.flight_planning.flight_plan_manager import FlightPlanManager

def demo_navigation_database():
    """Demonstrate navigation database functionality"""
    print("🗄️  Navigation Database Demo")
    print("-" * 40)
    
    # Initialize database
    nav_db = NavigationDatabase()
    print("Database initialized with sample waypoints")
    
    # Show all waypoints
    waypoints = nav_db.list_all_waypoints()
    print(f"\nAvailable waypoints ({len(waypoints)}):")
    for wp in waypoints:
        print(f"  {wp.identifier:8} | {wp.waypoint_type:8} | {wp.latitude:8.4f}°N {wp.longitude:9.4f}°W")
    
    # Demonstrate waypoint lookup
    print(f"\nWaypoint lookup examples:")
    test_waypoints = ['KSFO', 'KOAK', 'SFO', 'INVALID']
    for wp_id in test_waypoints:
        wp = nav_db.find_waypoint(wp_id)
        if wp:
            print(f"  {wp_id}: Found at {wp.latitude:.4f}°N, {wp.longitude:.4f}°W")
        else:
            print(f"  {wp_id}: Not found")
    
    return nav_db

def demo_flight_planning(nav_db):
    """Demonstrate flight planning functionality"""
    print(f"\n✈️  Flight Planning Demo")
    print("-" * 40)
    
    # Initialize flight plan manager
    fp_manager = FlightPlanManager(nav_db)
    print("Flight plan manager initialized")
    
    # Create sample flight plans
    flight_plans = [
        {
            'name': 'SFO_TO_OAK',
            'departure': 'KSFO',
            'arrival': 'KOAK',
            'route': ['SFO'],
            'cruise_alt': 3000,
            'cruise_speed': 250
        },
        {
            'name': 'OAK_TO_SFO_VIA_FAITH',
            'departure': 'KOAK',
            'arrival': 'KSFO',
            'route': ['FAITH', 'SFO'],
            'cruise_alt': 5000,
            'cruise_speed': 280
        }
    ]
    
    created_plans = []
    
    for fp_data in flight_plans:
        print(f"\nCreating flight plan: {fp_data['name']}")
        
        plan = fp_manager.create_flight_plan(
            name=fp_data['name'],
            departure=fp_data['departure'],
            arrival=fp_data['arrival'],
            route=fp_data['route'],
            cruise_alt=fp_data['cruise_alt'],
            cruise_speed=fp_data['cruise_speed']
        )
        
        if plan:
            print(f"  ✓ Created successfully")
            print(f"  ✓ Route: {plan.departure} → {' → '.join([wp.waypoint.identifier for wp in plan.waypoints[1:-1]])} → {plan.arrival}")
            print(f"  ✓ Cruise: {plan.cruise_altitude}ft @ {plan.cruise_speed}kts")
            print(f"  ✓ Waypoints: {len(plan.waypoints)}")
            
            # Save the flight plan
            if fp_manager.save_flight_plan(plan):
                print(f"  ✓ Saved to database")
                created_plans.append(plan.name)
            else:
                print(f"  ✗ Failed to save")
        else:
            print(f"  ✗ Failed to create")
    
    # Demonstrate loading flight plans
    print(f"\nTesting flight plan loading:")
    for plan_name in created_plans:
        loaded_plan = fp_manager.load_flight_plan(plan_name)
        if loaded_plan:
            print(f"  ✓ Loaded {plan_name}: {len(loaded_plan.waypoints)} waypoints")
        else:
            print(f"  ✗ Failed to load {plan_name}")

def main():
    """Main demo function"""
    print("🚀 FMS Integrated System Demo")
    print("=" * 50)
    print("This demo shows the core FMS functionality:")
    print("- Navigation database with waypoints")
    print("- Flight plan creation and management")
    print("- Data persistence and retrieval")
    print("=" * 50)
    
    try:
        # Demo navigation database
        nav_db = demo_navigation_database()
        
        # Demo flight planning
        demo_flight_planning(nav_db)
        
        print(f"\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("- Run 'python run_tests.py' to execute the test suite")
        print("- Check the database files: nav_database.db, flight_plans.db")
        print("- Integrate with MATLAB using the python bridge")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
