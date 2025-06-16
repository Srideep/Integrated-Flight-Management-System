
import json
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, asdict
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from nav_database.nav_data_manager import NavigationDatabase, Waypoint

@dataclass
class FlightPlanWaypoint:
    identifier: str
    latitude: float
    longitude: float
    altitude: Optional[int] = None

@dataclass
class FlightPlan:
    name: str
    departure: str
    arrival: str
    waypoints: List[FlightPlanWaypoint]
    created_date: str

class FlightPlanManager:
    def __init__(self):
        self.nav_db = NavigationDatabase()
        
    def create_flight_plan(self, name: str, departure: str, arrival: str, 
                          route: List[str]) -> Optional[FlightPlan]:
        """Create flight plan from waypoint identifiers"""
        waypoints = []
        
        # Build complete route: departure + route + arrival
        full_route = [departure] + route + [arrival]
        
        for wp_id in full_route:
            wp = self.nav_db.find_waypoint(wp_id)
            if wp:
                fp_wp = FlightPlanWaypoint(
                    identifier=wp.identifier,
                    latitude=wp.latitude,
                    longitude=wp.longitude,
                    altitude=int(wp.altitude) if wp.altitude else None
                )
                waypoints.append(fp_wp)
            else:
                print(f"Warning: Waypoint {wp_id} not found")
                return None
                
        return FlightPlan(
            name=name,
            departure=departure,
            arrival=arrival,
            waypoints=waypoints,
            created_date=datetime.now().isoformat()
        )
        
    def save_flight_plan(self, flight_plan: FlightPlan, filename: str) -> bool:
        """Save flight plan to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(asdict(flight_plan), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving flight plan: {e}")
            return False
            
    def load_flight_plan(self, filename: str) -> Optional[FlightPlan]:
        """Load flight plan from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Convert waypoint dictionaries back to FlightPlanWaypoint objects
            waypoints = [FlightPlanWaypoint(**wp) for wp in data['waypoints']]
            data['waypoints'] = waypoints
            
            return FlightPlan(**data)
        except Exception as e:
            print(f"Error loading flight plan: {e}")
            return None

if __name__ == "__main__":
    # Basic test
    fp_manager = FlightPlanManager()
    
    # Create test flight plan
    plan = fp_manager.create_flight_plan(
        name="TEST_SFO_OAK",
        departure="KSFO",
        arrival="KOAK", 
        route=["SFO"]
    )
    
    if plan:
        print(f"Created flight plan: {plan.name}")
        print(f"Route has {len(plan.waypoints)} waypoints")
    else:
        print("Failed to create flight plan")
