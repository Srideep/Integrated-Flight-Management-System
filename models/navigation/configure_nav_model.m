%% configure_nav_model.m
% Creates a new, blank Simulink model and configures its core properties
% according to the FMS project's System Requirements Specification (SRS).

function configure_nav_model(modelName)
    % Ensure the output directory exists
    outputDir = 'models/navigation';
    if ~exist(outputDir, 'dir')
       mkdir(outputDir);
       fprintf('Directory ''%s'' created.\n', outputDir);
    end

    % Close the model if it's already open from a previous run
    if bdIsLoaded(modelName)
        close_system(modelName, 0);
    end
    
    % Create a new, blank system
    new_system(modelName);
    open_system(modelName);
    
    % Configure model solver to meet the 50Hz real-time requirement (SRS PR-1.1)
    set_param(modelName, 'SolverType', 'Fixed-step');
    set_param(modelName, 'FixedStep', '0.02'); % 1 / 50Hz = 0.02s
    
    fprintf('Simulink model ''%s'' created and configured.\n', modelName);
end