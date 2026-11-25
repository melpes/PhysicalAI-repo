import sys
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from neutral_scene import numbers, read_scene


def to_mujoco(neutral_path, mjcf_path):
    root = ET.Element("mujoco", model="neutral_scene")
    worldbody = ET.SubElement(root, "worldbody")
    for obj in read_scene(neutral_path):
        ET.SubElement(worldbody, "geom", {
            "name": obj["id"],
            "type": "box",
            "size": numbers(s / 2 for s in obj["size"]),
            "pos": numbers(obj["position"]),
            "quat": numbers(obj["orientation"]),
            "rgba": numbers(obj["color"]),
        })
    ET.indent(root)
    ET.ElementTree(root).write(mjcf_path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    to_mujoco(sys.argv[1], sys.argv[2])
