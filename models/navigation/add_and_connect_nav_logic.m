%% add_and_connect_nav_logic
% Populates the FMS Navigation model with all necessary blocks, sets their
% parameters according to the ICD, and connects them to form the data path.

function add_and_connect_nav_logic(modelName)
    
    % --- Add Blocks ---
    
    % Add Input Port (per ICD)
    add_block('simulink/Sources/In1', [modelName '/Position_In'], 'Position', [100, 100, 130, 120]);
    set_param([modelName '/Position_In'], 'UseBusObject', 'on', 'BusObject', 'PositionBus', 'BusOutputAsStruct', 'on');
    
    % Add Central MATLAB Function Block
    add_block('simulink/User-Defined Functions/MATLAB Function', [modelName '/Navigation_Logic'], 'Position', [250, 80, 550, 140]);
    
    % Add Output Port (per ICD)
    add_block('simulink/Sinks/Out1', [modelName '/Navigation_Out'], 'Position', [650, 100, 680, 120]);
    set_param([modelName '/Navigation_Out'], 'UseBusObject', 'on', 'BusObject', 'NavigationBus');

    % --- Set Block Logic ---
    
    % Retrieve the logic script from its dedicated source file
    logic_script = get_nav_logic_script_text();
    
    % Get a handle to the chart object and set its script property
    sf_root = sfroot;
    block_chart = sf_root.find('Path', [modelName '/Navigation_Logic'], '-isa', 'Stateflow.Chart');
    if ~isempty(block_chart)
        block_chart.Script = logic_script;
    end
    
    % --- Connect Blocks ---
    
    % Connect the blocks to form the complete data path
    add_line(modelName, 'Position_In/1', 'Navigation_Logic/1', 'autorouting', 'on');
    add_line(modelName, 'Navigation_Logic/1', 'Navigation_Out/1', 'autorouting', 'on');

    fprintf('Blocks added and connected within ''%s''.\n', modelName);
end