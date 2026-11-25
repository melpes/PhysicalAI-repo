import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from neutral_scene import read_scene
from rotation import quat_to_axis_angle, quat_to_matrix

M_TO_MM = 1000.0
BLOCK_REFERENCE = "bottom_center"

SCRIPT_HEAD = """from vcScript import *

app = getApplication()


def place_box(box_id, size_mm, origin_mm, axis, angle_deg, rgba):
    comp = app.findComponent(box_id)
    if comp is None:
        comp = app.createComponent()
        comp.Name = box_id
    block = comp.findFeature(box_id)
    if block is None:
        block = comp.RootFeature.createFeature(VC_BLOCK, box_id)
    block.Length = str(size_mm[0])
    block.Width = str(size_mm[1])
    block.Height = str(size_mm[2])

    material = app.findMaterial(box_id + "_material", True)
    if material is None:
        material = app.createMaterial(box_id + "_material")
        app.addMaterial(material)
    diffuse = material.Diffuse
    diffuse.X, diffuse.Y, diffuse.Z = rgba[0], rgba[1], rgba[2]
    material.Diffuse = diffuse
    material.Opacity = rgba[3]
    block.Material = material
    block.rebuild()

    matrix = comp.PositionMatrix
    matrix.setAxisAngle(axis[0], axis[1], axis[2], angle_deg)
    position = matrix.P
    position.X, position.Y, position.Z = origin_mm
    matrix.P = position
    comp.PositionMatrix = matrix
    comp.rebuild()

    p = comp.PositionMatrix.P
    print("%s position (mm): %.3f %.3f %.3f" % (box_id, p.X, p.Y, p.Z))
    print("%s WPR (deg): %s" % (box_id, comp.PositionMatrix.WPR))
    print("%s block L/W/H (mm): %s %s %s" % (box_id, block.Length, block.Width, block.Height))
    if hasattr(comp, "BoundCenter"):
        print("%s bound center in component frame (mm): %s" % (box_id, comp.BoundCenter))

"""






def block_origin(obj):
    center = obj["position"]
    if BLOCK_REFERENCE == "center":
        return center
    R = quat_to_matrix(obj["orientation"])
    half_height = obj["size"][2] / 2.0
    return [center[i] - R[i][2] * half_height for i in range(3)]


def to_visual_components(neutral_path, py_path):
    calls = []
    for obj in read_scene(neutral_path):
        axis, angle_deg = quat_to_axis_angle(obj["orientation"])
        size_mm = tuple(round(v * M_TO_MM, 6) for v in obj["size"])
        origin_mm = tuple(round(v * M_TO_MM, 6) for v in block_origin(obj))
        calls.append("place_box(%r, %r, %r, %r, %r, %r)" % (
            obj["id"], size_mm, origin_mm, tuple(round(a, 12) for a in axis),
            round(angle_deg, 9), tuple(obj["color"])))
    with open(py_path, "w", encoding="utf-8") as fp:
        fp.write(SCRIPT_HEAD + "\n".join(calls) + "\napp.render()\n")


if __name__ == "__main__":
    to_visual_components(sys.argv[1], sys.argv[2])
