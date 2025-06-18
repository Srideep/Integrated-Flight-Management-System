
import sqlite3
from dataclasses import dataclass
from typing import List, Optional

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
        self.initialize_database()
        
    def initialize_database(self):
        """Create database and populate with test data"""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # Create waypoints table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waypoints (
                id INTEGER PRIMARY KEY,
                identifier TEXT UNIQUE NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                altitude REAL,
                waypoint_type TEXT DEFAULT 'WAYPOINT'
            )
        ''')
        
        # Insert test data
        test_waypoints = [
            ('KSFO', 37.6213, -122.3790, 13, 'AIRPORT'),
            ('KOAK', 37.7214, -122.2208, 9, 'AIRPORT'),
            ('SFO', 37.6189, -122.3750, None, 'VOR'),
            ('FAITH', 37.2833, -122.0167, None, 'WAYPOINT'),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO waypoints 
            (identifier, latitude, longitude, altitude, waypoint_type)
            VALUES (?, ?, ?, ?, ?)
        ''', test_waypoints)
        
        self.connection.commit()

    def add_waypoint(self, waypoint):
        """Add a waypoint to the database"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO waypoints 
            (identifier, latitude, longitude, altitude, waypoint_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (waypoint.identifier, waypoint.latitude, waypoint.longitude, 
              waypoint.altitude, waypoint.waypoint_type))
        self.connection.commit()
        
    def find_waypoint(self, identifier: str) -> Optional[Waypoint]:
        """Find waypoint by identifier"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT identifier, latitude, longitude, altitude, waypoint_type
            FROM waypoints WHERE identifier = ?
        ''', (identifier,))
        
        result = cursor.fetchone()
        if result:
            return Waypoint(*result)
        return None
        
    def list_all_waypoints(self) -> List[Waypoint]:
        """Get all waypoints for testing"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT identifier, latitude, longitude, altitude, waypoint_type FROM waypoints')
        return [Waypoint(*row) for row in cursor.fetchall()]

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