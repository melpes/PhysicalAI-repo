function fig = run_in_matlab(neutralPath)
%RUN_IN_MATLAB Read the neutral XML directly and draw every object.
%   run_in_matlab('scenes/box.neutral.xml')

    fig = figure('Color', 'w');
    ax = axes('Parent', fig);
    hold(ax, 'on');
    grid(ax, 'on');
    axis(ax, 'equal');
    view(ax, 3);
    xlabel(ax, 'x (m)'); ylabel(ax, 'y (m)'); zlabel(ax, 'z (m)');
    for obj = read_neutral_scene(neutralPath)
        drawBox(ax, obj.id, obj.size, obj.position, obj.orientation, obj.color);
    end
end
