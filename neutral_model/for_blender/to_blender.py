import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from neutral_scene import read_scene

ADD_BOX = """import bpy


def add_box(obj_id, size, position, quaternion, rgba_linear):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=position)
    obj = bpy.context.active_object
    obj.name = obj_id
    obj.scale = size
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = quaternion
    material = bpy.data.materials.new(obj_id + "_material")
    if material.node_tree is None:
        material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba_linear
    material.diffuse_color = rgba_linear
    obj.data.materials.append(material)

"""


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def to_blender(neutral_path, py_path):
    calls = []
    for o in read_scene(neutral_path):
        rgba_linear = [srgb_to_linear(c) for c in o["color"][:3]] + [o["color"][3]]
        calls.append(f"add_box({o['id']!r}, {tuple(o['size'])}, {tuple(o['position'])}, "
                     f"{tuple(o['orientation'])}, {tuple(rgba_linear)})")
    with open(py_path, "w", encoding="utf-8") as fp:
        fp.write(ADD_BOX + "\n".join(calls) + "\n")


if __name__ == "__main__":
    to_blender(sys.argv[1], sys.argv[2])
