function h = drawBox(ax, id, boxSize, position, q, rgba)
%DRAWBOX Draw one neutral-model box as a patch.
%   boxSize is the full length along x, y, z. position is the box centre.
%   q is a unit quaternion [w x y z]. rgba is sRGB colour with alpha.

    w = q(1); x = q(2); y = q(3); z = q(4);
    R = [1-2*(y^2+z^2), 2*(x*y-w*z),   2*(x*z+w*y);
         2*(x*y+w*z),   1-2*(x^2+z^2), 2*(y*z-w*x);
         2*(x*z-w*y),   2*(y*z+w*x),   1-2*(x^2+y^2)];
    corners = [-1 -1 -1; 1 -1 -1; 1 1 -1; -1 1 -1; ...
               -1 -1 1; 1 -1 1; 1 1 1; -1 1 1];
    vertices = (corners .* (boxSize/2)) * R.' + position;
    faces = [1 4 3 2; 5 6 7 8; 1 2 6 5; 2 3 7 6; 3 4 8 7; 4 1 5 8];
    h = patch('Parent', ax, 'Vertices', vertices, 'Faces', faces, ...
        'FaceColor', rgba(1:3), 'FaceAlpha', rgba(4), 'EdgeColor', 'k', 'Tag', id);
end
