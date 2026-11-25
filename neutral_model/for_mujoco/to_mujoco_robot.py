import math
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from neutral_robot import read_robot
from neutral_scene import numbers

POSITION_GAIN = 20000.0
JOINT_DAMPING = 2000.0
PLACEHOLDER_MASS = 1.0
PLACEHOLDER_INERTIA = 0.001


def add_visuals(body, robot, link_id):
    for visual in (v for v in robot["visuals"] if v["link"] == link_id):
        ET.SubElement(body, "geom", {
            "name": visual["id"],
            "type": "box",
            "size": numbers(s / 2 for s in visual["size"]),
            "pos": numbers(visual["position"]),
            "quat": numbers(visual["orientation"]),
            "rgba": numbers(visual["color"]),
            "contype": "0",
            "conaffinity": "0",
        })


def to_mujoco_robot(neutral_path, mjcf_path):
    robot = read_robot(neutral_path)
    root = ET.Element("mujoco", model=robot["id"])
    ET.SubElement(root, "compiler", angle="degree")
    ET.SubElement(root, "option", gravity="0 0 0")
    worldbody = ET.SubElement(root, "worldbody")
    placement_position, placement_orientation = robot["placement"]
    bodies = {robot["base_link"]: ET.SubElement(worldbody, "body", {
        "name": robot["base_link"],
        "pos": numbers(placement_position),
        "quat": numbers(placement_orientation),
    })}
    add_visuals(bodies[robot["base_link"]], robot, robot["base_link"])

    actuator = ET.SubElement(root, "actuator")
    for joint in robot["joints"]:
        body = ET.SubElement(bodies[joint["parent"]], "body", {
            "name": joint["child"],
            "pos": numbers(joint["position"]),
            "quat": numbers(joint["orientation"]),
        })
        ET.SubElement(body, "joint", {
            "name": joint["id"],
            "type": "hinge",
            "axis": numbers(joint["axis"]),
            "range": numbers([joint["lower"], joint["upper"]]),
            "limited": "true",
            "damping": str(JOINT_DAMPING),
        })
        add_visuals(body, robot, joint["child"])
        if not any(v["link"] == joint["child"] for v in robot["visuals"]):
            ET.SubElement(body, "inertial", pos="0 0 0", mass=str(PLACEHOLDER_MASS),
                          diaginertia=numbers([PLACEHOLDER_INERTIA] * 3))
        bodies[joint["child"]] = body
        ET.SubElement(actuator, "position", {
            "name": f"{joint['id']}_position",
            "joint": joint["id"],
            "kp": str(POSITION_GAIN),
            "ctrlrange": numbers([math.radians(joint["lower"]), math.radians(joint["upper"])]),
            "ctrllimited": "true",
        })

    for frame in robot["frames"]:
        ET.SubElement(bodies[frame["parent"]], "site", {
            "name": frame["id"],
            "pos": numbers(frame["position"]),
            "quat": numbers(frame["orientation"]),
            "size": "0.03",
            "rgba": "0 0.6 1 1",
        })
    ET.indent(root)
    ET.ElementTree(root).write(mjcf_path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    to_mujoco_robot(sys.argv[1], sys.argv[2])
