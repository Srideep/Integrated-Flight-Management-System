% +test/tDistanceBearing.m
classdef tDistanceBearing < matlab.unittest.TestCase
    methods (Test)
        function goldenKLAX_KJFK(test)
            % Hand-checked truth via Jeppesen route planner
            [d,b] = calculate_distance_bearing( ...
                      33.9425,-118.4081, ... % KLAX
                      40.6397, -73.7789);    % KJFK
            test.verifyEqual(d,2146.3, 'AbsTol',0.5);   % NM
            test.verifyEqual(b,  65.871, 'AbsTol',0.5);    % deg
        end

        function vectorisedTwoPoints(test)
            lat1=[0 0]'; lon1=[0 0]';
            lat2=[0 1]'; lon2=[1 0]';
            [d,~] = calculate_distance_bearing(lat1,lon1,lat2,lon2);
            test.verifySize(d,[2 1]);              % proves .* path
        end
    end
end
