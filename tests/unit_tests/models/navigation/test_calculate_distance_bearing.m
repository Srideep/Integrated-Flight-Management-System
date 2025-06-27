function tests = test_calculate_distance_bearing
% CALCULATE_DISTANCE_BEARING_TEST Unit tests for calculate_distance_bearing function.
%   This test suite verifies the accuracy of the calculate_distance_bearing function by
%   checking its results for a variety of scenarios, including basic usage and edge cases.
%
%   To run these tests, use the following command in MATLAB:
%       runtests('tests/unit_tests/models/navigation/calculate_distance_bearing_test.m')

    tests = functiontests(localfunctions);
end

function testBasicCalculation(testCase)
    % Test basic calculation with example inputs.
    %
    % For this test, we assume that moving from (0,0) to (1,0)
    % yields an approximate distance of 111.195 km (for 1 degree latitude difference)
    % and a bearing of 0 degrees (north).
    %
    % NOTE: These expected values are based on common approximations.
    % Adjust the expected values according to the actual implementation details
    % of calculate_distance_bearing.

    expectedDistance = 111.195;  % approximate distance in kilometers
    expectedBearing  = 0;         % bearing in degrees (north)

    % Call the function under test.
    [distance, bearing] = calculate_distance_bearing(0, 0, 1, 0);

    % Verify the computed values against the expected values.
    verifyEqual(testCase, distance, expectedDistance, 'AbsTol', 1e-2);
    verifyEqual(testCase, bearing, expectedBearing, 'AbsTol', 1e-2);
end

function testSamePoint(testCase)
    % Test the edge case where both points are identical.
    %
    % When the start and end points are the same, the expected behavior
    % is a distance of 0. The bearing is conventionally set to 0 as well.

    [distance, bearing] = calculate_distance_bearing(1, 1, 1, 1);
    verifyEqual(testCase, distance, 0, 'AbsTol', 1e-10);
    verifyEqual(testCase, bearing, 0, 'AbsTol', 1e-10);
end