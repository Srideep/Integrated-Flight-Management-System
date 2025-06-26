function [distance_nm, bearing_deg] = calculate_distance_bearing(lat1_deg, lon1_deg, lat2_deg, lon2_deg)
% CALCULATE_DISTANCE_BEARING Great-circle distance and initial bearing
%
% Implements the Haversine distance and bearing formulas referenced in the
% Real-Time Navigation Loop section of the SDD (FMS-SDD-001) and aligns with
% the NavigationBus definitions in the ICD (FMS-ICD-001).
%
% Inputs are geographic coordinates in degrees. Outputs are distance in
% nautical miles and bearing in degrees.

% Convert degrees to radians
lat1 = deg2rad(lat1_deg);
lon1 = deg2rad(lon1_deg);
lat2 = deg2rad(lat2_deg);
lon2 = deg2rad(lon2_deg);

% Haversine formula for distance
dlat = lat2 - lat1;
dlon = lon2 - lon1;
a = sin(dlat/2).^2 + cos(lat1).*cos(lat2).*sin(dlon/2).^2;
c = 2 .* atan2(sqrt(a), sqrt(1-a));

% Earth radius in nautical miles
R = 3440.065;

distance_nm = R .* c;

% Initial bearing calculation
y = sin(dlon) .* cos(lat2);
x = cos(lat1).*sin(lat2) - sin(lat1).*cos(lat2).*cos(dlon);

bearing_rad = atan2(y, x);

% Normalize to 0-360 degrees
bearing_deg = mod(rad2deg(bearing_rad) + 360, 360);
end
