
"""
Unit Tests for FlightPlanManager

This module contains comprehensive unit tests for all FlightPlanManager functionality
as required by the FMS Implementation Checklist.
"""

import pytest
import tempfile
import os
import sys
import json

# Add project modules to path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
    )
)

from python_modules.flight_planning.flight_plan_manager import (
    FlightPlanManager, FlightPlan, FlightPlanWaypoint, create_flight_plan_manager
)
from python_modules.nav_database.nav_data_manager import NavigationDatabase, Waypoint

class TestFlightPlanWaypoint:
    """Test FlightPlanWaypoint data structure"""
    
    def test_waypoint_creation(self):
        """Test basic waypoint creation"""
        wp = FlightPlanWaypoint(
            identifier="TEST",
            latitude=37.6189,
            longitude=-122.3750,
            altitude=1000,
            speed=250
        )
        
        assert wp.identifier == "TEST"
        assert wp.latitude == 37.6189
        assert wp.longitude == -122.3750
        assert wp.altitude == 1000
        assert wp.speed == 250
    
    def test_waypoint_to_dict(self):
        """Test waypoint dictionary conversion"""
        wp = FlightPlanWaypoint("TEST", 37.6189, -122.3750, altitude=1000)
        wp_dict = wp.to_dict()
        
        assert wp_dict['identifier'] == "TEST"
        assert wp_dict['latitude'] == 37.6189
        assert wp_dict['longitude'] == -122.3750
        assert wp_dict['altitude'] == 1000
    
    def test_waypoint_from_dict(self):
        """Test waypoint creation from dictionary"""
        wp_dict = {
            'identifier': 'TEST',
            'latitude': 37.6189,
            'longitude': -122.3750,
            'altitude': 1000,
            'speed': 250,
            'waypoint_type': 'VOR'
        }
        
        wp = FlightPlanWaypoint.from_dict(wp_dict)
        
        assert wp.identifier == "TEST"
        assert wp.latitude == 37.6189
        assert wp.waypoint_type == "VOR"

class TestFlightPlan:
    """Test FlightPlan data structure"""
    
    def test_flight_plan_creation(self):
        """Test basic flight plan creation"""
        waypoints = [
            FlightPlanWaypoint("KSFO", 37.6189, -122.3750),
            FlightPlanWaypoint("SFO", 37.6189, -122.3750),
            FlightPlanWaypoint("KOAK", 37.7213, -122.2211)
        ]
        
        plan = FlightPlan(
            name="TEST_PLAN",
            departure="KSFO",
            arrival="KOAK",
            waypoints=waypoints
        )
        
        assert plan.name == "TEST_PLAN"
        assert plan.departure == "KSFO"
        assert plan.arrival == "KOAK"
        assert len(plan.waypoints) == 3
        assert plan.cruise_altitude == 35000  # default
    
    def test_flight_plan_serialization(self):
        """Test flight plan to/from dictionary conversion"""
        waypoints = [
            FlightPlanWaypoint("KSFO", 37.6189, -122.3750),
            FlightPlanWaypoint("KOAK", 37.7213, -122.2211)
        ]
        
        plan = FlightPlan(
            name="SERIALIZE_TEST",
            departure="KSFO",
            arrival="KOAK",
            waypoints=waypoints,
            cruise_altitude=37000
        )
        
        # Convert to dict and back
        plan_dict = plan.to_dict()
        restored_plan = FlightPlan.from_dict(plan_dict)
        
        assert restored_plan.name == plan.name
        assert restored_plan.departure == plan.departure
        assert len(restored_plan.waypoints) == len(plan.waypoints)
        assert restored_plan.waypoints[0].identifier == "KSFO"

class TestFlightPlanManagerCoreState:
    """Test Core State Management (Checklist Section 1)"""
    
    @pytest.fixture
    def manager(self):
        """Create a test flight plan manager"""
        # Use in-memory database for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        # Create and populate test database
        nav_db = NavigationDatabase(db_path)
        test_waypoints = [
            Waypoint("KSFO", 37.6189, -122.3750, "airport"),
            Waypoint("SFO", 37.6189, -122.3750, "VOR"),
            Waypoint("KOAK", 37.7213, -122.2211, "airport"),
            Waypoint("FAITH", 37.6500, -122.2000, "waypoint")
        ]
        
        for wp in test_waypoints:
            nav_db.add_waypoint(wp)
        
        manager = FlightPlanManager(db_path)

        yield manager

        # Cleanup
        try:
            nav_db.close()
            os.unlink(db_path)
        except:
            pass
    
    @pytest.fixture
    def sample_flight_plan(self, manager):
        """Create a sample flight plan for testing"""
        return manager.create_flight_plan(
            name="TEST_PLAN",
            departure="KSFO",
            arrival="KOAK",
            route=["SFO", "FAITH"]
        )
    
    def test_initial_state(self, manager):
        """Test initial manager state"""
        assert manager.active_plan is None
        assert manager.current_leg_index == 0
        assert len(manager.flight_plans) == 0
    
    def test_set_active_plan(self, manager, sample_flight_plan):
        """Test setting active flight plan"""
        result = manager.set_active_plan(sample_flight_plan)
        
        assert result is True
        assert manager.active_plan == sample_flight_plan
        assert manager.current_leg_index == 0
    
    def test_clear_active_plan(self, manager, sample_flight_plan):
        """Test clearing active flight plan"""
        manager.set_active_plan(sample_flight_plan)
        manager.current_leg_index = 2
        
        manager.clear_active_plan()
        
        assert manager.active_plan is None
        assert manager.current_leg_index == 0

class TestFlightPlanManagerNavigation:
    """Test Live Navigation Interface (Checklist Section 2)"""
    
    @pytest.fixture
    def setup_active_plan(self):
        """Setup manager with active plan for navigation testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        nav_db = NavigationDatabase(db_path)
        test_waypoints = [
            Waypoint("KSFO", 37.6189, -122.3750, "airport"),
            Waypoint("SFO", 37.6189, -122.3750, "VOR"),
            Waypoint("FAITH", 37.6500, -122.2000, "waypoint"),
            Waypoint("KOAK", 37.7213, -122.2211, "airport")
        ]
        
        for wp in test_waypoints:
            nav_db.add_waypoint(wp)
        
        manager = FlightPlanManager(db_path)
        flight_plan = manager.create_flight_plan(
            name="NAV_TEST",
            departure="KSFO",
            arrival="KOAK",
            route=["SFO", "FAITH"]
        )
        manager.set_active_plan(flight_plan)
        
        yield manager

        try:
            nav_db.close()
            os.unlink(db_path)
        except:
            pass
    
    def test_get_current_leg(self, setup_active_plan):
        """Test getting current flight leg"""
        manager = setup_active_plan
        
        current_leg = manager.get_current_leg()
        
        assert current_leg is not None
        start_wp, end_wp = current_leg
        assert start_wp.identifier == "KSFO"
        assert end_wp.identifier == "SFO"
    
    def test_get_next_waypoint(self, setup_active_plan):
        """Test getting next waypoint"""
        manager = setup_active_plan
        
        next_wp = manager.get_next_waypoint()
        
        assert next_wp is not None
        assert next_wp.identifier == "SFO"
    
    def test_advance_to_next_leg(self, setup_active_plan):
        """Test advancing to next leg"""
        manager = setup_active_plan
        
        # Initially at leg 0 (KSFO -> SFO)
        assert manager.current_leg_index == 0
        
        result = manager.advance_to_next_leg()
        assert result is True
        assert manager.current_leg_index == 1
        
        # Now should be at leg 1 (SFO -> FAITH)
        current_leg = manager.get_current_leg()
        start_wp, end_wp = current_leg
        assert start_wp.identifier == "SFO"
        assert end_wp.identifier == "FAITH"
    
    def test_end_of_route_handling(self, setup_active_plan):
        """Test end of route detection and handling"""
        manager = setup_active_plan
        
        # Advance to end of route
        while not manager.is_end_of_route():
            manager.advance_to_next_leg()
        
        # Should be at end now
        assert manager.is_end_of_route() is True
        assert manager.get_current_leg() is None
        assert manager.get_next_waypoint() is None
        
        # Try to advance past end
        result = manager.advance_to_next_leg()
        assert result is False
    
    def test_navigation_with_no_active_plan(self):
        """Test navigation methods with no active plan"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        manager = FlightPlanManager(db_path)
        
        assert manager.get_current_leg() is None
        assert manager.get_next_waypoint() is None
        assert manager.advance_to_next_leg() is False
        assert manager.is_end_of_route() is True
        
        os.unlink(db_path)

class TestFlightPlanManagerModification:
    """Test Advanced Flight Planning Features (Checklist Section 3)"""
    
    @pytest.fixture
    def setup_modifiable_plan(self):
        """Setup manager with plan for modification testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        nav_db = NavigationDatabase(db_path)
        test_waypoints = [
            Waypoint("KSFO", 37.6189, -122.3750, "airport"),
            Waypoint("SFO", 37.6189, -122.3750, "VOR"),
            Waypoint("FAITH", 37.6500, -122.2000, "waypoint"),
            Waypoint("KOAK", 37.7213, -122.2211, "airport"),
            Waypoint("INSERT", 37.6000, -122.3000, "waypoint")
        ]
        
        for wp in test_waypoints:
            nav_db.add_waypoint(wp)
        
        manager = FlightPlanManager(db_path)
        flight_plan = manager.create_flight_plan(
            name="MOD_TEST",
            departure="KSFO",
            arrival="KOAK",
            route=["SFO", "FAITH"]
        )
        manager.set_active_plan(flight_plan)
        
        yield manager

        try:
            nav_db.close()
            os.unlink(db_path)
        except:
            pass
    
    def test_insert_waypoint(self, setup_modifiable_plan):
        """Test waypoint insertion"""
        manager = setup_modifiable_plan
        initial_count = len(manager.active_plan.waypoints)
        
        result = manager.insert_waypoint("INSERT", 2)
        
        assert result is True
        assert len(manager.active_plan.waypoints) == initial_count + 1
        assert manager.active_plan.waypoints[2].identifier == "INSERT"
    
    def test_delete_waypoint(self, setup_modifiable_plan):
        """Test waypoint deletion"""
        manager = setup_modifiable_plan
        initial_count = len(manager.active_plan.waypoints)
        
        result = manager.delete_waypoint(1)  # Delete SFO
        
        assert result is True
        assert len(manager.active_plan.waypoints) == initial_count - 1
        # Check that SFO is no longer at position 1
        assert manager.active_plan.waypoints[1].identifier != "SFO"
    
    def test_modify_waypoint(self, setup_modifiable_plan):
        """Test waypoint modification"""
        manager = setup_modifiable_plan
        
        result = manager.modify_waypoint(1, new_altitude=10000, new_speed=300)
        
        assert result is True
        waypoint = manager.active_plan.waypoints[1]
        assert waypoint.altitude == 10000
        assert waypoint.speed == 300
    
    def test_invalid_position_handling(self, setup_modifiable_plan):
        """Test handling of invalid positions"""
        manager = setup_modifiable_plan
        
        # Test invalid positions
        assert manager.insert_waypoint("INSERT", -1) is False
        assert manager.delete_waypoint(999) is False
        assert manager.modify_waypoint(-1, new_altitude=1000) is False
    
    def test_modification_with_no_active_plan(self):
        """Test modifications with no active plan"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        manager = FlightPlanManager(db_path)
        
        assert manager.insert_waypoint("TEST", 0) is False
        assert manager.delete_waypoint(0) is False
        assert manager.modify_waypoint(0, new_altitude=1000) is False
        
        os.unlink(db_path)

class TestFlightPlanManagerFileOperations:
    """Test file operations and persistence"""
    
    @pytest.fixture
    def manager_with_plans(self):
        """Create manager with test flight plans"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        nav_db = NavigationDatabase(db_path)
        test_waypoints = [
            Waypoint("KSFO", 37.6189, -122.3750, "airport"),
            Waypoint("SFO", 37.6189, -122.3750, "VOR"),
            Waypoint("KOAK", 37.7213, -122.2211, "airport")
        ]
        
        for wp in test_waypoints:
            nav_db.add_waypoint(wp)
        
        manager = FlightPlanManager(db_path)
        
        # Create test flight plans
        plan1 = manager.create_flight_plan("PLAN1", "KSFO", "KOAK", ["SFO"])
        plan2 = manager.create_flight_plan("PLAN2", "KOAK", "KSFO", ["SFO"])
        
        yield manager

        try:
            nav_db.close()
            os.unlink(db_path)
        except:
            pass
    
    def test_save_flight_plan(self, manager_with_plans):
        """Test saving flight plan to file"""
        manager = manager_with_plans
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            filename = tmp.name
        
        try:
            plan = manager.flight_plans["PLAN1"]
            result = manager.save_flight_plan(plan, filename)
            
            assert result is True
            assert os.path.exists(filename)
            
            # Verify file content
            with open(filename, 'r') as f:
                data = json.load(f)
            assert data['name'] == "PLAN1"
            
        finally:
            try:
                os.unlink(filename)
            except:
                pass
    
    def test_load_flight_plan(self, manager_with_plans):
        """Test loading flight plan from file"""
        manager = manager_with_plans
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            filename = tmp.name
        
        try:
            # Save a plan first
            plan = manager.flight_plans["PLAN1"]
            manager.save_flight_plan(plan, filename)
            
            # Clear the manager's plans
            manager.flight_plans.clear()
            
            # Load the plan back
            loaded_plan = manager.load_flight_plan(filename)
            
            assert loaded_plan is not None
            assert loaded_plan.name == "PLAN1"
            assert "PLAN1" in manager.flight_plans
            
        finally:
            try:
                os.unlink(filename)
            except:
                pass

class TestFlightPlanManagerStatus:
    """Test status and utility functions"""
    
    def test_get_flight_plan_status_no_active(self):
        """Test status with no active plan"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        manager = FlightPlanManager(db_path)
        status = manager.get_flight_plan_status()
        
        assert status["status"] == "no_active_plan"
        
        os.unlink(db_path)
    
    def test_get_flight_plan_status_active(self):
        """Test status with active plan"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        nav_db = NavigationDatabase(db_path)
        test_waypoints = [
            Waypoint("KSFO", 37.6189, -122.3750, "airport"),
            Waypoint("KOAK", 37.7213, -122.2211, "airport")
        ]
        
        for wp in test_waypoints:
            nav_db.add_waypoint(wp)
        
        manager = FlightPlanManager(db_path)
        plan = manager.create_flight_plan("STATUS_TEST", "KSFO", "KOAK", [])
        manager.set_active_plan(plan)
        
        status = manager.get_flight_plan_status()
        
        assert status["status"] == "active"
        assert status["plan_name"] == "STATUS_TEST"
        assert status["current_leg_index"] == 0
        assert "total_waypoints" in status

        nav_db.close()
        os.unlink(db_path)

class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_route(self):
        """Test creating flight plan with empty route"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        nav_db = NavigationDatabase(db_path)
        nav_db.add_waypoint(Waypoint("KSFO", 37.6189, -122.3750, "airport"))
        nav_db.add_waypoint(Waypoint("KOAK", 37.7213, -122.2211, "airport"))
        
        manager = FlightPlanManager(db_path)
        plan = manager.create_flight_plan("EMPTY_ROUTE", "KSFO", "KOAK", [])
        
        assert plan is not None
        assert len(plan.waypoints) == 2  # Just departure and arrival
        
        nav_db.close()
        os.unlink(db_path)
    
    def test_nonexistent_waypoints(self):
        """Test handling of non-existent waypoints"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        manager = FlightPlanManager(db_path)
        plan = manager.create_flight_plan("BAD_ROUTE", "NOTFOUND", "ALSONOTFOUND", ["MISSING"])
        
        # Should still create plan but with empty waypoints for missing items
        assert plan is not None
        
        os.unlink(db_path)
    
    def test_corrupted_file_handling(self):
        """Test handling of corrupted flight plan files"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        manager = FlightPlanManager(db_path)
        
        # Create corrupted JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_json:
            tmp_json.write("{ corrupted json }")
            corrupted_file = tmp_json.name
        
        try:
            result = manager.load_flight_plan(corrupted_file)
            assert result is None
        finally:
            try:
                os.unlink(corrupted_file)
                os.unlink(db_path)
            except:
                pass

def test_factory_function():
    """Test the factory function"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    manager = create_flight_plan_manager(db_path)
    
    assert isinstance(manager, FlightPlanManager)
    assert manager.nav_db is not None
    
    os.unlink(db_path)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
