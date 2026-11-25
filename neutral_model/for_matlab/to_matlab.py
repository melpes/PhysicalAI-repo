import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from neutral_scene import numbers, read_scene

HEADER = """fig = figure('Color', 'w');
ax = axes('Parent', fig);
hold(ax, 'on');
grid(ax, 'on');
axis(ax, 'equal');
view(ax, 3);
xlabel(ax, 'x (m)'); ylabel(ax, 'y (m)'); zlabel(ax, 'z (m)');
"""

DRAW_BOX = """
function drawBox(ax, id, boxSize, position, q, rgba)
    w = q(1); x = q(2); y = q(3); z = q(4);
    R = [1-2*(y^2+z^2), 2*(x*y-w*z),   2*(x*z+w*y);
         2*(x*y+w*z),   1-2*(x^2+z^2), 2*(y*z-w*x);
         2*(x*z-w*y),   2*(y*z+w*x),   1-2*(x^2+y^2)];
    corners = [-1 -1 -1; 1 -1 -1; 1 1 -1; -1 1 -1; ...
               -1 -1 1; 1 -1 1; 1 1 1; -1 1 1];
    vertices = (corners .* (boxSize/2)) * R.' + position;
    faces = [1 4 3 2; 5 6 7 8; 1 2 6 5; 2 3 7 6; 3 4 8 7; 4 1 5 8];
    patch('Parent', ax, 'Vertices', vertices, 'Faces', faces, ...
        'FaceColor', rgba(1:3), 'FaceAlpha', rgba(4), 'EdgeColor', 'k', 'Tag', id);
end
"""


def to_matlab(neutral_path, m_path):
    calls = [f"drawBox(ax, '{o['id']}', [{numbers(o['size'])}], [{numbers(o['position'])}], "
             f"[{numbers(o['orientation'])}], [{numbers(o['color'])}]);"
             for o in read_scene(neutral_path)]
    with open(m_path, "w", encoding="utf-8") as fp:
        fp.write(HEADER + "\n".join(calls) + "\n" + DRAW_BOX)


if __name__ == "__main__":
    to_matlab(sys.argv[1], sys.argv[2])
