% +test/test_navigation_calculations.m
classdef test_navigation_calculations < matlab.unittest.TestCase
    properties
        Model = fullfile('models','navigation','Navigation_Calculations.slx');
    end
    methods (TestClassSetup)
        function loadModel(testCase)
            load_system(testCase.Model);
        end
    end
    methods (TestClassTeardown)
        function closeModel(testCase)
            close_system(testCase.Model,0);
        end
    end
    methods (Test)
        function simpleScenario(testCase)
            define_navigation_buses;

            % Input scenario
            pos.Latitude = 0;
            pos.Longitude = 0.5;
            pos.Altitude = 0;

            startLat = 0;
            startLon = 0;
            endLat   = 0;
            endLon   = 1;

            ds = Simulink.SimulationData.Dataset;
            ds = addElement(ds, timeseries(pos,0), 'Aicraft_Position');
            ds = addElement(ds, timeseries(startLat,0), 'Start_Waypoint_Lat');
            ds = addElement(ds, timeseries(startLon,0), 'Start_Waypoint_Lon');
            ds = addElement(ds, timeseries(endLat,0), 'End_Waypoint_Lat');
            ds = addElement(ds, timeseries(endLon,0), 'End_Waypoint_Lon');

            simOut = sim(testCase.Model, 'StopTime','0', ...
                'LoadExternalInput','on', 'ExternalInput','ds', ...
                'SaveOutput','on', 'SaveFormat','Dataset', ...
                'ReturnWorkspaceOutputs','on');

            navTS = simOut.yout.getElement('Navigation_Commands').Values;
            nav = navTS.Data(1);

            [dist,bearing] = calculate_distance_bearing(pos.Latitude,pos.Longitude,endLat,endLon);
            xte = calculate_cross_track_error(pos.Latitude,pos.Longitude,startLat,startLon,endLat,endLon);
            bank = calculate_bank_angle_cmd(xte,bearing);

            testCase.verifyEqual(nav.DistanceToGo, dist, 'AbsTol', 1e-3);
            testCase.verifyEqual(nav.DesiredCourse, bearing, 'AbsTol', 1e-3);
            testCase.verifyEqual(nav.CrossTrackError, xte, 'AbsTol', 1e-3);
            testCase.verifyEqual(nav.BankAngleCmd, bank, 'AbsTol', 1e-3);
        end
    end
end
