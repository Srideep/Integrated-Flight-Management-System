%% test_navigation_module.m
% A test harness script to perform unit testing on the
% Navigation_Calculations.slx model.

function tests = test_navigation_module
    % Create a collection of tests to be run by the MATLAB Test Manager
    tests = functiontests(localfunctions);
end

function setupOnce(testCase)
    % --- 1. SETUP PHASE ---
    fprintf('\n--- Setting up FMS Test Environment ---\n');
    project_root = matlab.project.currentProject().RootFolder;
    if count(py.sys.path, project_root) == 0
        insert(py.sys.path, int32(0), project_root);
    end
    
    define_navigation_buses();
    
    % Re-generate the model to ensure it's up-to-date with any script changes
    create_navigation_module();
    
    py.python_modules.interfaces.matlab_python_bridge.initialize_fms_bridge();
    py.python_modules.interfaces.matlab_python_bridge.create_flight_plan_bridge(...
        'TEST01', 'KSFO', 'KOAK', {'SFO'});
    py.python_modules.interfaces.matlab_python_bridge.set_active_flight_plan_bridge('TEST01');
    fprintf('Test setup complete. Active plan is TEST01 (KSFO-SFO-KOAK).\n');
end

function teardownOnce(testCase)
    % --- 4. TEARDOWN PHASE ---
    fprintf('\n--- Tearing down FMS Test Environment ---\n');
    py.python_modules.interfaces.matlab_python_bridge.cleanup_bridge();
    modelName = 'Navigation_Calculations';
    if bdIsLoaded(modelName)
        close_system(modelName, 0);
    end
    fprintf('Teardown complete.\n');
end

function test_NavCalcs_OnTrack(testCase)
    % --- 2. EXECUTION PHASE ---
    modelName = 'Navigation_Calculations';
    fprintf('\nRunning test: test_NavCalcs_OnTrack...\n');
    
    % Define Test Inputs
    ac_pos.latitude = 37.6213;
    ac_pos.longitude = -122.3790;
    ac_pos.altitude = 5000;
    
    % Create a Simulink.SimulationInput object
    simIn = Simulink.SimulationInput(modelName);
    simIn = simIn.setExternalInput(ac_pos);
    simIn = simIn.setModelParameter('StopTime', '0.02');
    
    % Run the simulation
    simOut = sim(simIn);
    
    % --- 3. VERIFICATION PHASE ---
    
    % FIX: Extract data from the bus signal structure.
    % The output is now a 'timeseries' object containing a struct.
    % We need to access the 'Data' property and get the last value.
    nav_output_signal = simOut.get('Navigation_Out');
    nav_output_struct = nav_output_signal.Values.Data(end);

    % Define the expected results
    expected_xte = 0.0;
    expected_dtg = 0.1545;
    expected_course = 136.2;

    % Assert that the actual output matches the expected output
    testCase.verifyEqual(nav_output_struct.CrossTrackError_nm, expected_xte, 'AbsTol', 0.01, ...
        'Verification failed: Cross-Track Error should be zero when on track.');
        
    testCase.verifyEqual(nav_output_struct.DistanceToGo_nm, expected_dtg, 'AbsTol', 0.01, ...
        'Verification failed: Distance to Go is incorrect.');
        
    testCase.verifyEqual(nav_output_struct.DesiredCourse_deg, expected_course, 'AbsTol', 0.1, ...
        'Verification failed: Desired Course is incorrect.');
        
    fprintf('Test passed!\n');
end
