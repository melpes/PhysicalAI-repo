function objects = read_neutral_scene(neutralPath)
%READ_NEUTRAL_SCENE MATLAB version of read_scene in common/neutral_scene.py.
%   objects = read_neutral_scene('scenes/box.neutral.xml')
%   Returns the Objects that carry their own Geometry, as a struct array with
%   fields id, size, position, orientation, color. Objects with ref are skipped.

    root = load_neutral_root(neutralPath);
    objects = struct('id', {}, 'size', {}, 'position', {}, 'orientation', {}, 'color', {});
    nodes = root.getElementsByTagName('Object');
    for i = 0:nodes.getLength()-1
        obj = nodes.item(i);
        if obj.getElementsByTagName('Geometry').getLength() == 0
            continue;
        end
        geometry = obj.getElementsByTagName('Geometry').item(0);
        if ~strcmp(char(geometry.getAttribute('type')), 'Box')
            error('read_neutral_scene:geometry', '%s: geometry type %s is not supported', ...
                char(obj.getAttribute('id')), char(geometry.getAttribute('type')));
        end
        [relativeTo, position, orientation] = read_neutral_pose(obj);
        if ~strcmp(relativeTo, 'World')
            error('read_neutral_scene:pose', '%s: Pose relativeTo=%s is not supported for Object', ...
                char(obj.getAttribute('id')), relativeTo);
        end
        objects(end+1) = struct( ...
            'id', char(obj.getAttribute('id')), ...
            'size', neutral_vector(geometry.getElementsByTagName('Size').item(0), {'x', 'y', 'z'}), ...
            'position', position, ...
            'orientation', orientation, ...
            'color', neutral_vector(obj.getElementsByTagName('Color').item(0), {'r', 'g', 'b', 'a'})); %#ok<AGROW>
    end
end
