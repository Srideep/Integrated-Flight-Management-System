%% define_navigation_buses.m
% Define all bus objects for Navigation module

function define_navigation_buses()
    % Clear any existing bus definitions
    clear PositionBus WaypointBus NavigationBus FlightPlanBus
    
    % Position Bus
    PositionElements(1) = Simulink.BusElement;
    PositionElements(1).Name = 'latitude';
    PositionElements(1).DataType = 'double';
    PositionElements(1).Min = -90;
    PositionElements(1).Max = 90;
    PositionElements(1).Unit = 'deg';
    
    PositionElements(2) = Simulink.BusElement;
    PositionElements(2).Name = 'longitude';
    PositionElements(2).DataType = 'double';
    PositionElements(2).Min = -180;
    PositionElements(2).Max = 180;
    PositionElements(2).Unit = 'deg';
    
    PositionElements(3) = Simulink.BusElement;
    PositionElements(3).Name = 'altitude';
    PositionElements(3).DataType = 'double';
    PositionElements(3).Min = 0;
    PositionElements(3).Max = 50000;
    PositionElements(3).Unit = 'ft';
    
    PositionBus = Simulink.Bus;
    PositionBus.Elements = PositionElements;
    
    % Flight Plan Bus (array of waypoints)
    FlightPlanElements(1) = Simulink.BusElement;
    FlightPlanElements(1).Name = 'waypoints';
    FlightPlanElements(1).DataType = 'Bus: WaypointBus';
    FlightPlanElements(1).Dimensions = [20 1];  % Max 20 waypoints
    
    FlightPlanElements(2) = Simulink.BusElement;
    FlightPlanElements(2).Name = 'numWaypoints';
    FlightPlanElements(2).DataType = 'uint8';
    
    FlightPlanBus = Simulink.Bus;
    FlightPlanBus.Elements = FlightPlanElements;
    
    % Save to base workspace and data dictionary
    assignin('base', 'PositionBus', PositionBus);
    assignin('base', 'WaypointBus', WaypointBus);
    assignin('base', 'NavigationBus', NavigationBus);
    assignin('base', 'FlightPlanBus', FlightPlanBus);
    
    % Save to MAT file for reuse
    save('data/navigation_buses.mat', 'PositionBus', 'WaypointBus', ...
         'NavigationBus', 'FlightPlanBus');
end