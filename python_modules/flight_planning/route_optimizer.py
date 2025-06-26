
"""
Route Optimizer for Flight Management System

This module provides route optimization capabilities for flight plans,
integrating with the FlightPlanManager as specified in the implementation checklist.
"""

import math
import logging
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass

from .flight_plan_manager import FlightPlan, FlightPlanWaypoint

logger = logging.getLogger(__name__)

@dataclass
class OptimizationResult:
    """Result of route optimization"""
    optimized_plan: FlightPlan
    original_distance: float
    optimized_distance: float
    distance_saved: float
    time_saved: float  # in minutes
    fuel_saved: float  # in pounds (estimated)

class RouteOptimizer:
    """Route optimization engine for flight plans"""
    
    def __init__(self):
        """Initialize the route optimizer"""
        self.optimization_algorithms = {
            'shortest_distance': self._optimize_shortest_distance,
            'fuel_efficient': self._optimize_fuel_efficient,
            'time_efficient': self._optimize_time_efficient
        }
    
    def optimize_flight_plan(self, flight_plan: FlightPlan, 
                           algorithm: str = 'shortest_distance',
                           constraints: Optional[Dict[str, Any]] = None) -> OptimizationResult:
        """
        Optimize a flight plan using specified algorithm
        
        Args:
            flight_plan: The flight plan to optimize
            algorithm: Optimization algorithm to use
            constraints: Optional constraints (weather, NOTAMs, etc.)
        
        Returns:
            OptimizationResult with optimized plan and metrics
        """
        if algorithm not in self.optimization_algorithms:
            raise ValueError(f"Unknown optimization algorithm: {algorithm}")
        
        logger.info(f"Optimizing flight plan {flight_plan.name} using {algorithm}")
        
        # Calculate original route metrics
        original_distance = self._calculate_total_distance(flight_plan.waypoints)
        
        # Apply optimization algorithm
        optimization_func = self.optimization_algorithms[algorithm]
        optimized_waypoints = optimization_func(flight_plan.waypoints, constraints)
        
        # Create optimized flight plan
        optimized_plan = FlightPlan(
            name=f"{flight_plan.name}_OPTIMIZED",
            departure=flight_plan.departure,
            arrival=flight_plan.arrival,
            waypoints=optimized_waypoints,
            cruise_altitude=flight_plan.cruise_altitude,
            cruise_speed=flight_plan.cruise_speed,
            created_date=flight_plan.created_date
        )
        
        # Calculate optimized metrics
        optimized_distance = self._calculate_total_distance(optimized_waypoints)
        distance_saved = original_distance - optimized_distance
        
        # Estimate time and fuel savings
        time_saved = self._estimate_time_savings(distance_saved, flight_plan.cruise_speed)
        fuel_saved = self._estimate_fuel_savings(distance_saved, time_saved)
        
        result = OptimizationResult(
            optimized_plan=optimized_plan,
            original_distance=original_distance,
            optimized_distance=optimized_distance,
            distance_saved=distance_saved,
            time_saved=time_saved,
            fuel_saved=fuel_saved
        )
        
        logger.info(f"Optimization complete: {distance_saved:.1f} nm saved, {time_saved:.1f} min faster")
        
        return result
    
    def _optimize_shortest_distance(self, waypoints: List[FlightPlanWaypoint], 
                                   constraints: Optional[Dict[str, Any]] = None) -> List[FlightPlanWaypoint]:
        """Optimize for shortest total distance"""
        if len(waypoints) <= 2:
            return waypoints
        
        # Keep departure and arrival fixed
        departure = waypoints[0]
        arrival = waypoints[-1]
        intermediate = waypoints[1:-1]
        
        if len(intermediate) <= 1:
            return waypoints
        
        # Apply simple nearest neighbor optimization to intermediate waypoints
        optimized_intermediate = self._nearest_neighbor_optimization(departure, arrival, intermediate)
        
        return [departure] + optimized_intermediate + [arrival]
    
    def _optimize_fuel_efficient(self, waypoints: List[FlightPlanWaypoint], 
                                constraints: Optional[Dict[str, Any]] = None) -> List[FlightPlanWaypoint]:
        """Optimize for fuel efficiency (considering winds, weather, etc.)"""
        # For now, use distance optimization as proxy
        # In real implementation, would consider:
        # - Wind patterns
        # - Altitude optimization
        # - Weather avoidance
        # - Air traffic patterns
        
        return self._optimize_shortest_distance(waypoints, constraints)
    
    def _optimize_time_efficient(self, waypoints: List[FlightPlanWaypoint], 
                                constraints: Optional[Dict[str, Any]] = None) -> List[FlightPlanWaypoint]:
        """Optimize for minimum flight time"""
        # For now, use distance optimization as proxy
        # In real implementation, would consider:
        # - Jet stream patterns
        # - Air traffic delays
        # - Airport congestion
        # - Preferred routes
        
        return self._optimize_shortest_distance(waypoints, constraints)
    
    def _nearest_neighbor_optimization(self, start: FlightPlanWaypoint, 
                                     end: FlightPlanWaypoint,
                                     intermediate: List[FlightPlanWaypoint]) -> List[FlightPlanWaypoint]:
        """Simple nearest neighbor optimization for intermediate waypoints"""
        if not intermediate:
            return []
        
        if len(intermediate) == 1:
            return intermediate
        
        # Start from departure point
        current_point = start
        remaining = intermediate.copy()
        optimized_route = []
        
        # Greedily select nearest remaining waypoint
        while remaining:
            nearest_idx = 0
            nearest_distance = self._calculate_distance(current_point, remaining[0])
            
            for i, waypoint in enumerate(remaining[1:], 1):
                distance = self._calculate_distance(current_point, waypoint)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_idx = i
            
            # Add nearest waypoint to route
            nearest_waypoint = remaining.pop(nearest_idx)
            optimized_route.append(nearest_waypoint)
            current_point = nearest_waypoint
        
        return optimized_route
    
    def _calculate_distance(self, wp1: FlightPlanWaypoint, wp2: FlightPlanWaypoint) -> float:
        """Calculate great circle distance between two waypoints in nautical miles"""
        lat1_rad = math.radians(wp1.latitude)
        lon1_rad = math.radians(wp1.longitude)
        lat2_rad = math.radians(wp2.latitude)
        lon2_rad = math.radians(wp2.longitude)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        # Earth radius in nautical miles
        earth_radius_nm = 3440.065
        
        return earth_radius_nm * c
    
    def _calculate_total_distance(self, waypoints: List[FlightPlanWaypoint]) -> float:
        """Calculate total route distance"""
        if len(waypoints) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(waypoints) - 1):
            total_distance += self._calculate_distance(waypoints[i], waypoints[i + 1])
        
        return total_distance
    
    def _estimate_time_savings(self, distance_saved: float, cruise_speed: int) -> float:
        """Estimate time savings in minutes"""
        if cruise_speed <= 0:
            return 0.0
        
        # Convert knots to nm/min
        speed_nm_per_min = cruise_speed / 60.0
        
        return distance_saved / speed_nm_per_min
    
    def _estimate_fuel_savings(self, distance_saved: float, time_saved: float) -> float:
        """Estimate fuel savings in pounds"""
        # Rough estimation: typical jet fuel consumption
        # For a medium jet: ~200 lbs/hour at cruise
        fuel_flow_lbs_per_minute = 200.0 / 60.0
        
        return time_saved * fuel_flow_lbs_per_minute
    
    def analyze_route_efficiency(self, flight_plan: FlightPlan) -> Dict[str, Any]:
        """Analyze current route efficiency and provide recommendations"""
        waypoints = flight_plan.waypoints
        
        if len(waypoints) < 2:
            return {"status": "insufficient_waypoints"}
        
        # Calculate current route metrics
        total_distance = self._calculate_total_distance(waypoints)
        direct_distance = self._calculate_distance(waypoints[0], waypoints[-1])
        
        # Calculate route efficiency
        efficiency = (direct_distance / total_distance) * 100 if total_distance > 0 else 0
        
        # Identify potential improvements
        recommendations = []
        
        if efficiency < 85:
            recommendations.append("Route is significantly longer than direct path")
        
        if len(waypoints) > 5:
            recommendations.append("Consider reducing number of intermediate waypoints")
        
        # Check for obvious detours
        max_deviation = 0
        for i in range(1, len(waypoints) - 1):
            # Calculate distance from direct path
            deviation = self._calculate_deviation_from_direct_path(
                waypoints[0], waypoints[-1], waypoints[i]
            )
            max_deviation = max(max_deviation, deviation)
        
        if max_deviation > 50:  # 50 nm deviation
            recommendations.append("Route contains significant detours")
        
        return {
            "status": "analyzed",
            "total_distance_nm": total_distance,
            "direct_distance_nm": direct_distance,
            "efficiency_percent": efficiency,
            "max_deviation_nm": max_deviation,
            "recommendations": recommendations,
            "optimization_potential": 100 - efficiency
        }
    
    def _calculate_deviation_from_direct_path(self, start: FlightPlanWaypoint, 
                                            end: FlightPlanWaypoint, 
                                            point: FlightPlanWaypoint) -> float:
        """Calculate how far a point deviates from the direct path"""
        # Simplified calculation - in reality would use great circle math
        # This is an approximation for small distances
        
        # Convert to Cartesian for easier calculation
        start_x = start.longitude
        start_y = start.latitude
        end_x = end.longitude
        end_y = end.latitude
        point_x = point.longitude
        point_y = point.latitude
        
        # Calculate perpendicular distance to line
        A = end_y - start_y
        B = start_x - end_x
        C = end_x * start_y - start_x * end_y
        
        distance = abs(A * point_x + B * point_y + C) / math.sqrt(A*A + B*B)
        
        # Convert to nautical miles (rough approximation)
        return distance * 60  # 1 degree ≈ 60 nm

def optimize_flight_plan_simple(flight_plan: FlightPlan) -> OptimizationResult:
    """Simple function interface for flight plan optimization"""
    optimizer = RouteOptimizer()
    return optimizer.optimize_flight_plan(flight_plan)

# Integration function for FlightPlanManager
def integrate_with_flight_plan_manager():
    """Demonstrate integration with FlightPlanManager"""
    logger.info("Route optimizer ready for FlightPlanManager integration")
    
    # This function would be called by FlightPlanManager.optimize_active_plan()
    # to provide the actual optimization logic
    
    return RouteOptimizer()
