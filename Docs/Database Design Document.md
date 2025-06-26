# **Database Design Document (DDD)**

## **Integrated Flight Management System (FMS)**

| Document ID: | FMS-DDD-001 |
| :---- | :---- |
| **Version:** | 1.0 |
| **Date:** | June 20, 2025 |
| **Status:** | Baseline |

### **1\. Introduction**

#### **1.1 Purpose**

This document provides a comprehensive design specification for the navigation database used by the Integrated Flight Management System (FMS). It details the database schema, tables, data types, relationships, and indexes.

#### **1.2 Scope**

The scope is limited to the SQLite database files located in the data/nav\_database/ directory. This includes the database for waypoints, airways, and procedures.

### **2\. Database Design**

#### **2.1 Database System**

The FMS uses **SQLite 3** as its database engine. This was chosen for its serverless, self-contained, and file-based nature, which is ideal for an embedded or simulation environment.

#### **2.2 Entity-Relationship Diagram (ERD)**

\+----------------+      \+------------------+      \+-------------------+  
|    Airways     |      |  Airway\_Segments |      |     Waypoints     |  
\+----------------+      \+------------------+      \+-------------------+  
| PK airway\_id   |----\<| FK airway\_id     |      | PK waypoint\_id    |  
|    airway\_name |      |    segment\_order |-----\>|    identifier     |  
\+----------------+      | FK waypoint\_id   |      |    latitude       |  
                        \+------------------+      |    longitude      |  
                                                  |    waypoint\_type  |  
                                                  |    ... (etc)      |  
                                                  \+-------------------+

### **3\. Table Schemas**

#### **3.1 waypoints Table**

* **Description:** Stores all navigational points, including airports, VORs, NDBs, and intersections.  
* **Filename:** waypoints.db

| Column Name | Data Type | Constraints | Description |
| :---- | :---- | :---- | :---- |
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique internal identifier |
| identifier | TEXT | UNIQUE NOT NULL | Official 3-5 character identifier (e.g., KSFO) |
| latitude | REAL | NOT NULL CHECK (\>= \-90 AND \<= 90\) | Geodetic Latitude in decimal degrees |
| longitude | REAL | NOT NULL CHECK (\>= \-180 AND \<= 180\) | Geodetic Longitude in decimal degrees |
| altitude | REAL |  | Altitude constraint in feet (if applicable) |
| waypoint\_type | TEXT |  | Type of waypoint (AIRPORT, VOR, WAYPOINT) |
| frequency | REAL |  | Frequency for radio navaids (VOR, NDB) |
| region | TEXT |  | Geographic region code (e.g., CA for California) |
| country | TEXT |  | Country code (e.g., USA) |

#### **3.2 airways Table**

* **Description:** Stores information about published airways.  
* **Filename:** airways.db

| Column Name | Data Type | Constraints | Description |
| :---- | :---- | :---- | :---- |
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique internal identifier |
| name | TEXT | UNIQUE NOT NULL | Name of the airway (e.g., J501) |

#### **3.3 airway\_segments Table**

* **Description:** A linking table that defines the sequence of waypoints that make up an airway.  
* **Filename:** airways.db

| Column Name | Data Type | Constraints | Description |
| :---- | :---- | :---- | :---- |
| airway\_id | INTEGER | FOREIGN KEY (airways.id) | Links to the airways table |
| waypoint\_id | INTEGER | FOREIGN KEY (waypoints.id) | Links to the waypoints table |
| sequence\_order | INTEGER | NOT NULL | The order of the waypoint in the airway sequence |

### **4\. Database Indexes**

To ensure performance meets the requirements laid out in the SRS (PR-1.4), the following indexes are implemented:

* **idx\_waypoint\_location**: A composite index on the latitude and longitude columns of the waypoints table to accelerate geographic radius searches.  
* **idx\_waypoint\_type**: An index on the waypoint\_type column to speed up filtering by type.  
* **idx\_waypoint\_region**: A composite index on the region and country columns for fast regional queries.
### **5. Backup and Maintenance**

Database maintenance follows the guidance in the README configuration section. The system performs periodic backups based on `BACKUP_INTERVAL` and uses a connection pool to meet query performance targets.
