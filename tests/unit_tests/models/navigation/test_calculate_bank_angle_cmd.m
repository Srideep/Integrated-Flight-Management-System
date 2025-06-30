function tests = test_calculate_bank_angle_cmd
    tests = functiontests(localfunctions);
end

function test_ZeroError(testCase)
    ba = calculate_bank_angle_cmd(0, 90);
    testCase.verifyEqual(ba, 0, 'AbsTol', 1e-6);
end

function test_LeftOfCourse(testCase)
    % Negative cross-track means left of course -> positive bank command
    ba = calculate_bank_angle_cmd(-2, 90);
    testCase.verifyEqual(ba, 10, 'AbsTol', 1e-6);
end

function test_RightOfCourse(testCase)
    % Positive cross-track means right of course -> negative bank command
    ba = calculate_bank_angle_cmd(2, 90);
    testCase.verifyEqual(ba, -10, 'AbsTol', 1e-6);
end

function test_Saturation(testCase)
    % Large error should saturate at +/-25 deg
    ba = calculate_bank_angle_cmd(10, 90);
    testCase.verifyEqual(ba, -25, 'AbsTol', 1e-6);
end
