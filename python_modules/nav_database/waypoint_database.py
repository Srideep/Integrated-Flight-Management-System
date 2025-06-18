
#!/usr/bin/env python3
"""
Waypoint Database Manager
Specialized functions for waypoint management, validation, and operations
"""

import sqlite3
import math
import logging
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Waypoint:
    """Enhanced waypoint class with validation and utility methods"""
    identifier: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    waypoint_type: str = 'WAYPOINT'
    frequency: Optional[float] = None  # For VOR/NDB
    magnetic_variation: Optional[float] = None
    elevation: Optional[float] = None  # Ground elevation for airports
    region: Optional[str] = None
    country: Optional[str] = None
    created_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate waypoint data after initialization"""
        if self.created_date is None:
            self.created_date = datetime.now()
        
        # Validate coordinates
        if not self.is_valid_coordinates():
            raise ValueError(f"Invalid coordinates for waypoint {self.identifier}")
        
        # Normalize identifier to uppercase
        self.identifier = self.identifier.upper()
    
    def is_valid_coordinates(self) -> bool:
        """Validate latitude and longitude ranges"""
        return (-90 <= self.latitude <= 90) and (-180 <= self.longitude <= 180)
    
    def distance_to(self, other: 'Waypoint') -> float:
        """Calculate great circle distance to another waypoint in nautical miles"""
        return calculate_distance(self.latitude, self.longitude, 
                                other.latitude, other.longitude)
    
    def bearing_to(self, other: 'Waypoint') -> float:
        """Calculate initial bearing to another waypoint in degrees"""
        return calculate_bearing(self.latitude, self.longitude,
                               other.latitude, other.longitude)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert waypoint to dictionary"""
        data = asdict(self)
        if self.created_date:
            data['created_date'] = self.created_date.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Waypoint':
        """Create waypoint from dictionary"""
        if 'created_date' in data and data['created_date']:
            data['created_date'] = datetime.fromisoformat(data['created_date'])
        return cls(**data)

class WaypointDatabase:
    """Specialized waypoint database manager with advanced search and validation"""
    
    def __init__(self, db_path: str = 'data/nav_database/waypoints.db'):
        """Initialize waypoint database"""
        self.db_path = db_path
        self.connection = None
        self.initialize_database()
        logger.info(f"WaypointDatabase initialized at {db_path}")
    
    def initialize_database(self):
        """Create database tables and indexes"""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # Create enhanced waypoints table
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
        
        # Create spatial index for efficient geographic queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_waypoint_location 
            ON waypoints (latitude, longitude)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_waypoint_type 
            ON waypoints (waypoint_type)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_waypoint_region 
            ON waypoints (region, country)
        ''')
        
        self.connection.commit()
        logger.info("Waypoint database tables and indexes created")
    
    def add_waypoint(self, waypoint: Waypoint) -> bool:
        """Add or update a waypoint in the database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO waypoints 
                (identifier, latitude, longitude, altitude, waypoint_type, 
                 frequency, magnetic_variation, elevation, region, country, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                waypoint.identifier, waypoint.latitude, waypoint.longitude,
                waypoint.altitude, waypoint.waypoint_type, waypoint.frequency,
                waypoint.magnetic_variation, waypoint.elevation, waypoint.region,
                waypoint.country, waypoint.created_date.isoformat() if waypoint.created_date else None
            ))
            
            self.connection.commit()
            logger.info(f"Added waypoint {waypoint.identifier}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add waypoint {waypoint.identifier}: {e}")
            return False
    
    def find_waypoint(self, identifier: str) -> Optional[Waypoint]:
        """Find waypoint by identifier"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT identifier, latitude, longitude, altitude, waypoint_type,
                       frequency, magnetic_variation, elevation, region, country, created_date
                FROM waypoints WHERE UPPER(identifier) = UPPER(?)
            ''', (identifier,))
            
            result = cursor.fetchone()
            if result:
                data = {
                    'identifier': result[0],
                    'latitude': result[1],
                    'longitude': result[2],
                    'altitude': result[3],
                    'waypoint_type': result[4],
                    'frequency': result[5],
                    'magnetic_variation': result[6],
                    'elevation': result[7],
                    'region': result[8],
                    'country': result[9],
                    'created_date': datetime.fromisoformat(result[10]) if result[10] else None
                }
                return Waypoint.from_dict(data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find waypoint {identifier}: {e}")
            return None
    
    def find_waypoints_by_type(self, waypoint_type: str) -> List[Waypoint]:
        """Find all waypoints of a specific type"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT identifier, latitude, longitude, altitude, waypoint_type,
                       frequency, magnetic_variation, elevation, region, country, created_date
                FROM waypoints WHERE UPPER(waypoint_type) = UPPER(?)
                ORDER BY identifier
            ''', (waypoint_type,))
            
            waypoints = []
            for row in cursor.fetchall():
                data = {
                    'identifier': row[0],
                    'latitude': row[1],
                    'longitude': row[2],
                    'altitude': row[3],
                    'waypoint_type': row[4],
                    'frequency': row[5],
                    'magnetic_variation': row[6],
                    'elevation': row[7],
                    'region': row[8],
                    'country': row[9],
                    'created_date': datetime.fromisoformat(row[10]) if row[10] else None
                }
                waypoints.append(Waypoint.from_dict(data))
            
            logger.info(f"Found {len(waypoints)} waypoints of type {waypoint_type}")
            return waypoints
            
        except Exception as e:
            logger.error(f"Failed to find waypoints by type {waypoint_type}: {e}")
            return []
    
    def find_waypoints_in_radius(self, center_lat: float, center_lon: float, 
                                radius_nm: float) -> List[Tuple[Waypoint, float]]:
        """Find waypoints within specified radius (nautical miles) of a point"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT identifier, latitude, longitude, altitude, waypoint_type,
                       frequency, magnetic_variation, elevation, region, country, created_date
                FROM waypoints
            ''')
            
            waypoints_with_distance = []
            for row in cursor.fetchall():
                data = {
                    'identifier': row[0],
                    'latitude': row[1],
                    'longitude': row[2],
                    'altitude': row[3],
                    'waypoint_type': row[4],
                    'frequency': row[5],
                    'magnetic_variation': row[6],
                    'elevation': row[7],
                    'region': row[8],
                    'country': row[9],
                    'created_date': datetime.fromisoformat(row[10]) if row[10] else None
                }
                waypoint = Waypoint.from_dict(data)
                
                # Calculate distance
                distance = calculate_distance(center_lat, center_lon, 
                                            waypoint.latitude, waypoint.longitude)
                
                if distance <= radius_nm:
                    waypoints_with_distance.append((waypoint, distance))
            
            # Sort by distance
            waypoints_with_distance.sort(key=lambda x: x[1])
            
            logger.info(f"Found {len(waypoints_with_distance)} waypoints within {radius_nm}nm")
            return waypoints_with_distance
            
        except Exception as e:
            logger.error(f"Failed to find waypoints in radius: {e}")
            return []
    
    def find_waypoints_by_region(self, region: str, country: str = None) -> List[Waypoint]:
        """Find waypoints by region and optionally country"""
        try:
            cursor = self.connection.cursor()
            
            if country:
                cursor.execute('''
                    SELECT identifier, latitude, longitude, altitude, waypoint_type,
                           frequency, magnetic_variation, elevation, region, country, created_date
                    FROM waypoints 
                    WHERE UPPER(region) = UPPER(?) AND UPPER(country) = UPPER(?)
                    ORDER BY identifier
                ''', (region, country))
            else:
                cursor.execute('''
                    SELECT identifier, latitude, longitude, altitude, waypoint_type,
                           frequency, magnetic_variation, elevation, region, country, created_date
                    FROM waypoints 
                    WHERE UPPER(region) = UPPER(?)
                    ORDER BY identifier
                ''', (region,))
            
            waypoints = []
            for row in cursor.fetchall():
                data = {
                    'identifier': row[0],
                    'latitude': row[1],
                    'longitude': row[2],
                    'altitude': row[3],
                    'waypoint_type': row[4],
                    'frequency': row[5],
                    'magnetic_variation': row[6],
                    'elevation': row[7],
                    'region': row[8],
                    'country': row[9],
                    'created_date': datetime.fromisoformat(row[10]) if row[10] else None
                }
                waypoints.append(Waypoint.from_dict(data))
            
            logger.info(f"Found {len(waypoints)} waypoints in region {region}")
            return waypoints
            
        except Exception as e:
            logger.error(f"Failed to find waypoints by region {region}: {e}")
            return []
    
    def search_waypoints(self, search_term: str, limit: int = 50) -> List[Waypoint]:
        """Search waypoints by partial identifier match"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT identifier, latitude, longitude, altitude, waypoint_type,
                       frequency, magnetic_variation, elevation, region, country, created_date
                FROM waypoints 
                WHERE UPPER(identifier) LIKE UPPER(?)
                ORDER BY identifier
                LIMIT ?
            ''', (f'%{search_term}%', limit))
            
            waypoints = []
            for row in cursor.fetchall():
                data = {
                    'identifier': row[0],
                    'latitude': row[1],
                    'longitude': row[2],
                    'altitude': row[3],
                    'waypoint_type': row[4],
                    'frequency': row[5],
                    'magnetic_variation': row[6],
                    'elevation': row[7],
                    'region': row[8],
                    'country': row[9],
                    'created_date': datetime.fromisoformat(row[10]) if row[10] else None
                }
                waypoints.append(Waypoint.from_dict(data))
            
            logger.info(f"Found {len(waypoints)} waypoints matching '{search_term}'")
            return waypoints
            
        except Exception as e:
            logger.error(f"Failed to search waypoints: {e}")
            return []
    
    def delete_waypoint(self, identifier: str) -> bool:
        """Delete waypoint by identifier"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM waypoints WHERE UPPER(identifier) = UPPER(?)', (identifier,))
            
            if cursor.rowcount > 0:
                self.connection.commit()
                logger.info(f"Deleted waypoint {identifier}")
                return True
            else:
                logger.warning(f"Waypoint {identifier} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete waypoint {identifier}: {e}")
            return False
    
    def get_waypoint_statistics(self) -> Dict[str, Any]:
        """Get statistics about waypoints in the database"""
        try:
            cursor = self.connection.cursor()
            
            # Total count
            cursor.execute('SELECT COUNT(*) FROM waypoints')
            total_count = cursor.fetchone()[0]
            
            # Count by type
            cursor.execute('''
                SELECT waypoint_type, COUNT(*) 
                FROM waypoints 
                GROUP BY waypoint_type 
                ORDER BY COUNT(*) DESC
            ''')
            type_counts = dict(cursor.fetchall())
            
            # Count by region
            cursor.execute('''
                SELECT region, COUNT(*) 
                FROM waypoints 
                WHERE region IS NOT NULL
                GROUP BY region 
                ORDER BY COUNT(*) DESC
                LIMIT 10
            ''')
            region_counts = dict(cursor.fetchall())
            
            stats = {
                'total_waypoints': total_count,
                'by_type': type_counts,
                'by_region': region_counts,
                'database_path': self.db_path
            }
            
            logger.info(f"Generated statistics for {total_count} waypoints")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get waypoint statistics: {e}")
            return {}
    
    def validate_waypoint_data(self, waypoint: Waypoint) -> List[str]:
        """Validate waypoint data and return list of validation errors"""
        errors = []
        
        # Required fields
        if not waypoint.identifier or not waypoint.identifier.strip():
            errors.append("Identifier is required")
        
        # Coordinate validation
        if not waypoint.is_valid_coordinates():
            errors.append("Invalid latitude or longitude coordinates")
        
        # Identifier format validation
        if waypoint.identifier and not waypoint.identifier.replace('_', '').replace('-', '').isalnum():
            errors.append("Identifier contains invalid characters")
        
        # Type validation
        valid_types = ['AIRPORT', 'VOR', 'NDB', 'WAYPOINT', 'INTERSECTION', 'DME', 'TACAN']
        if waypoint.waypoint_type not in valid_types:
            errors.append(f"Invalid waypoint type. Must be one of: {', '.join(valid_types)}")
        
        # Frequency validation for radio aids
        if waypoint.waypoint_type in ['VOR', 'NDB', 'DME', 'TACAN'] and waypoint.frequency:
            if waypoint.waypoint_type == 'VOR' and not (108.0 <= waypoint.frequency <= 118.0):
                errors.append("VOR frequency must be between 108.0 and 118.0 MHz")
            elif waypoint.waypoint_type == 'NDB' and not (190 <= waypoint.frequency <= 1750):
                errors.append("NDB frequency must be between 190 and 1750 kHz")
        
        return errors
    
    def bulk_import_waypoints(self, waypoints: List[Waypoint]) -> Tuple[int, int, List[str]]:
        """Import multiple waypoints, return (success_count, error_count, errors)"""
        success_count = 0
        error_count = 0
        errors = []
        
        for waypoint in waypoints:
            validation_errors = self.validate_waypoint_data(waypoint)
            if validation_errors:
                error_count += 1
                errors.extend([f"{waypoint.identifier}: {error}" for error in validation_errors])
            else:
                if self.add_waypoint(waypoint):
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"{waypoint.identifier}: Failed to add to database")
        
        logger.info(f"Bulk import completed: {success_count} success, {error_count} errors")
        return success_count, error_count, errors
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Waypoint database connection closed")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great circle distance between two points in nautical miles"""
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = (math.sin(dlat/2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    # Earth radius in nautical miles
    earth_radius_nm = 3440.065
    
    return earth_radius_nm * c

def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate initial bearing from point 1 to point 2 in degrees"""
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    
    y = math.sin(dlon) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))
    
    bearing_rad = math.atan2(y, x)
    bearing_deg = math.degrees(bearing_rad)
    
    # Normalize to 0-360 degrees
    return (bearing_deg + 360) % 360

def create_waypoint_from_coordinates(identifier: str, latitude: float, longitude: float,
                                   waypoint_type: str = 'WAYPOINT', **kwargs) -> Waypoint:
    """Factory function to create waypoint from coordinates"""
    return Waypoint(
        identifier=identifier,
        latitude=latitude,
        longitude=longitude,
        waypoint_type=waypoint_type,
        **kwargs
    )

# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

if __name__ == "__main__":
    # Example usage
    print("=== Waypoint Database Manager Test ===")
    
    # Initialize database
    wp_db = WaypointDatabase('test_waypoints.db')
    
    # Create test waypoints
    test_waypoints = [
        Waypoint("KSFO", 37.6213, -122.3790, altitude=13, waypoint_type="AIRPORT", region="CA", country="USA"),
        Waypoint("KOAK", 37.7214, -122.2208, altitude=9, waypoint_type="AIRPORT", region="CA", country="USA"),
        Waypoint("SFO", 37.6189, -122.3750, waypoint_type="VOR", frequency=113.9, region="CA", country="USA"),
        Waypoint("WESLA", 37.7000, -122.4167, waypoint_type="WAYPOINT", region="CA", country="USA"),
    ]
    
    # Bulk import
    success, errors, error_list = wp_db.bulk_import_waypoints(test_waypoints)
    print(f"Imported {success} waypoints, {errors} errors")
    
    # Test searches
    print("\n--- Search Tests ---")
    ksfo = wp_db.find_waypoint("KSFO")
    if ksfo:
        print(f"Found KSFO: {ksfo.latitude}, {ksfo.longitude}")
    
    airports = wp_db.find_waypoints_by_type("AIRPORT")
    print(f"Found {len(airports)} airports")
    
    nearby = wp_db.find_waypoints_in_radius(37.6213, -122.3790, 50)
    print(f"Found {len(nearby)} waypoints within 50nm of KSFO")
    
    # Statistics
    stats = wp_db.get_waypoint_statistics()
    print(f"\nDatabase statistics: {stats}")
    
    # Clean up
    wp_db.close()
    import os
    os.remove('test_waypoints.db')
    
    print("\nTest completed successfully!")
