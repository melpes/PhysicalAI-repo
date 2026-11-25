function fig = animate_matlab_robot(neutralPath, csvPath, poseId)
%ANIMATE_MATLAB_ROBOT Show the shared test poses one after another, like run_in_mujoco_robot.py.
%   animate_matlab_robot('scenes/irb4600_40_255.neutral.xml', 'tests/irb4600_test_poses.csv')
%       cycles through every pose, holding each for secondsPerPose seconds.
%   animate_matlab_robot(..., 'general_1') holds a single pose.
%   Close the figure window to stop.

    secondsPerPose = 3;
    robot = read_neutral_robot(neutralPath);
    poses = readtable(csvPath, 'TextType', 'char');
    if nargin == 3
        poses = poses(strcmp(poses.pose_id, poseId), :);
        if isempty(poses)
            error('animate_matlab_robot:pose', 'pose_id %s is not in %s', poseId, csvPath);
        end
    end
    jointIds = {robot.joints.id};

    fig = figure('Color', 'w');
    ax = axes('Parent', fig);
    draw_neutral_robot(ax, robot, cellfun(@(id) poses.(id)(1), jointIds));
    r = 0;
    while isgraphics(fig)
        r = mod(r, height(poses)) + 1;
        q = cellfun(@(id) poses.(id)(r), jointIds);
        [az, el] = view(ax);
        cla(ax);
        draw_neutral_robot(ax, robot, q);
        view(ax, az, el);
        title(ax, sprintf('%s   %s   q = %s deg', robot.model, poses.pose_id{r}, mat2str(round(q, 3))), ...
            'Interpreter', 'none');
        fprintf('%s: %s deg\n', poses.pose_id{r}, mat2str(round(q, 3)));
        drawnow;
        if height(poses) == 1
            waitfor(fig);
        else
            pause(secondsPerPose);
        end
    end
end
