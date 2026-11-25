from neutral_scene import WORLD, load_root, read_box, read_pose, vector
from rotation import axis_rotation, matmul, quat_to_matrix, rotate

JOINT_TYPES = ("Revolute",)
SPECIFICATION_TERMS = {
    "payload": "massUnit",
    "armload": "massUnit",
    "mass": "massUnit",
    "reach": "unit",
    "height": "unit",
    "positionRepeatability": "unit",
    "pathRepeatability": "unit",
}
IDENTITY_POSE = ([0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0])


def read_robot(path):
    root = load_root(path)
    robot_el = root.find("Robot")
    links = [link.get("id") for link in robot_el.findall("Link")]

    def pose_on_link(el):
        relative_to, position, orientation = read_pose(el)
        if relative_to not in links:
            raise ValueError(f"{el.get('id')}: Pose relativeTo={relative_to} is not a Link of {robot_el.get('id')}")
        return relative_to, position, orientation

    specification = {}
    for key, value in robot_el.find("Specification").attrib.items():
        if key == "source":
            continue
        if key not in SPECIFICATION_TERMS:
            raise ValueError(f"Specification term {key} is not defined")
        specification[key] = float(value)

    robot = {
        "id": robot_el.get("id"),
        "manufacturer": robot_el.get("manufacturer"),
        "model": robot_el.get("model"),
        "base_link": robot_el.get("baseLink"),
        "specification": specification,
        "visuals": [],
        "joints": [],
        "frames": [],
        "placement": IDENTITY_POSE,
    }
    for visual_el in robot_el.findall("Visual"):
        link, position, orientation = pose_on_link(visual_el)
        robot["visuals"].append({
            "id": visual_el.get("id"),
            "link": link,
            "size": read_box(visual_el),
            "position": position,
            "orientation": orientation,
            "color": vector(visual_el.find("Appearance/Color"), "rgba"),
        })
    for joint_el in robot_el.findall("Joint"):
        if joint_el.get("type") not in JOINT_TYPES:
            raise ValueError(f"{joint_el.get('id')}: joint type {joint_el.get('type')} is not supported")
        parent, position, orientation = pose_on_link(joint_el)
        limit = joint_el.find("Limit")
        robot["joints"].append({
            "id": joint_el.get("id"),
            "parent": parent,
            "child": joint_el.get("child"),
            "position": position,
            "orientation": orientation,
            "axis": vector(joint_el.find("Axis"), "xyz"),
            "lower": float(limit.get("lower")),
            "upper": float(limit.get("upper")),
            "velocity": float(limit.get("velocity")),
        })
    for frame_el in robot_el.findall("Frame"):
        parent, position, orientation = pose_on_link(frame_el)
        robot["frames"].append({"id": frame_el.get("id"), "parent": parent,
                                "position": position, "orientation": orientation})
    for obj in root.findall("Object"):
        if obj.get("ref") == robot["id"]:
            relative_to, position, orientation = read_pose(obj)
            if relative_to != WORLD:
                raise ValueError(f"{obj.get('id')}: Pose relativeTo={relative_to} is not supported for Object")
            robot["placement"] = (position, orientation)
    return robot


def compose(pose, position, rotation):
    R, p = pose
    return matmul(R, rotation), [p[i] + v for i, v in enumerate(rotate(R, position))]


def link_poses(robot, q_deg):
    identity = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    poses = {robot["base_link"]: (identity, [0.0, 0.0, 0.0])}
    for joint, q in zip(robot["joints"], q_deg):
        origin = compose(poses[joint["parent"]], joint["position"], quat_to_matrix(joint["orientation"]))
        poses[joint["child"]] = compose(origin, [0.0, 0.0, 0.0], axis_rotation(joint["axis"], q))
    for frame in robot["frames"]:
        poses[frame["id"]] = compose(poses[frame["parent"]], frame["position"], quat_to_matrix(frame["orientation"]))
    return poses


def joint_axis_world(robot, poses, joint_id):
    joint = next(j for j in robot["joints"] if j["id"] == joint_id)
    return rotate(poses[joint["child"]][0], joint["axis"])
