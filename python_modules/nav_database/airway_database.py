import sqlite3
import os
from dataclasses import dataclass
from typing import List

@dataclass
class AirwaySegment:
    waypoint_id: str
    sequence_order: int

class AirwayDatabase:
    """Manage airway database with segments"""

    def __init__(self, db_path: str = 'data/nav_database/airways.db'):
        self.db_path = db_path
        self.connection = None
        self.initialize_database()

    def initialize_database(self):
        db_dir = os.path.dirname(self.db_path) or '.'
        os.makedirs(db_dir, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS airways (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS airway_segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                airway_id INTEGER,
                waypoint_id TEXT NOT NULL,
                sequence_order INTEGER NOT NULL,
                FOREIGN KEY(airway_id) REFERENCES airways(id)
            )
        ''')

        self.connection.commit()
        self._insert_sample_data()

    def _insert_sample_data(self):
        cursor = self.connection.cursor()

        # Airway V334
        cursor.execute('INSERT OR IGNORE INTO airways (name) VALUES (?)', ('V334',))
        cursor.execute('SELECT id FROM airways WHERE name=?', ('V334',))
        v334_id = cursor.fetchone()[0]

        v334_segments = [
            (v334_id, 'SFO', 1),
            (v334_id, 'WESLA', 2),
            (v334_id, 'KOAK', 3)
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO airway_segments (airway_id, waypoint_id, sequence_order)
            VALUES (?, ?, ?)
        ''', v334_segments)

        # Additional airway V135
        cursor.execute('INSERT OR IGNORE INTO airways (name) VALUES (?)', ('V135',))
        cursor.execute('SELECT id FROM airways WHERE name=?', ('V135',))
        v135_id = cursor.fetchone()[0]

        v135_segments = [
            (v135_id, 'SFO', 1),
            (v135_id, 'CNDEL', 2),
            (v135_id, 'KOAK', 3)
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO airway_segments (airway_id, waypoint_id, sequence_order)
            VALUES (?, ?, ?)
        ''', v135_segments)

        # Additional airway V200
        cursor.execute('INSERT OR IGNORE INTO airways (name) VALUES (?)', ('V200',))
        cursor.execute('SELECT id FROM airways WHERE name=?', ('V200',))
        v200_id = cursor.fetchone()[0]

        v200_segments = [
            (v200_id, 'KOAK', 1),
            (v200_id, 'REJOY', 2),
            (v200_id, 'SFO', 3)
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO airway_segments (airway_id, waypoint_id, sequence_order)
            VALUES (?, ?, ?)
        ''', v200_segments)

        self.connection.commit()

    def get_airway_waypoints(self, airway_name: str) -> List[str]:
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT waypoint_id FROM airway_segments
            JOIN airways ON airways.id = airway_segments.airway_id
            WHERE airways.name = ?
            ORDER BY sequence_order
        ''', (airway_name,))
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
