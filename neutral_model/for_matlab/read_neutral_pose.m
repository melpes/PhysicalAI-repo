function [relativeTo, position, orientation] = read_neutral_pose(el)
%READ_NEUTRAL_POSE Read the Pose child of an element: reference frame, position, quaternion.
%   MATLAB version of read_pose in common/neutral_scene.py.

    pose = el.getElementsByTagName('Pose').item(0);
    relativeTo = char(pose.getAttribute('relativeTo'));
    position = neutral_vector(pose.getElementsByTagName('Position').item(0), {'x', 'y', 'z'});
    orientation = neutral_vector(pose.getElementsByTagName('Orientation').item(0), {'w', 'x', 'y', 'z'});
end
