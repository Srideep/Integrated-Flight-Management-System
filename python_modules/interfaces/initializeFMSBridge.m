% Initialize the FMS Python Bridge
% This should be called once when the simulation starts

function initializeFMSBridge()
    % Add the Python modules path to MATLAB's Python path
    if count(py.sys.path,'') == 0
        insert(py.sys.path,int32(0),'');
    end
    
    % Add your project's python_modules directory
    project_root = fileparts(fileparts(mfilename('fullpath')));
    python_path = fullfile(project_root, 'python_modules');
    
    if count(py.sys.path, python_path) == 0
        insert(py.sys.path, int32(0), python_path);
    end
    
    % Initialize the bridge
    success = py.interfaces.matlab_python_bridge.initialize_fms_bridge();
    
    if success
        disp('FMS Python bridge initialized successfully');
    else
        error('Failed to initialize FMS Python bridge');
    end
end