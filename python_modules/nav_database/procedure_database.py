import sqlite3
import os
from dataclasses import dataclass
from typing import List

@dataclass
class ProcedureSegment:
    waypoint_id: str
    sequence_order: int

class ProcedureDatabase:
    """Manage standard procedure database"""

    def __init__(self, db_path: str = 'data/nav_database/procedures.db'):
        self.db_path = db_path
        self.connection = None
        self.initialize_database()

    def initialize_database(self):
        db_dir = os.path.dirname(self.db_path) or '.'
        os.makedirs(db_dir, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS procedures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS procedure_segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                procedure_id INTEGER,
                waypoint_id TEXT NOT NULL,
                sequence_order INTEGER NOT NULL,
                FOREIGN KEY(procedure_id) REFERENCES procedures(id)
            )
        ''')

        self.connection.commit()
        self._insert_sample_data()

    def _insert_sample_data(self):
        cursor = self.connection.cursor()
        # SID procedure
        cursor.execute('INSERT OR IGNORE INTO procedures (name, type) VALUES (?, ?)',
                       ('TEST_SID', 'SID'))
        cursor.execute('SELECT id FROM procedures WHERE name=?', ('TEST_SID',))
        sid_id = cursor.fetchone()[0]
        sid_segments = [
            (sid_id, 'KSFO', 1),
            (sid_id, 'SFO', 2),
            (sid_id, 'WESLA', 3)
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO procedure_segments (procedure_id, waypoint_id, sequence_order)
            VALUES (?, ?, ?)
        ''', sid_segments)

        # STAR procedure
        cursor.execute('INSERT OR IGNORE INTO procedures (name, type) VALUES (?, ?)',
                       ('TEST_STAR', 'STAR'))
        cursor.execute('SELECT id FROM procedures WHERE name=?', ('TEST_STAR',))
        star_id = cursor.fetchone()[0]
        star_segments = [
            (star_id, 'KOAK', 1),
            (star_id, 'REJOY', 2),
            (star_id, 'SFO', 3),
            (star_id, 'KSFO', 4)
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO procedure_segments (procedure_id, waypoint_id, sequence_order)
            VALUES (?, ?, ?)
        ''', star_segments)

        # Approach procedure
        cursor.execute('INSERT OR IGNORE INTO procedures (name, type) VALUES (?, ?)',
                       ('TEST_APP', 'APP'))
        cursor.execute('SELECT id FROM procedures WHERE name=?', ('TEST_APP',))
        app_id = cursor.fetchone()[0]
        app_segments = [
            (app_id, 'FAITH', 1),
            (app_id, 'WESLA', 2),
            (app_id, 'KSFO', 3)
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO procedure_segments (procedure_id, waypoint_id, sequence_order)
            VALUES (?, ?, ?)
        ''', app_segments)
        self.connection.commit()

    def get_procedure_waypoints(self, name: str) -> List[str]:
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT waypoint_id FROM procedure_segments
            JOIN procedures ON procedures.id = procedure_segments.procedure_id
            WHERE procedures.name = ?
            ORDER BY sequence_order
        ''', (name,))
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
