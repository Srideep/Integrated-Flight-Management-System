function nav = Navigation_Logic(position)
%#codegen
% position : struct with fields Latitude, Longitude, Altitude (deg,deg,ft)
% nav      : NavigationBus struct

nav = struct( ...
    'CrossTrackError',0, ...
    'DistanceToGo',   0, ...
    'DesiredCourse',  0, ...
    'BankAngleCmd',   0);

% -- example placeholder math (replace with real great-circle logic) --
[dist,bear]  = computeDistanceAndBearing(position.Latitude,position.Longitude);
xte          = computeCrossTrackError(position.Latitude,position.Longitude);
nav.CrossTrackError = xte;
nav.DistanceToGo    = dist;
nav.DesiredCourse   = bear;
nav.BankAngleCmd    = computeBankAngle(xte,dist,bear);
