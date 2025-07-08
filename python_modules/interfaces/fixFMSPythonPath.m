function fixFMSPythonPath()
    pythonFile = 'C:\Users\deepd\MATLAB Drive\Projects\FMS_Integrated_System\python_modules\interfaces\matlab_python_bridge.py';
    
    % Read the file
    fid = fopen(pythonFile, 'r');
    lines = {};
    while ~feof(fid)
        lines{end+1} = fgetl(fid);
    end
    fclose(fid);
    
    % Fix common relative import patterns
    modified = false;
    for i = 1:length(lines)
        originalLine = lines{i};
        
        % Fix relative imports that go beyond package
        if contains(lines{i}, 'from ...')
            fprintf('Found relative import at line %d: %s\n', i, lines{i});
            
            % Convert patterns like:
            % from ...module import something → from module import something
            % from ..package.module import something → from package.module import something
            lines{i} = regexprep(lines{i}, 'from \.\.+', 'from ');
            
            modified = true;
            fprintf('Changed to: %s\n', lines{i});
        elseif contains(lines{i}, 'from .')
            fprintf('Found relative import at line %d: %s\n', i, lines{i});
            
            % Convert single dot relative imports
            % from .module import something → from interfaces.module import something
            lines{i} = strrep(lines{i}, 'from .', 'from interfaces.');
            
            modified = true;
            fprintf('Changed to: %s\n', lines{i});
        end
    end
    
    % Save the fixed file if modified
    if modified
        % Backup original
        copyfile(pythonFile, [pythonFile '.backup']);
        fprintf('\nOriginal file backed up to: %s.backup\n', pythonFile);
        
        % Write fixed version
        fid = fopen(pythonFile, 'w');
        for i = 1:length(lines)
            if ischar(lines{i})
                fprintf(fid, '%s\n', lines{i});
            end
        end
        fclose(fid);
        fprintf('Fixed imports in matlab_python_bridge.py\n');
    else
        fprintf('No relative imports found to fix.\n');
    end
end

% Run the fix