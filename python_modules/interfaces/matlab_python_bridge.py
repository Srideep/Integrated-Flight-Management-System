
"""
MATLAB-Python Bridge for Flight Management System Integration

This module provides the interface between MATLAB/Simulink and the Python
flight planning and navigation database components.
"""

import sys
import os
import json
import logging
from typing import Optional, List, Dict, Any, Tuple

# Add project modules to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flight_planning.flight_plan_manager import FlightPlanManager, FlightPlan
from nav_database.nav_data_manager import NavigationDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances for MATLAB integration
_flight_plan_manager: Optional[FlightPlanManager] = None
_nav_database: Optional[NavigationDatabase] = None

def initialize_fms_bridge(nav_db_path: str = "data/nav_database/navigation.db") -> bool:
    """Initialize the FMS bridge with navigation database and flight plan manager"""
    global _flight_plan_manager, _nav_database
    
    try:
        _nav_database = NavigationDatabase(nav_db_path)
        _flight_plan_manager = FlightPlanManager(nav_db_path)
        logger.info("FMS bridge initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize FMS bridge: {e}")
        return False

# ============================================================================
# NAVIGATION DATABASE INTERFACE FUNCTIONS
# ============================================================================

def find_waypoint_bridge(waypoint_id: str) -> Optional[Dict[str, Any]]:
    """Find waypoint and return as dictionary for MATLAB"""
    if not _nav_database:
        logger.error("Navigation database not initialized")
        return None
    
    waypoint = _nav_database.find_waypoint(waypoint_id)
    if waypoint:
        return {
            'identifier': waypoint.identifier,
            'latitude': waypoint.latitude,
            'longitude': waypoint.longitude,
            'waypoint_type': waypoint.waypoint_type
        }
    return None

def search_waypoints_near_bridge(lat: float, lon: float, radius_nm: float = 50.0) -> List[Dict[str, Any]]:
    """Search for waypoints near a position"""
    if not _nav_database:
        return []
    
    waypoints = _nav_database.search_waypoints_near(lat, lon, radius_nm)
    return [
        {
            'identifier': wp.identifier,
            'latitude': wp.latitude,
            'longitude': wp.longitude,
            'waypoint_type': wp.waypoint_type,
            'distance_nm': wp.distance_nm if hasattr(wp, 'distance_nm') else 0.0
        }
        for wp in waypoints
    ]

# ============================================================================
# FLIGHT PLAN CREATION INTERFACE
# ============================================================================

def create_flight_plan_bridge(name: str, departure: str, arrival: str, 
                            route_list: List[str], cruise_alt: int = 35000) -> bool:
    """Create flight plan via bridge interface"""
    if not _flight_plan_manager:
        logger.error("Flight plan manager not initialized")
        return False
    
    flight_plan = _flight_plan_manager.create_flight_plan(
        name=name,
        departure=departure,
        arrival=arrival,
        route=route_list,
        cruise_alt=cruise_alt
    )
    
    return flight_plan is not None

def save_flight_plan_bridge(plan_name: str, filename: str = None) -> bool:
    """Save flight plan to file"""
    if not _flight_plan_manager or plan_name not in _flight_plan_manager.flight_plans:
        return False
    
    flight_plan = _flight_plan_manager.flight_plans[plan_name]
    return _flight_plan_manager.save_flight_plan(flight_plan, filename)

def load_flight_plan_bridge(filename: str) -> bool:
    """Load flight plan from file"""
    if not _flight_plan_manager:
        return False
    
    flight_plan = _flight_plan_manager.load_flight_plan(filename)
    return flight_plan is not None

# ============================================================================
# ACTIVE FLIGHT PLAN MANAGEMENT
# ============================================================================

def set_active_flight_plan_bridge(plan_name: str) -> bool:
    """Set active flight plan by name"""
    if not _flight_plan_manager or plan_name not in _flight_plan_manager.flight_plans:
        logger.error(f"Flight plan {plan_name} not found")
        return False
    
    flight_plan = _flight_plan_manager.flight_plans[plan_name]
    return _flight_plan_manager.set_active_plan(flight_plan)

def clear_active_flight_plan_bridge() -> bool:
    """Clear the active flight plan"""
    if not _flight_plan_manager:
        return False
    
    _flight_plan_manager.clear_active_plan()
    return True

# ============================================================================
# REAL-TIME NAVIGATION INTERFACE FOR SIMULINK
# ============================================================================

def get_current_leg_bridge() -> Optional[Dict[str, Any]]:
    """Get current flight leg information"""
    if not _flight_plan_manager:
        return None
    
    current_leg = _flight_plan_manager.get_current_leg()
    if current_leg:
        start_wp, end_wp = current_leg
        return {
            'start_waypoint': {
                'identifier': start_wp.identifier,
                'latitude': start_wp.latitude,
                'longitude': start_wp.longitude,
                'altitude': start_wp.altitude
            },
            'end_waypoint': {
                'identifier': end_wp.identifier,
                'latitude': end_wp.latitude,
                'longitude': end_wp.longitude,
                'altitude': end_wp.altitude
            },
            'leg_index': _flight_plan_manager.current_leg_index
        }
    return None

def get_next_waypoint_bridge() -> Optional[Dict[str, Any]]:
    """Get next waypoint information"""
    if not _flight_plan_manager:
        return None
    
    next_wp = _flight_plan_manager.get_next_waypoint()
    if next_wp:
        return {
            'identifier': next_wp.identifier,
            'latitude': next_wp.latitude,
            'longitude': next_wp.longitude,
            'altitude': next_wp.altitude,
            'speed': next_wp.speed,
            'waypoint_type': next_wp.waypoint_type
        }
    return None

def advance_to_next_leg_bridge() -> bool:
    """Advance to next leg (called when waypoint passage detected)"""
    if not _flight_plan_manager:
        return False
    
    return _flight_plan_manager.advance_to_next_leg()

def is_end_of_route_bridge() -> bool:
    """Check if at end of route"""
    if not _flight_plan_manager:
        return True
    
    return _flight_plan_manager.is_end_of_route()

def get_flight_plan_status_bridge() -> Dict[str, Any]:
    """Get comprehensive flight plan status"""
    if not _flight_plan_manager:
        return {"status": "not_initialized"}
    
    return _flight_plan_manager.get_flight_plan_status()

# ============================================================================
# FLIGHT PLAN MODIFICATION INTERFACE
# ============================================================================

def insert_waypoint_bridge(wp_id: str, position: int) -> bool:
    """Insert waypoint into active flight plan"""
    if not _flight_plan_manager:
        return False
    
    return _flight_plan_manager.insert_waypoint(wp_id, position)

def delete_waypoint_bridge(position: int) -> bool:
    """Delete waypoint from active flight plan"""
    if not _flight_plan_manager:
        return False
    
    return _flight_plan_manager.delete_waypoint(position)

def modify_waypoint_bridge(position: int, new_altitude: int = None, 
                          new_speed: int = None) -> bool:
    """Modify waypoint in active flight plan"""
    if not _flight_plan_manager:
        return False
    
    return _flight_plan_manager.modify_waypoint(position, new_altitude, new_speed)

def optimize_active_plan_bridge() -> bool:
    """Optimize the active flight plan"""
    if not _flight_plan_manager:
        return False
    
    return _flight_plan_manager.optimize_active_plan()

# ============================================================================
# UTILITY FUNCTIONS FOR MATLAB
# ============================================================================

def get_all_flight_plans_bridge() -> List[str]:
    """Get list of all available flight plan names"""
    if not _flight_plan_manager:
        return []
    
    return list(_flight_plan_manager.flight_plans.keys())

def get_flight_plan_info_bridge(plan_name: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a specific flight plan"""
    if not _flight_plan_manager or plan_name not in _flight_plan_manager.flight_plans:
        return None
    
    flight_plan = _flight_plan_manager.flight_plans[plan_name]
    return {
        'name': flight_plan.name,
        'departure': flight_plan.departure,
        'arrival': flight_plan.arrival,
        'waypoint_count': len(flight_plan.waypoints),
        'cruise_altitude': flight_plan.cruise_altitude,
        'cruise_speed': flight_plan.cruise_speed,
        'waypoints': [
            {
                'identifier': wp.identifier,
                'latitude': wp.latitude,
                'longitude': wp.longitude,
                'altitude': wp.altitude,
                'waypoint_type': wp.waypoint_type
            }
            for wp in flight_plan.waypoints
        ]
    }

def test_bridge_connection() -> Dict[str, Any]:
    """Test the bridge connection and return system status"""
    return {
        'bridge_initialized': _flight_plan_manager is not None and _nav_database is not None,
        'nav_db_available': _nav_database is not None,
        'flight_plan_manager_available': _flight_plan_manager is not None,
        'active_plan': _flight_plan_manager.active_plan.name if _flight_plan_manager and _flight_plan_manager.active_plan else None,
        'available_plans': get_all_flight_plans_bridge(),
        'timestamp': str(logger.handlers[0].formatter.formatTime(logging.LogRecord('test', 0, '', 0, '', (), None))) if logger.handlers else 'unknown'
    }

# ============================================================================
# INITIALIZATION AND CLEANUP
# ============================================================================

def cleanup_bridge():
    """Cleanup bridge resources"""
    global _flight_plan_manager, _nav_database
    _flight_plan_manager = None
    _nav_database = None
    logger.info("FMS bridge cleaned up")

# Auto-initialize when module is imported
if __name__ == "__main__":
    # Test the bridge when run directly
    if initialize_fms_bridge():
        print("Bridge test successful")
        status = test_bridge_connection()
        print(f"Bridge status: {status}")
    else:
        print("Bridge initialization failed")
