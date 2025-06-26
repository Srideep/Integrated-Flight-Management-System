%% configure_nav_model
% Creates a new, blank Simulink model and configures its core properties.

function configure_nav_model(modelName)
    outputDir = 'models/navigation';
    if ~exist(outputDir, 'dir')
       mkdir(outputDir);
    end

    if bdIsLoaded(modelName)
        close_system(modelName, 0);
    end
    
    new_system(modelName);
    open_system(modelName);
    
    set_param(modelName, 'SolverType', 'Fixed-step', 'FixedStep', '0.02');
end
