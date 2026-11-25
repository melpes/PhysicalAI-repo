function poses = robot_link_poses(robot, qDeg)
%ROBOT_LINK_POSES World pose of every link and frame for joint values qDeg (degrees).
%   poses = robot_link_poses(robot, [0 0 0 0 0 0])
%   w = poses('WristCenter'); w.p is a 1x3 position, w.R a 3x3 rotation.
%   Written independently of neutral_robot.py: joint rotations use the
%   Rodrigues formula, origin orientations use the quaternion formula.

    poses = containers.Map();
    poses(robot.baseLink) = struct('R', eye(3), 'p', [0 0 0]);
    for k = 1:numel(robot.joints)
        joint = robot.joints(k);
        parent = poses(joint.parent);
        R = parent.R * quatToRotm(joint.orientation) * axisRotation(joint.axis, qDeg(k));
        p = parent.p + (parent.R * joint.position(:)).';
        poses(joint.child) = struct('R', R, 'p', p);
    end
    for k = 1:numel(robot.frames)
        frame = robot.frames(k);
        parent = poses(frame.parent);
        poses(frame.id) = struct('R', parent.R * quatToRotm(frame.orientation), ...
            'p', parent.p + (parent.R * frame.position(:)).');
    end
end

function R = quatToRotm(q)
    q = q / norm(q);
    w = q(1); x = q(2); y = q(3); z = q(4);
    R = [1-2*(y^2+z^2), 2*(x*y-w*z),   2*(x*z+w*y);
         2*(x*y+w*z),   1-2*(x^2+z^2), 2*(y*z-w*x);
         2*(x*z-w*y),   2*(y*z+w*x),   1-2*(x^2+y^2)];
end

function R = axisRotation(axis, angleDeg)
    a = axis / norm(axis);
    K = [0 -a(3) a(2); a(3) 0 -a(1); -a(2) a(1) 0];
    R = eye(3) + sind(angleDeg) * K + (1 - cosd(angleDeg)) * (K * K);
end
