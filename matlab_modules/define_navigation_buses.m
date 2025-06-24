%% define_navigation_buses.m
% Define all bus objects for Navigation module

function define_navigation_buses()
    % Clear any existing bus definitions
    clear PositionBus WaypointBus NavigationBus FlightPlanBus
   
    % =================================================================
    % DEFINE POSITION BUS
    % =================================================================

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

    % =================================================================
    % DEFINE WAYPOINT BUS
    % =================================================================    
    WaypointBus = Simulink.Bus; 
    % -----------------------------------------
    
    % Clear and define elements
    clear elems;
    elems(1) = Simulink.BusElement;
    elems(1).Name = 'identifier';
    elems(1).DataType = 'uint8(5)'; % Using a fixed-size char array
    % ... (continue defining the rest of your elements for latitude, longitude, etc.) ...
    elems(2) = Simulink.BusElement;
    elems(2).Name = 'latitude';
    elems(2).DataType = 'double';
    
    % Assign the defined elements to the bus object
    WaypointBus.Elements = elems;
    
    % Add a description for clarity
    WaypointBus.Description = 'Structure for a single navigation waypoint.';

% Assign the fully created WaypointBus object to the base workspace
    
    % Save to base workspace and data dictionary
    assignin('base', 'PositionBus', PositionBus);
    assignin('base', 'WaypointBus', WaypointBus);
    assignin('base', 'NavigationBus', NavigationBus);
    assignin('base', 'FlightPlanBus', FlightPlanBus);
    
    % Save to MAT file for reuse
    save('data/navigation_buses.mat', 'PositionBus', 'WaypointBus', ...
         'NavigationBus', 'FlightPlanBus');
end