function root = load_neutral_root(neutralPath)
%LOAD_NEUTRAL_ROOT Open a neutral XML and check version, conventions and source references.
%   MATLAB version of load_root in common/neutral_scene.py.

    expected = struct('version', '0.3', 'unit', 'm', 'angleUnit', 'deg', 'massUnit', 'kg', ...
        'timeUnit', 's', 'upAxis', '+Z', 'handedness', 'right', 'colorSpace', 'sRGB');
    doc = xmlread(neutralPath);
    root = doc.getDocumentElement();
    keys = fieldnames(expected);
    for k = 1:numel(keys)
        value = char(root.getAttribute(keys{k}));
        if ~strcmp(value, expected.(keys{k}))
            error('load_neutral_root:convention', '%s=%s is not supported (expected %s)', ...
                keys{k}, value, expected.(keys{k}));
        end
    end

    sourceNodes = root.getElementsByTagName('Source');
    sourceIds = cell(1, sourceNodes.getLength());
    for i = 0:sourceNodes.getLength()-1
        sourceIds{i+1} = char(sourceNodes.item(i).getAttribute('id'));
    end
    allNodes = root.getElementsByTagName('*');
    for i = 0:allNodes.getLength()-1
        ref = char(allNodes.item(i).getAttribute('source'));
        if ~isempty(ref) && ~any(strcmp(ref, sourceIds))
            error('load_neutral_root:source', '<%s> refers to unknown source %s', ...
                char(allNodes.item(i).getTagName()), ref);
        end
    end
end
