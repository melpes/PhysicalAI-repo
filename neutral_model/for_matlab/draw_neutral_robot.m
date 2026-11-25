function draw_neutral_robot(ax, robot, qDeg)
%DRAW_NEUTRAL_ROBOT Draw a neutral robot at joint values qDeg (degrees) into axes ax.
%   The floor and light are display aids only; they are not part of the neutral model.

    hold(ax, 'on');
    grid(ax, 'on');
    axis(ax, 'equal');
    xlim(ax, [-2.6 2.9]); ylim(ax, [-1.6 1.6]); zlim(ax, [-1.9 3.0]);
    xlabel(ax, 'x (m)'); ylabel(ax, 'y (m)'); zlabel(ax, 'z (m)');
    patch('Parent', ax, 'XData', [-3 3 3 -3], 'YData', [-3 -3 3 3], 'ZData', [0 0 0 0], ...
        'FaceColor', [0.8 0.85 0.9], 'FaceAlpha', 0.4, 'EdgeColor', 'none', 'Tag', 'DisplayFloor');

    poses = robot_link_poses(robot, qDeg);
    placementR = quatToRotm(robot.placement.orientation);
    placementP = robot.placement.position;
    for k = 1:numel(robot.visuals)
        visual = robot.visuals(k);
        link = poses(visual.link);
        R = placementR * link.R * quatToRotm(visual.orientation);
        center = placementP + (placementR * (link.p(:) + link.R * visual.position(:))).';
        drawBox(ax, visual.id, visual.size, center, rotmToQuat(R), visual.color);
    end
    wristPose = poses('WristCenter');
    wrist = placementP + (placementR * wristPose.p(:)).';
    plot3(ax, wrist(1), wrist(2), wrist(3), 'o', 'MarkerSize', 7, ...
        'MarkerFaceColor', [0 0.6 1], 'MarkerEdgeColor', 'k', 'Tag', 'WristCenter');
    view(ax, 150, 15);
    camlight(ax, 'headlight');
end

function R = quatToRotm(q)
    q = q / norm(q);
    w = q(1); x = q(2); y = q(3); z = q(4);
    R = [1-2*(y^2+z^2), 2*(x*y-w*z),   2*(x*z+w*y);
         2*(x*y+w*z),   1-2*(x^2+z^2), 2*(y*z-w*x);
         2*(x*z-w*y),   2*(y*z+w*x),   1-2*(x^2+y^2)];
end

function q = rotmToQuat(R)
% Shepperd's method: pick the largest diagonal term to stay numerically stable.
    t = trace(R);
    if t > 0
        s = 2 * sqrt(1 + t);
        q = [s/4, (R(3,2)-R(2,3))/s, (R(1,3)-R(3,1))/s, (R(2,1)-R(1,2))/s];
    elseif R(1,1) > R(2,2) && R(1,1) > R(3,3)
        s = 2 * sqrt(1 + R(1,1) - R(2,2) - R(3,3));
        q = [(R(3,2)-R(2,3))/s, s/4, (R(1,2)+R(2,1))/s, (R(1,3)+R(3,1))/s];
    elseif R(2,2) > R(3,3)
        s = 2 * sqrt(1 + R(2,2) - R(1,1) - R(3,3));
        q = [(R(1,3)-R(3,1))/s, (R(1,2)+R(2,1))/s, s/4, (R(2,3)+R(3,2))/s];
    else
        s = 2 * sqrt(1 + R(3,3) - R(1,1) - R(2,2));
        q = [(R(2,1)-R(1,2))/s, (R(1,3)+R(3,1))/s, (R(2,3)+R(3,2))/s, s/4];
    end
end
