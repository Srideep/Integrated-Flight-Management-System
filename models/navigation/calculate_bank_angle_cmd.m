function bank_angle_deg = calculate_bank_angle_cmd(xte_nm, bearing_deg)
% CALCULATE_BANK_ANGLE_CMD Generate a commanded bank angle for LNAV
%
% Converts cross-track error to a bank angle command using a simple
% proportional guidance law referenced in the Real-Time Navigation Loop of
% the SDD (FMS-SDD-001). Output units are in degrees to match the
% NavigationBus specification in the ICD (FMS-ICD-001).
%
% Inputs:
%   xte_nm      - Cross-track error in nautical miles (positive = right of course)
%   bearing_deg - Desired course over ground in degrees (unused in this simple
%                 implementation but included for future expansion)
%
% Output:
%   bank_angle_deg - Commanded bank angle in degrees
%
% The algorithm uses a proportional gain with saturation:
%   bank_angle_deg = -K * xte_nm;
%   bank_angle_deg limited to +/- MAX_BANK.
%
% This provides a basic "fly-to" capability that rolls toward the desired
% course with the correct sign convention.

K = 5;           % Gain in degrees per nautical mile
MAX_BANK = 25;   % Saturation limit in degrees

bank_angle_deg = -K .* xte_nm;

bank_angle_deg(bank_angle_deg >  MAX_BANK) =  MAX_BANK;
bank_angle_deg(bank_angle_deg < -MAX_BANK) = -MAX_BANK;
end