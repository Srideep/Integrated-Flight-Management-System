%% create_navigation_module
% This script orchestrates the programmatic creation of the Navigation
% Calculations Simulink model by calling a series of modular helper scripts.

function create_navigation_module()
    % Define model and directory constants
    modelName = 'Navigation_Calculations';
    outputDir = 'models/navigation';
    project_root = matlab.project.currentProject().RootFolder;
    
    fprintf('--- FMS Navigation Module Creation Script ---\n');

    % --- Step 1: Define Data Contracts ---
    fprintf('Step 1: Defining navigation bus objects...\n');
    define_navigation_buses();

    % --- Step 2: Create and Configure the Blank Model ---
    fprintf('Step 2: Creating and configuring the Simulink model...\n');
    configure_nav_model(modelName);

    % --- Step 3: Add and Connect All Blocks and Logic ---
    fprintf('Step 3: Adding and connecting blocks...\n');
    add_and_connect_nav_logic(modelName);
    
    % --- Step 4: Finalize and Save ---
    fprintf('Step 4: Finalizing and saving the model...\n');
    Simulink.BlockDiagram.arrangeSystem(modelName);
    set_param(modelName, 'ScreenColor', '[0.95, 0.98, 1.0]');
    
    fullPath = fullfile(project_root, outputDir, [modelName, '.slx']);
    save_system(modelName, fullPath);
    close_system(modelName);
    
    fprintf('\nNavigation Calculations module created successfully at %s!\n', fullPath);
end