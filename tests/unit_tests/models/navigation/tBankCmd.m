% +test/tBankCmd.m
classdef tBankCmd < matlab.unittest.TestCase
    methods (Test)
        function zeroErrorGivesZeroBank(test)
            phi = calculate_bank_angle_cmd(0, 100);   %#ok<ASGLU>
            test.verifyEqual(phi,0);
        end

        function saturation(test)
            phi = calculate_bank_angle_cmd(-10,45);  % Left-of-leg 10 NM
% proportional term = -K*xte = 50 → saturated to +25 deg
            test.verifyEqual(phi,25);
        end
    end
end
