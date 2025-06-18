
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
import os
import sys

# Add the parent directory to the path so we can import nav_database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nav_database.nav_data_manager import NavigationDatabase, Waypoint

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FlightPlanWaypoint:
    """Enhanced waypoint class for flight planning"""
    identifier: str
    latitude: float
    longitude: float
    altitude: Optional[int] = None
    speed: Optional[int] = None
    waypoint_type: str = "waypoint"
    procedure_type: Optional[str] = None  # SID, STAR, APPROACH
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlightPlanWaypoint':
        return cls(**data)

@dataclass
class FlightPlan:
    """Enhanced flight plan data structure"""
    name: str
    departure: str
    arrival: str
    waypoints: List[FlightPlanWaypoint]
    cruise_altitude: int = 35000
    cruise_speed: int = 450
    route_distance: float = 0.0
    estimated_time: float = 0.0
    created_date: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.created_date:
            data['created_date'] = self.created_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlightPlan':
        if 'created_date' in data and data['created_date']:
            data['created_date'] = datetime.fromisoformat(data['created_date'])
        
        # Convert waypoint dictionaries back to FlightPlanWaypoint objects
        if 'waypoints' in data:
            data['waypoints'] = [FlightPlanWaypoint.from_dict(wp) for wp in data['waypoints']]
        
        return cls(**data)

class FlightPlanManager:
    """Complete Flight Plan Manager with all FMS integration capabilities"""
    
    def __init__(self, nav_db_path: str = "data/nav_database/navigation.db"):
        """Initialize the Flight Plan Manager with navigation database"""
        self.nav_db = NavigationDatabase(nav_db_path)
        
        # Core State Management (Checklist Section 1)
        self.active_plan: Optional[FlightPlan] = None
        self.current_leg_index: int = 0
        
        # Flight plan storage
        self.flight_plans: Dict[str, FlightPlan] = {}
        
        logger.info("FlightPlanManager initialized successfully")
    
    # ========================================================================
    # SECTION 1: CORE STATE MANAGEMENT
    # ========================================================================
    
    def set_active_plan(self, flight_plan: FlightPlan) -> bool:
        """Set the active flight plan and reset leg index"""
        try:
            self.active_plan = flight_plan
            self.current_leg_index = 0
            logger.info(f"Active plan set to: {flight_plan.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to set active plan: {e}")
            return False
    
    def clear_active_plan(self) -> None:
        """Clear the active plan and reset state variables"""
        self.active_plan = None
        self.current_leg_index = 0
        logger.info("Active plan cleared")
    
    # ========================================================================
    # SECTION 2: LIVE NAVIGATION INTERFACE FOR SIMULINK
    # ========================================================================
    
    def get_current_leg(self) -> Optional[Tuple[FlightPlanWaypoint, FlightPlanWaypoint]]:
        """Get the current leg's start and end waypoints"""
        if not self.active_plan or not self.active_plan.waypoints:
            return None
        
        waypoints = self.active_plan.waypoints
        
        # Handle end of route
        if self.current_leg_index >= len(waypoints) - 1:
            logger.warning("At end of route - no current leg available")
            return None
        
        start_wp = waypoints[self.current_leg_index]
        end_wp = waypoints[self.current_leg_index + 1]
        
        return (start_wp, end_wp)
    
    def get_next_waypoint(self) -> Optional[FlightPlanWaypoint]:
        """Get the next waypoint (destination of current leg)"""
        if not self.active_plan or not self.active_plan.waypoints:
            return None
        
        waypoints = self.active_plan.waypoints
        
        # Handle end of route
        if self.current_leg_index >= len(waypoints) - 1:
            logger.info("At end of route - no next waypoint")
            return None
        
        return waypoints[self.current_leg_index + 1]
    
    def advance_to_next_leg(self) -> bool:
        """Advance to the next leg of the flight plan"""
        if not self.active_plan or not self.active_plan.waypoints:
            logger.warning("No active plan to advance")
            return False
        
        waypoints = self.active_plan.waypoints
        
        # Check if we can advance
        if self.current_leg_index >= len(waypoints) - 1:
            logger.info("Already at end of route")
            return False
        
        self.current_leg_index += 1
        logger.info(f"Advanced to leg {self.current_leg_index}")
        return True
    
    def is_end_of_route(self) -> bool:
        """Check if we've reached the end of the route"""
        if not self.active_plan or not self.active_plan.waypoints:
            return True
        
        return self.current_leg_index >= len(self.active_plan.waypoints) - 1
    
    # ========================================================================
    # SECTION 3: ADVANCED FLIGHT PLANNING FEATURES
    # ========================================================================
    
    def insert_waypoint(self, wp_id: str, position: int) -> bool:
        """Insert a waypoint into the active plan at specified position"""
        if not self.active_plan:
            logger.error("No active plan to modify")
            return False
        
        try:
            waypoint = self.nav_db.find_waypoint(wp_id)
            if not waypoint:
                logger.error(f"Waypoint {wp_id} not found in database")
                return False
            
            fp_waypoint = FlightPlanWaypoint(
                identifier=waypoint.identifier,
                latitude=waypoint.latitude,
                longitude=waypoint.longitude,
                waypoint_type=waypoint.waypoint_type
            )
            
            self.active_plan.waypoints.insert(position, fp_waypoint)
            logger.info(f"Inserted waypoint {wp_id} at position {position}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert waypoint: {e}")
            return False
    
    def delete_waypoint(self, position: int) -> bool:
        """Remove waypoint from active plan at specified position"""
        if not self.active_plan or not self.active_plan.waypoints:
            logger.error("No active plan or waypoints to delete")
            return False
        
        try:
            if 0 <= position < len(self.active_plan.waypoints):
                removed_wp = self.active_plan.waypoints.pop(position)
                logger.info(f"Deleted waypoint {removed_wp.identifier} at position {position}")
                
                # Adjust current leg index if necessary
                if position <= self.current_leg_index and self.current_leg_index > 0:
                    self.current_leg_index -= 1
                
                return True
            else:
                logger.error(f"Invalid position {position}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete waypoint: {e}")
            return False
    
    def modify_waypoint(self, position: int, new_altitude: Optional[int] = None, 
                       new_speed: Optional[int] = None) -> bool:
        """Modify waypoint data at specified position"""
        if not self.active_plan or not self.active_plan.waypoints:
            logger.error("No active plan or waypoints to modify")
            return False
        
        try:
            if 0 <= position < len(self.active_plan.waypoints):
                waypoint = self.active_plan.waypoints[position]
                
                if new_altitude is not None:
                    waypoint.altitude = new_altitude
                if new_speed is not None:
                    waypoint.speed = new_speed
                
                logger.info(f"Modified waypoint {waypoint.identifier} at position {position}")
                return True
            else:
                logger.error(f"Invalid position {position}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to modify waypoint: {e}")
            return False
    
    def expand_airway(self, airway_id: str) -> List[FlightPlanWaypoint]:
        """Expand airway identifier into sequence of waypoints"""
        try:
            # Get airway waypoints from navigation database
            airway_waypoints = self.nav_db.get_airway_waypoints(airway_id)
            
            fp_waypoints = []
            for waypoint in airway_waypoints:
                fp_waypoint = FlightPlanWaypoint(
                    identifier=waypoint.identifier,
                    latitude=waypoint.latitude,
                    longitude=waypoint.longitude,
                    waypoint_type="airway_waypoint"
                )
                fp_waypoints.append(fp_waypoint)
            
            logger.info(f"Expanded airway {airway_id} to {len(fp_waypoints)} waypoints")
            return fp_waypoints
            
        except Exception as e:
            logger.error(f"Failed to expand airway {airway_id}: {e}")
            return []
    
    def add_procedure(self, procedure_type: str, procedure_id: str, 
                     position: str = "end") -> bool:
        """Add SID/STAR procedure to flight plan"""
        if not self.active_plan:
            logger.error("No active plan to add procedure to")
            return False
        
        try:
            # This would typically query a procedures database
            # For now, we'll create a placeholder implementation
            logger.info(f"Adding {procedure_type} procedure {procedure_id}")
            
            # Create placeholder procedure waypoint
            proc_waypoint = FlightPlanWaypoint(
                identifier=f"{procedure_id}_WP",
                latitude=0.0,  # Would be populated from procedures database
                longitude=0.0,
                waypoint_type="procedure",
                procedure_type=procedure_type
            )
            
            if position == "start":
                self.active_plan.waypoints.insert(0, proc_waypoint)
            else:  # "end"
                self.active_plan.waypoints.append(proc_waypoint)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add procedure: {e}")
            return False
    
    # ========================================================================
    # ENHANCED FLIGHT PLAN CREATION AND MANAGEMENT
    # ========================================================================
    
    def create_flight_plan(self, name: str, departure: str, arrival: str, 
                          route: List[str], cruise_alt: int = 35000, 
                          cruise_speed: int = 450) -> Optional[FlightPlan]:
        """Enhanced flight plan creation with airway expansion"""
        try:
            waypoints = []
            
            # Add departure
            dep_waypoint = self.nav_db.find_waypoint(departure)
            if dep_waypoint:
                waypoints.append(FlightPlanWaypoint(
                    identifier=dep_waypoint.identifier,
                    latitude=dep_waypoint.latitude,
                    longitude=dep_waypoint.longitude,
                    waypoint_type=dep_waypoint.waypoint_type
                ))
            
            # Process route elements (could be waypoints or airways)
            for element in route:
                if element.startswith(('J', 'V', 'Q', 'T')):  # Common airway prefixes
                    # Expand airway
                    airway_waypoints = self.expand_airway(element)
                    waypoints.extend(airway_waypoints)
                else:
                    # Regular waypoint
                    waypoint = self.nav_db.find_waypoint(element)
                    if waypoint:
                        waypoints.append(FlightPlanWaypoint(
                            identifier=waypoint.identifier,
                            latitude=waypoint.latitude,
                            longitude=waypoint.longitude,
                            waypoint_type=waypoint.waypoint_type
                        ))
            
            # Add arrival
            arr_waypoint = self.nav_db.find_waypoint(arrival)
            if arr_waypoint:
                waypoints.append(FlightPlanWaypoint(
                    identifier=arr_waypoint.identifier,
                    latitude=arr_waypoint.latitude,
                    longitude=arr_waypoint.longitude,
                    waypoint_type=arr_waypoint.waypoint_type
                ))
            
            flight_plan = FlightPlan(
                name=name,
                departure=departure,
                arrival=arrival,
                waypoints=waypoints,
                cruise_altitude=cruise_alt,
                cruise_speed=cruise_speed
            )
            
            self.flight_plans[name] = flight_plan
            logger.info(f"Created flight plan {name} with {len(waypoints)} waypoints")
            return flight_plan
            
        except Exception as e:
            logger.error(f"Failed to create flight plan: {e}")
            return None
    
    def optimize_active_plan(self) -> bool:
        """Optimize the active flight plan (placeholder for route optimizer integration)"""
        if not self.active_plan:
            logger.error("No active plan to optimize")
            return False
        
        try:
            # This would integrate with route_optimizer.py
            # For now, implement basic optimization logic
            logger.info(f"Optimizing flight plan: {self.active_plan.name}")
            
            # Placeholder optimization - could calculate more efficient routes
            # In a real implementation, this would call the route optimizer
            
            logger.info("Flight plan optimization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize flight plan: {e}")
            return False
    
    def save_flight_plan(self, flight_plan: FlightPlan, filename: str = None) -> bool:
        """Save flight plan to file"""
        try:
            if filename is None:
                filename = f"data/flight_plans/{flight_plan.name}.json"
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(flight_plan.to_dict(), f, indent=2, default=str)
            
            logger.info(f"Saved flight plan to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save flight plan: {e}")
            return False
    
    def load_flight_plan(self, filename: str) -> Optional[FlightPlan]:
        """Load flight plan from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            flight_plan = FlightPlan.from_dict(data)
            self.flight_plans[flight_plan.name] = flight_plan
            
            logger.info(f"Loaded flight plan: {flight_plan.name}")
            return flight_plan
            
        except Exception as e:
            logger.error(f"Failed to load flight plan from {filename}: {e}")
            return None
    
    def get_flight_plan_status(self) -> Dict[str, Any]:
        """Get comprehensive status of current flight plan state"""
        if not self.active_plan:
            return {"status": "no_active_plan"}
        
        current_leg = self.get_current_leg()
        next_waypoint = self.get_next_waypoint()
        
        return {
            "status": "active",
            "plan_name": self.active_plan.name,
            "current_leg_index": self.current_leg_index,
            "total_legs": len(self.active_plan.waypoints) - 1,
            "current_leg": {
                "from": current_leg[0].identifier if current_leg else None,
                "to": current_leg[1].identifier if current_leg else None
            } if current_leg else None,
            "next_waypoint": next_waypoint.identifier if next_waypoint else None,
            "end_of_route": self.is_end_of_route(),
            "total_waypoints": len(self.active_plan.waypoints)
        }

# Factory function for easier integration
def create_flight_plan_manager(nav_db_path: str = "data/nav_database/navigation.db") -> FlightPlanManager:
    """Factory function to create a FlightPlanManager instance"""
    return FlightPlanManager(nav_db_path)
