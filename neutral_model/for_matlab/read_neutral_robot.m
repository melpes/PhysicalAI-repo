function robot = read_neutral_robot(neutralPath)
%READ_NEUTRAL_ROBOT MATLAB version of read_robot in common/neutral_robot.py.
%   robot = read_neutral_robot('scenes/irb4600_40_255.neutral.xml')
%   Joint, Frame and Visual poses are relative to the Link named in relativeTo.
%   robot.placement is the Pose of the Object whose ref is this robot.

    specificationTerms = {'payload', 'armload', 'mass', 'reach', 'height', ...
        'positionRepeatability', 'pathRepeatability'};
    root = load_neutral_root(neutralPath);
    robotEl = root.getElementsByTagName('Robot').item(0);
    robot.id = char(robotEl.getAttribute('id'));
    robot.model = char(robotEl.getAttribute('model'));
    robot.baseLink = char(robotEl.getAttribute('baseLink'));

    linkNodes = robotEl.getElementsByTagName('Link');
    links = cell(1, linkNodes.getLength());
    for i = 0:linkNodes.getLength()-1
        links{i+1} = char(linkNodes.item(i).getAttribute('id'));
    end

    robot.specification = struct();
    attributes = robotEl.getElementsByTagName('Specification').item(0).getAttributes();
    for i = 0:attributes.getLength()-1
        name = char(attributes.item(i).getName());
        if strcmp(name, 'source')
            continue;
        end
        if ~any(strcmp(name, specificationTerms))
            error('read_neutral_robot:specification', 'Specification term %s is not defined', name);
        end
        robot.specification.(name) = str2double(char(attributes.item(i).getValue()));
    end

    robot.visuals = struct('id', {}, 'link', {}, 'size', {}, 'position', {}, 'orientation', {}, 'color', {});
    nodes = robotEl.getElementsByTagName('Visual');
    for i = 0:nodes.getLength()-1
        el = nodes.item(i);
        [link, position, orientation] = poseOnLink(el, links);
        robot.visuals(end+1) = struct( ...
            'id', char(el.getAttribute('id')), ...
            'link', link, ...
            'size', neutral_vector(el.getElementsByTagName('Size').item(0), {'x', 'y', 'z'}), ...
            'position', position, ...
            'orientation', orientation, ...
            'color', neutral_vector(el.getElementsByTagName('Color').item(0), {'r', 'g', 'b', 'a'})); %#ok<AGROW>
    end

    robot.joints = struct('id', {}, 'parent', {}, 'child', {}, 'position', {}, 'orientation', {}, ...
        'axis', {}, 'lower', {}, 'upper', {}, 'velocity', {});
    nodes = robotEl.getElementsByTagName('Joint');
    for i = 0:nodes.getLength()-1
        el = nodes.item(i);
        if ~strcmp(char(el.getAttribute('type')), 'Revolute')
            error('read_neutral_robot:joint', '%s: joint type %s is not supported', ...
                char(el.getAttribute('id')), char(el.getAttribute('type')));
        end
        [parent, position, orientation] = poseOnLink(el, links);
        limit = el.getElementsByTagName('Limit').item(0);
        robot.joints(end+1) = struct( ...
            'id', char(el.getAttribute('id')), ...
            'parent', parent, ...
            'child', char(el.getAttribute('child')), ...
            'position', position, ...
            'orientation', orientation, ...
            'axis', neutral_vector(el.getElementsByTagName('Axis').item(0), {'x', 'y', 'z'}), ...
            'lower', str2double(char(limit.getAttribute('lower'))), ...
            'upper', str2double(char(limit.getAttribute('upper'))), ...
            'velocity', str2double(char(limit.getAttribute('velocity')))); %#ok<AGROW>
    end

    robot.frames = struct('id', {}, 'parent', {}, 'position', {}, 'orientation', {});
    nodes = robotEl.getElementsByTagName('Frame');
    for i = 0:nodes.getLength()-1
        el = nodes.item(i);
        [parent, position, orientation] = poseOnLink(el, links);
        robot.frames(end+1) = struct('id', char(el.getAttribute('id')), 'parent', parent, ...
            'position', position, 'orientation', orientation); %#ok<AGROW>
    end

    robot.placement = struct('position', [0 0 0], 'orientation', [1 0 0 0]);
    nodes = root.getElementsByTagName('Object');
    for i = 0:nodes.getLength()-1
        el = nodes.item(i);
        if strcmp(char(el.getAttribute('ref')), robot.id)
            [relativeTo, position, orientation] = read_neutral_pose(el);
            if ~strcmp(relativeTo, 'World')
                error('read_neutral_robot:placement', '%s: Pose relativeTo=%s is not supported for Object', ...
                    char(el.getAttribute('id')), relativeTo);
            end
            robot.placement = struct('position', position, 'orientation', orientation);
        end
    end
end

function [link, position, orientation] = poseOnLink(el, links)
    [link, position, orientation] = read_neutral_pose(el);
    if ~any(strcmp(link, links))
        error('read_neutral_robot:pose', '%s: Pose relativeTo=%s is not a Link', ...
            char(el.getAttribute('id')), link);
    end
end
