% +test/tCrossTrack.m
classdef tCrossTrack < matlab.unittest.TestCase
    methods (Test)
        function onLegIsZero(test)
            xte = calculate_cross_track_error( ...
                     51,-1, 51,-1, 52,0);        % start & current coincide
            test.verifyEqual(xte,0,'AbsTol',1e-9);
        end

        function signConvention(test)
            % Point 5 NM right of a due-north leg
            xte = calculate_cross_track_error( ...
                     51.0417,-0.0833, 51,-1, 52,-1);  % ≈5 NM east
            test.verifyGreaterThan(xte,0);           % right of course ⇒ +
        end
    end
end
