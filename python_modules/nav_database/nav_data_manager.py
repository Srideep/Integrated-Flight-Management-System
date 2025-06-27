
import sqlite3
import os
from dataclasses import dataclass
from typing import List, Optional

from .airway_database import AirwayDatabase
from .procedure_database import ProcedureDatabase

@dataclass
class Waypoint:
    identifier: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    waypoint_type: str = 'WAYPOINT'

class NavigationDatabase:
    def __init__(self, db_path: str = 'nav_database.db'):
        self.db_path = db_path
        self.connection = None
        self.airway_db = AirwayDatabase(os.path.join(os.path.dirname(db_path), 'airways.db'))
        self.procedure_db = ProcedureDatabase(os.path.join(os.path.dirname(db_path), 'procedures.db'))
        self.initialize_database()
        
    def initialize_database(self):
        """Create database and populate with test data"""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # Create waypoints table with enhanced schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waypoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier TEXT UNIQUE NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                altitude REAL,
                waypoint_type TEXT DEFAULT 'WAYPOINT',
                frequency REAL,
                magnetic_variation REAL,
                elevation REAL,
                region TEXT,
                country TEXT,
                created_date TEXT,
                CHECK (latitude >= -90 AND latitude <= 90),
                CHECK (longitude >= -180 AND longitude <= 180)
            )
        ''')
        
        # Insert test data with enhanced schema
        test_waypoints = [
            ('KSFO', 37.6213, -122.3790, 13, 'AIRPORT', None, None, 13, 'CA', 'USA', None),
            ('KOAK', 37.7214, -122.2208, 9, 'AIRPORT', None, None, 9, 'CA', 'USA', None),
            ('SFO', 37.6189, -122.3750, None, 'VOR', 113.9, None, None, 'CA', 'USA', None),
            ('FAITH', 37.2833, -122.0167, None, 'WAYPOINT', None, None, None, 'CA', 'USA', None),
            ('WESLA', 37.7000, -122.4167, None, 'WAYPOINT', None, None, None, 'CA', 'USA', None),
            ('REJOY', 37.5000, -122.2000, None, 'WAYPOINT', None, None, None, 'CA', 'USA', None),
            ('CNDEL', 37.4000, -122.1000, None, 'WAYPOINT', None, None, None, 'CA', 'USA', None),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO waypoints 
            (identifier, latitude, longitude, altitude, waypoint_type, frequency, magnetic_variation, elevation, region, country, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_waypoints)
        
        self.connection.commit()

    def add_waypoint(self, waypoint):
        """Add a waypoint to the database"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO waypoints 
            (identifier, latitude, longitude, altitude, waypoint_type, frequency, magnetic_variation, elevation, region, country, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (waypoint.identifier, waypoint.latitude, waypoint.longitude, 
              waypoint.altitude, waypoint.waypoint_type,
              getattr(waypoint, 'frequency', None),
              getattr(waypoint, 'magnetic_variation', None),
              getattr(waypoint, 'elevation', None),
              getattr(waypoint, 'region', None),
              getattr(waypoint, 'country', None),
              getattr(waypoint, 'created_date', None)))
        self.connection.commit()
        
    def find_waypoint(self, identifier: str) -> Optional[Waypoint]:
        """Find waypoint by identifier"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT identifier, latitude, longitude, altitude, waypoint_type,
                   frequency, magnetic_variation, elevation, region, country, created_date
            FROM waypoints WHERE identifier = ?
        ''', (identifier,))
        
        result = cursor.fetchone()
        if result:
            # Create waypoint with basic fields, extras will be ignored if Waypoint doesn't support them
            return Waypoint(result[0], result[1], result[2], result[3], result[4])
        return None
        
    def list_all_waypoints(self) -> List[Waypoint]:
        """Get all waypoints for testing"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT identifier, latitude, longitude, altitude, waypoint_type,
                   frequency, magnetic_variation, elevation, region, country, created_date
            FROM waypoints
        ''')
        # Create waypoints with basic fields only
        return [Waypoint(row[0], row[1], row[2], row[3], row[4]) for row in cursor.fetchall()]

    def get_airway_waypoints(self, airway_name: str) -> List[Waypoint]:
        """Return waypoints for the specified airway"""
        waypoint_ids = self.airway_db.get_airway_waypoints(airway_name)
        waypoints = []
        for wp_id in waypoint_ids:
            wp = self.find_waypoint(wp_id)
            if wp:
                waypoints.append(wp)
        return waypoints

    def get_procedure_waypoints(self, procedure_name: str) -> List[Waypoint]:
        """Return waypoints for the specified procedure"""
        waypoint_ids = self.procedure_db.get_procedure_waypoints(procedure_name)
        waypoints = []
        for wp_id in waypoint_ids:
            wp = self.find_waypoint(wp_id)
            if wp:
                waypoints.append(wp)
        return waypoints

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
        self.airway_db.close()
        self.procedure_db.close()

if __name__ == "__main__":
    # Basic test when run directly
    db = NavigationDatabase()
    print("Database initialized successfully")
    
    # Test waypoint lookup
    ksfo = db.find_waypoint('KSFO')
    if ksfo:
        print(f"Found KSFO: {ksfo.latitude}, {ksfo.longitude}")
    else:
        print("KSFO not found")

    # Test airway lookup
    airway_wps = db.get_airway_waypoints('V334')
    print(f"Airway V334 has {len(airway_wps)} waypoints")

    # Test procedure lookup
    proc_wps = db.get_procedure_waypoints('TEST_SID')
    print(f"Procedure TEST_SID has {len(proc_wps)} waypoints")
    db.close()
