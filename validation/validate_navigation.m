%% Navigation Calculations Test Data Generator
% This script generates comprehensive test data for navigation subsystem testing
% Author: Test Data Generator
% Date: 2025-07-07

clear all; close all; clc;

%% Test Configuration
numSamples = 1000;          % Number of test samples
sampleTime = 0.01;          % Sample time in seconds (100 Hz)
testDuration = numSamples * sampleTime;
time = (0:numSamples-1)' * sampleTime;

%% 1. GPS/GNSS Test Data
% Simulate GPS measurements with realistic noise and errors
GPS.latitude = 40.7128 + 0.001*sin(2*pi*0.1*time) + 1e-5*randn(numSamples,1);  % New York lat (deg)
GPS.longitude = -74.0060 + 0.001*cos(2*pi*0.1*time) + 1e-5*randn(numSamples,1); % New York lon (deg)
GPS.altitude = 100 + 10*sin(2*pi*0.05*time) + 0.5*randn(numSamples,1);          % Altitude (m)
GPS.numSatellites = randi([4, 12], numSamples, 1);                              % Number of satellites
GPS.HDOP = 1 + 0.5*rand(numSamples,1);                                         % Horizontal dilution of precision
GPS.velocity_north = 5*sin(2*pi*0.1*time) + 0.1*randn(numSamples,1);           % North velocity (m/s)
GPS.velocity_east = 5*cos(2*pi*0.1*time) + 0.1*randn(numSamples,1);            % East velocity (m/s)
GPS.velocity_down = -0.5*sin(2*pi*0.05*time) + 0.05*randn(numSamples,1);       % Down velocity (m/s)
GPS.timestamp = time;

%% 2. IMU (Inertial Measurement Unit) Test Data
% Simulate accelerometer and gyroscope measurements
IMU.accel_x = 0.5*sin(2*pi*0.5*time) + 0.01*randn(numSamples,1);              % X acceleration (m/s²)
IMU.accel_y = 0.3*cos(2*pi*0.5*time) + 0.01*randn(numSamples,1);              % Y acceleration (m/s²)
IMU.accel_z = -9.81 + 0.1*sin(2*pi*0.2*time) + 0.01*randn(numSamples,1);      % Z acceleration (m/s²)
IMU.gyro_x = 0.1*sin(2*pi*0.3*time) + 0.001*randn(numSamples,1);              % X angular rate (rad/s)
IMU.gyro_y = 0.1*cos(2*pi*0.3*time) + 0.001*randn(numSamples,1);              % Y angular rate (rad/s)
IMU.gyro_z = 0.05*sin(2*pi*0.1*time) + 0.001*randn(numSamples,1);             % Z angular rate (rad/s)
IMU.temperature = 25 + 5*sin(2*pi*0.01*time) + 0.1*randn(numSamples,1);        % Temperature (°C)
IMU.timestamp = time;

%% 3. Magnetometer Test Data
% Simulate magnetic field measurements
magField = 50;  % Earth's magnetic field strength (μT)
declination = 13.5 * pi/180;  % Magnetic declination (rad)
MAG.mag_x = magField*cos(declination) + 2*randn(numSamples,1);                 % X magnetic field (μT)
MAG.mag_y = magField*sin(declination) + 2*randn(numSamples,1);                 % Y magnetic field (μT)
MAG.mag_z = -40 + 2*randn(numSamples,1);                                       % Z magnetic field (μT)
MAG.timestamp = time;

%% 4. Barometer Test Data
% Simulate barometric pressure and altitude
seaLevelPressure = 101325;  % Pa
BARO.pressure = seaLevelPressure * (1 - 0.0065*GPS.altitude/288.15).^5.256;    % Pressure (Pa)
BARO.pressure = BARO.pressure + 10*randn(numSamples,1);                        % Add noise
BARO.temperature = 20 + 5*sin(2*pi*0.01*time) + 0.5*randn(numSamples,1);       % Temperature (°C)
BARO.altitude = GPS.altitude + 1*randn(numSamples,1);                          % Barometric altitude (m)
BARO.timestamp = time;

%% 5. Vehicle Dynamics Test Data
% Simulate vehicle speed and steering angle (for ground vehicles)
VEHICLE.speed = 20 + 10*sin(2*pi*0.05*time) + 0.5*randn(numSamples,1);         % Vehicle speed (m/s)
VEHICLE.speed(VEHICLE.speed < 0) = 0;                                          % Ensure non-negative
VEHICLE.steering_angle = 0.1*sin(2*pi*0.1*time) + 0.01*randn(numSamples,1);    % Steering angle (rad)
VEHICLE.wheel_speed_FL = VEHICLE.speed + 0.1*randn(numSamples,1);              % Front left wheel
VEHICLE.wheel_speed_FR = VEHICLE.speed + 0.1*randn(numSamples,1);              % Front right wheel
VEHICLE.wheel_speed_RL = VEHICLE.speed + 0.1*randn(numSamples,1);              % Rear left wheel
VEHICLE.wheel_speed_RR = VEHICLE.speed + 0.1*randn(numSamples,1);              % Rear right wheel
VEHICLE.timestamp = time;

%% 6. Test Cases for Edge Conditions
% Create specific test scenarios
testCases = struct();

% Test Case 1: GPS Outage
testCases.gpsOutage.startTime = 5;    % seconds
testCases.gpsOutage.duration = 2;     % seconds
testCases.gpsOutage.indices = find(time >= testCases.gpsOutage.startTime & ...
                                  time < testCases.gpsOutage.startTime + testCases.gpsOutage.duration);

% Test Case 2: High Acceleration Maneuver
testCases.highAccel.startTime = 3;
testCases.highAccel.duration = 0.5;
testCases.highAccel.indices = find(time >= testCases.highAccel.startTime & ...
                                  time < testCases.highAccel.startTime + testCases.highAccel.duration);

% Test Case 3: Magnetic Interference
testCases.magInterference.startTime = 7;
testCases.magInterference.duration = 1;
testCases.magInterference.indices = find(time >= testCases.magInterference.startTime & ...
                                        time < testCases.magInterference.startTime + testCases.magInterference.duration);

% Apply test cases
GPS.numSatellites(testCases.gpsOutage.indices) = 0;
GPS.HDOP(testCases.gpsOutage.indices) = 99;
IMU.accel_x(testCases.highAccel.indices) = 5;
IMU.accel_y(testCases.highAccel.indices) = 3;
MAG.mag_x(testCases.magInterference.indices) = MAG.mag_x(testCases.magInterference.indices) + 100;
MAG.mag_y(testCases.magInterference.indices) = MAG.mag_y(testCases.magInterference.indices) + 100;

%% 7. Create Simulink-Compatible Data Structures
% Format data for Simulink signal builder or from workspace blocks
simData.time = time;
simData.signals.values = [GPS.latitude, GPS.longitude, GPS.altitude, ...
                         GPS.velocity_north, GPS.velocity_east, GPS.velocity_down, ...
                         IMU.accel_x, IMU.accel_y, IMU.accel_z, ...
                         IMU.gyro_x, IMU.gyro_y, IMU.gyro_z, ...
                         MAG.mag_x, MAG.mag_y, MAG.mag_z, ...
                         BARO.pressure, BARO.altitude, ...
                         VEHICLE.speed, VEHICLE.steering_angle];

simData.signals.dimensions = size(simData.signals.values, 2);
simData.signals.label = 'NavigationTestData';

%% 8. Save Test Data
save('navigation_test_data.mat', 'GPS', 'IMU', 'MAG', 'BARO', 'VEHICLE', ...
     'testCases', 'simData', 'time', 'sampleTime', 'numSamples');

%% 9. Create Timeseries Objects for Simulink
% Create timeseries objects that can be directly used in Simulink
ts_GPS_lat = timeseries(GPS.latitude, time, 'Name', 'GPS_Latitude');
ts_GPS_lon = timeseries(GPS.longitude, time, 'Name', 'GPS_Longitude');
ts_GPS_alt = timeseries(GPS.altitude, time, 'Name', 'GPS_Altitude');
ts_IMU_accel = timeseries([IMU.accel_x, IMU.accel_y, IMU.accel_z], time, 'Name', 'IMU_Acceleration');
ts_IMU_gyro = timeseries([IMU.gyro_x, IMU.gyro_y, IMU.gyro_z], time, 'Name', 'IMU_AngularRate');
ts_MAG = timeseries([MAG.mag_x, MAG.mag_y, MAG.mag_z], time, 'Name', 'Magnetometer');

save('navigation_timeseries.mat', 'ts_GPS_lat', 'ts_GPS_lon', 'ts_GPS_alt', ...
     'ts_IMU_accel', 'ts_IMU_gyro', 'ts_MAG');

%% 10. Generate Test Report
fprintf('Navigation Test Data Generated Successfully!\n');
fprintf('================================================\n');
fprintf('Test Duration: %.2f seconds\n', testDuration);
fprintf('Sample Rate: %.0f Hz\n', 1/sampleTime);
fprintf('Total Samples: %d\n', numSamples);
fprintf('\nTest Cases Included:\n');
fprintf('1. GPS Outage: %.1f - %.1f seconds\n', testCases.gpsOutage.startTime, ...
        testCases.gpsOutage.startTime + testCases.gpsOutage.duration);
fprintf('2. High Acceleration: %.1f - %.1f seconds\n', testCases.highAccel.startTime, ...
        testCases.highAccel.startTime + testCases.highAccel.duration);
fprintf('3. Magnetic Interference: %.1f - %.1f seconds\n', testCases.magInterference.startTime, ...
        testCases.magInterference.startTime + testCases.magInterference.duration);
fprintf('\nData saved to:\n');
fprintf('- navigation_test_data.mat\n');
fprintf('- navigation_timeseries.mat\n');

%% 11. Plot Sample Data
figure('Name', 'Navigation Test Data Preview', 'Position', [100 100 1200 800]);

% GPS Position
subplot(3,3,1);
plot(time, GPS.latitude);
xlabel('Time (s)'); ylabel('Latitude (deg)');
title('GPS Latitude');
grid on;

subplot(3,3,2);
plot(time, GPS.longitude);
xlabel('Time (s)'); ylabel('Longitude (deg)');
title('GPS Longitude');
grid on;

subplot(3,3,3);
plot(time, GPS.altitude);
xlabel('Time (s)'); ylabel('Altitude (m)');
title('GPS Altitude');
grid on;

% IMU Data
subplot(3,3,4);
plot(time, [IMU.accel_x, IMU.accel_y, IMU.accel_z]);
xlabel('Time (s)'); ylabel('Acceleration (m/s²)');
title('IMU Accelerometer');
legend('X', 'Y', 'Z');
grid on;

subplot(3,3,5);
plot(time, [IMU.gyro_x, IMU.gyro_y, IMU.gyro_z]);
xlabel('Time (s)'); ylabel('Angular Rate (rad/s)');
title('IMU Gyroscope');
legend('X', 'Y', 'Z');
grid on;

% Magnetometer
subplot(3,3,6);
plot(time, [MAG.mag_x, MAG.mag_y, MAG.mag_z]);
xlabel('Time (s)'); ylabel('Magnetic Field (μT)');
title('Magnetometer');
legend('X', 'Y', 'Z');
grid on;

% Vehicle Data
subplot(3,3,7);
plot(time, VEHICLE.speed);
xlabel('Time (s)'); ylabel('Speed (m/s)');
title('Vehicle Speed');
grid on;

% GPS Quality
subplot(3,3,8);
yyaxis left;
plot(time, GPS.numSatellites);
ylabel('Number of Satellites');
yyaxis right;
plot(time, GPS.HDOP);
ylabel('HDOP');
xlabel('Time (s)');
title('GPS Quality Indicators');
grid on;

% Barometer
subplot(3,3,9);
plot(time, BARO.altitude);
xlabel('Time (s)'); ylabel('Altitude (m)');
title('Barometric Altitude');
grid on;

sgtitle('Navigation Test Data Overview');

%% 12. Create Validation Test Script
validationScript = [...
'%% Navigation Calculations Validation Script\n', ...
'% This script validates the navigation calculations output\n\n', ...
'% Load test data\n', ...
'load(''navigation_test_data.mat'');\n\n', ...
'% Run your Simulink model\n', ...
'% sim(''Navigation_Calculations'');\n\n', ...
'% Validate outputs\n', ...
'% Add your validation checks here\n', ...
'% Example: check position error, velocity error, attitude error\n'];

fid = fopen('validate_navigation.m', 'w');
fprintf(fid, '%s', validationScript);
fclose(fid);

fprintf('\nValidation script created: validate_navigation.m\n');