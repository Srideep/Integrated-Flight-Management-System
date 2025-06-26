function xte_nm = calculate_cross_track_error(lat_deg, lon_deg, start_lat_deg, start_lon_deg, end_lat_deg, end_lon_deg)
% CALCULATE_CROSS_TRACK_ERROR Compute perpendicular distance to a flight leg
%
% Implements the cross-track error equation referenced in the Real-Time
% Navigation Loop of the SDD (FMS-SDD-001). Output units correspond to the
% NavigationBus specification in the ICD (FMS-ICD-001).
%
% Inputs are current position and leg endpoints in degrees. Output is the
% signed cross-track error in nautical miles (positive = right of course).

% Convert degrees to radians
lat = deg2rad(lat_deg);
lon = deg2rad(lon_deg);
start_lat = deg2rad(start_lat_deg);
start_lon = deg2rad(start_lon_deg);
end_lat = deg2rad(end_lat_deg);
end_lon = deg2rad(end_lon_deg);

% Earth radius in nautical miles
R = 3440.065;

% Distance and bearings from start point
d13 = 2 .* asin( sqrt( sin((lat - start_lat)/2).^2 + ...
                     cos(start_lat).*cos(lat).*sin((lon - start_lon)/2).^2 ) );

bearing13 = atan2( sin(lon - start_lon).*cos(lat), ...
                   cos(start_lat).*sin(lat) - sin(start_lat).*cos(lat).*cos(lon - start_lon) );

bearing12 = atan2( sin(end_lon - start_lon).*cos(end_lat), ...
                   cos(start_lat).*sin(end_lat) - sin(start_lat).*cos(end_lat).*cos(end_lon - start_lon) );

% Cross-track error in radians
xte_rad = asin( sin(d13) .* sin(bearing13 - bearing12) );

xte_nm = R .* xte_rad;
end
