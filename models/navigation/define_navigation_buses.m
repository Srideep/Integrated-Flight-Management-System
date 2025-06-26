%% define_navigation_buses
% This script programmatically defines all Simulink.Bus objects required for
% the Integrated Flight Management System. Running this script ensures that
% all data signals in the Simulink models have a consistent and well-defined
% structure, which is critical for robust model design and integration.
%
% This script directly implements the bus structures defined in the
% Interface Control Document (FMS-ICD-001).

function define_navigation_buses()
    % --- 1. Cleanup Phase ---
    % Clear any bus objects from previous runs to ensure a clean state.
    clear PositionBus WaypointBus NavigationBus FlightPlanBus;


    % =================================================================
    % DEFINE PositionBus
    % =================================================================
    % This bus carries the aircraft's fundamental position data.

    % Create an array to hold the elements of the bus
    PositionElements(1) = Simulink.BusElement;
    PositionElements(1).Name = 'Latitude';
    PositionElements(1).DataType = 'double';
    PositionElements(1).Min = -90;
    PositionElements(1).Max = 90;
    PositionElements(1).Unit = 'deg';

    PositionElements(2) = Simulink.BusElement;
    PositionElements(2).Name = 'Longitude';
    PositionElements(2).DataType = 'double';
    PositionElements(2).Min = -180;
    PositionElements(2).Max = 180;
    PositionElements(2).Unit = 'deg';

    PositionElements(3) = Simulink.BusElement;
    PositionElements(3).Name = 'Altitude';
    PositionElements(3).DataType = 'double';
    PositionElements(3).Min = -5000; % Allow for ground elevation variance
    PositionElements(3).Max = 60000;
    PositionElements(3).Unit = 'ft';

    % Create the bus object itself
    PositionBus = Simulink.Bus;
    PositionBus.Elements = PositionElements;
    PositionBus.Description = 'Contains the aircraft''s current position.';

    % =================================================================
    % DEFINE WaypointBus
    % =================================================================
    % This bus defines the structure for a single waypoint. It will be
    % nested inside the FlightPlanBus.

    
    WaypointBus = Simulink.Bus;

    WaypointElements(1) = Simulink.BusElement;
    WaypointElements(1).Name = 'identifier';
    WaypointElements(1).DataType = 'uint8'; % Store string as ASCII values
    WaypointElements(1).Dimensions = [1 5];  % Fixed size for a 5-char identifier

    WaypointElements(2) = Simulink.BusElement;
    WaypointElements(2).Name = 'latitude';
    WaypointElements(2).DataType = 'double';

    WaypointElements(3) = Simulink.BusElement;
    WaypointElements(3).Name = 'longitude';
    WaypointElements(3).DataType = 'double';

    WaypointElements(4) = Simulink.BusElement;
    WaypointElements(4).Name = 'altitude_constraint';
    WaypointElements(4).DataType = 'double';
    WaypointElements(4).Unit = 'ft';

    % Assign the elements to the bus object
    WaypointBus.Elements = WaypointElements;
    WaypointBus.Description = 'Defines the data structure for a single waypoint.';

    % =================================================================
    % DEFINE NavigationBus
    % =================================================================
    % This bus carries the output of the navigation calculations, which
    % are used by the guidance and display systems.

    
    NavigationBus = Simulink.Bus;

    NavigationElements(1) = Simulink.BusElement;
    NavigationElements(1).Name = 'CrossTrackError';
    NavigationElements(1).DataType = 'double';
    NavigationElements(1).Unit = 'nautical_miles';

    NavigationElements(2) = Simulink.BusElement;
    NavigationElements(2).Name = 'DistanceToGo';
    NavigationElements(2).DataType = 'double';
    NavigationElements(2).Unit = 'nautical_miles';

    NavigationElements(3) = Simulink.BusElement;
    NavigationElements(3).Name = 'DesiredCourse';
    NavigationElements(3).DataType = 'double';
    NavigationElements(3).Unit = 'deg';

    NavigationElements(4) = Simulink.BusElement;
    NavigationElements(4).Name = 'BankAngleCmd';
    NavigationElements(4).DataType = 'double';
    NavigationElements(4).Unit = 'degrees';

    % Assign the elements to the bus object
    NavigationBus.Elements = NavigationElements;
    NavigationBus.Description = 'Contains outputs of the core navigation calculations.';

    % =================================================================
    % DEFINE FlightPlanBus
    % =================================================================
    % This bus represents a complete flight plan, containing an array of
    % WaypointBus objects.

    FlightPlanBus = Simulink.Bus;

    FlightPlanElements(1) = Simulink.BusElement;
    FlightPlanElements(1).Name = 'waypoints';
    FlightPlanElements(1).DataType = 'Bus: WaypointBus'; % Nested bus
    FlightPlanElements(1).Dimensions = [20 1];  % Max 20 waypoints per plan

    FlightPlanElements(2) = Simulink.BusElement;
    FlightPlanElements(2).Name = 'numWaypoints';
    FlightPlanElements(2).DataType = 'uint8';

    FlightPlanBus.Elements = FlightPlanElements;
    FlightPlanBus.Description = 'Contains the active flight plan as an array of waypoints.';

    % --- 2. Assignment Phase ---
    % Save the newly created bus objects to MATLAB's base workspace so
    % Simulink models can see and use them.
    assignin('base', 'PositionBus', PositionBus);
    assignin('base', 'WaypointBus', WaypointBus);
    assignin('base', 'NavigationBus', NavigationBus);
    assignin('base', 'FlightPlanBus', FlightPlanBus);

    fprintf('Navigation bus objects have been defined in the base workspace.\n');

    % --- 3. Persistence Phase ---
    % Save the bus definitions to a MAT file. This allows them to be
    % loaded quickly in future sessions without re-running this script.
    
    outputFolder = fullfile('/MATLAB Drive/Projects/FMS_Integrated_System/data');

    % Create the output folder if it doesn't exist
    if ~exist(outputFolder, 'dir')
       mkdir(outputFolder)
    end
    
    filePath = fullfile(outputFolder, 'navigation_buses.mat');
    save(filePath);
        
    fprintf('Bus definitions saved to %s\n', filePath);
end
