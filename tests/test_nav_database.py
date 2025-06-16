
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
