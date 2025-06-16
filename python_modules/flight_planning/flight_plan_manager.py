
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
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import sys
import os

# Add the parent directory to sys.path to import nav_database
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from nav_database.nav_data_manager import NavigationDatabase, Waypoint

@dataclass
class FlightPlanWaypoint:
    waypoint: Waypoint
    sequence: int
    altitude_constraint: Optional[int] = None
    speed_constraint: Optional[int] = None

@dataclass
class FlightPlan:
    name: str
    departure: str
    arrival: str
    waypoints: List[FlightPlanWaypoint] = field(default_factory=list)
    cruise_altitude: int = 35000
    cruise_speed: int = 450
    created_date: datetime = field(default_factory=datetime.now)

class FlightPlanManager:
    def __init__(self, nav_db: Optional[NavigationDatabase] = None):
        self.nav_db = nav_db or NavigationDatabase()
        self.connection = sqlite3.connect('flight_plans.db')
        self.initialize_database()
        
    def initialize_database(self):
        """Initialize flight plan database"""
        cursor = self.connection.cursor()
        
        # Create flight plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flight_plans (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                departure TEXT NOT NULL,
                arrival TEXT NOT NULL,
                cruise_altitude INTEGER DEFAULT 35000,
                cruise_speed INTEGER DEFAULT 450,
                created_date TEXT NOT NULL
            )
        ''')
        
        # Create flight plan waypoints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flight_plan_waypoints (
                id INTEGER PRIMARY KEY,
                flight_plan_id INTEGER,
                waypoint_identifier TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                altitude_constraint INTEGER,
                speed_constraint INTEGER,
                FOREIGN KEY (flight_plan_id) REFERENCES flight_plans (id)
            )
        ''')
        
        self.connection.commit()
        
    def create_flight_plan(self, name: str, departure: str, arrival: str, 
                          route: List[str], cruise_alt: int = 35000, 
                          cruise_speed: int = 450) -> Optional[FlightPlan]:
        """Create a new flight plan"""
        try:
            # Validate departure and arrival airports
            dep_waypoint = self.nav_db.find_waypoint(departure)
            arr_waypoint = self.nav_db.find_waypoint(arrival)
            
            if not dep_waypoint or not arr_waypoint:
                print(f"Error: Could not find departure ({departure}) or arrival ({arrival}) waypoint")
                return None
            
            # Create flight plan
            flight_plan = FlightPlan(
                name=name,
                departure=departure,
                arrival=arrival,
                cruise_altitude=cruise_alt,
                cruise_speed=cruise_speed
            )
            
            # Add departure waypoint
            flight_plan.waypoints.append(
                FlightPlanWaypoint(waypoint=dep_waypoint, sequence=0)
            )
            
            # Add route waypoints
            for i, waypoint_id in enumerate(route):
                waypoint = self.nav_db.find_waypoint(waypoint_id)
                if waypoint:
                    flight_plan.waypoints.append(
                        FlightPlanWaypoint(waypoint=waypoint, sequence=i+1)
                    )
                else:
                    print(f"Warning: Waypoint {waypoint_id} not found, skipping")
            
            # Add arrival waypoint
            flight_plan.waypoints.append(
                FlightPlanWaypoint(
                    waypoint=arr_waypoint, 
                    sequence=len(flight_plan.waypoints)
                )
            )
            
            return flight_plan
            
        except Exception as e:
            print(f"Error creating flight plan: {e}")
            return None
    
    def save_flight_plan(self, flight_plan: FlightPlan) -> bool:
        """Save flight plan to database"""
        try:
            cursor = self.connection.cursor()
            
            # Insert flight plan
            cursor.execute('''
                INSERT OR REPLACE INTO flight_plans 
                (name, departure, arrival, cruise_altitude, cruise_speed, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                flight_plan.name,
                flight_plan.departure,
                flight_plan.arrival,
                flight_plan.cruise_altitude,
                flight_plan.cruise_speed,
                flight_plan.created_date.isoformat()
            ))
            
            flight_plan_id = cursor.lastrowid
            
            # Delete existing waypoints for this flight plan
            cursor.execute('''
                DELETE FROM flight_plan_waypoints WHERE flight_plan_id = ?
            ''', (flight_plan_id,))
            
            # Insert waypoints
            for wp in flight_plan.waypoints:
                cursor.execute('''
                    INSERT INTO flight_plan_waypoints
                    (flight_plan_id, waypoint_identifier, sequence_number, 
                     altitude_constraint, speed_constraint)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    flight_plan_id,
                    wp.waypoint.identifier,
                    wp.sequence,
                    wp.altitude_constraint,
                    wp.speed_constraint
                ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"Error saving flight plan: {e}")
            return False
    
    def load_flight_plan(self, name: str) -> Optional[FlightPlan]:
        """Load flight plan from database"""
        try:
            cursor = self.connection.cursor()
            
            # Get flight plan info
            cursor.execute('''
                SELECT name, departure, arrival, cruise_altitude, cruise_speed, created_date
                FROM flight_plans WHERE name = ?
            ''', (name,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            # Create flight plan object
            flight_plan = FlightPlan(
                name=result[0],
                departure=result[1],
                arrival=result[2],
                cruise_altitude=result[3],
                cruise_speed=result[4],
                created_date=datetime.fromisoformat(result[5])
            )
            
            # Get waypoints
            cursor.execute('''
                SELECT waypoint_identifier, sequence_number, altitude_constraint, speed_constraint
                FROM flight_plan_waypoints 
                WHERE flight_plan_id = (SELECT id FROM flight_plans WHERE name = ?)
                ORDER BY sequence_number
            ''', (name,))
            
            for row in cursor.fetchall():
                waypoint = self.nav_db.find_waypoint(row[0])
                if waypoint:
                    flight_plan.waypoints.append(
                        FlightPlanWaypoint(
                            waypoint=waypoint,
                            sequence=row[1],
                            altitude_constraint=row[2],
                            speed_constraint=row[3]
                        )
                    )
            
            return flight_plan
            
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
