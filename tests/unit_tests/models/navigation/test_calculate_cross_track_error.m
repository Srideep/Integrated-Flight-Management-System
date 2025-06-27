function tests = test_calculate_cross_track_error
    tests = functiontests(localfunctions);
end

function test_OnTrack(testCase)
    xte = calculate_cross_track_error(0, 0.5, 0, 0, 0, 1);
    testCase.verifyEqual(xte, 0, 'AbsTol', 1e-6);
end

function test_LeftOfCourse(testCase)
    xte = calculate_cross_track_error(1, 0.5, 0, 0, 0, 1);
    expected = -60.04046;
    testCase.verifyEqual(xte, expected, 'AbsTol', 0.01);
end

function test_RightOfCourse(testCase)
    xte = calculate_cross_track_error(-1, 0.5, 0, 0, 0, 1);
    expected = 60.04046;
    testCase.verifyEqual(xte, expected, 'AbsTol', 0.01);
end
