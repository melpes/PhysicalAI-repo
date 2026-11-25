function fig = show_matlab_robot_poses(neutralPath, csvPath)
%SHOW_MATLAB_ROBOT_POSES Draw the robot in every shared test pose, one tile per pose.
%   show_matlab_robot_poses('scenes/irb4600_40_255.neutral.xml', 'tests/irb4600_test_poses.csv')
%   Same poses and layout as for_mujoco/outputs/irb4600_poses.png, for side-by-side comparison.

    robot = read_neutral_robot(neutralPath);
    poses = readtable(csvPath, 'TextType', 'char');
    jointIds = {robot.joints.id};
    fig = figure('Color', 'w', 'Position', [50 50 1600 800]);
    layout = tiledlayout(fig, 2, ceil(height(poses) / 2), 'TileSpacing', 'compact', 'Padding', 'compact');
    for r = 1:height(poses)
        ax = nexttile(layout);
        q = cellfun(@(id) poses.(id)(r), jointIds);
        draw_neutral_robot(ax, robot, q);
        title(ax, poses.pose_id{r}, 'Interpreter', 'none');
    end
    title(layout, robot.model);
end
