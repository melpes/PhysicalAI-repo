function fig = run_in_matlab_robot(neutralPath, qDeg)
%RUN_IN_MATLAB_ROBOT Draw the neutral robot at joint values qDeg (degrees).
%   run_in_matlab_robot('scenes/irb4600_40_255.neutral.xml', [30 20 -10 40 30 60])

    robot = read_neutral_robot(neutralPath);
    fig = figure('Color', 'w');
    ax = axes('Parent', fig);
    draw_neutral_robot(ax, robot, qDeg);
    title(ax, sprintf('%s  q = %s deg', robot.model, mat2str(qDeg)));
end
