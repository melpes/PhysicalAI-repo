import xml.etree.ElementTree as ET

SCHEMA_VERSION = "0.3"
CONVENTIONS = {"unit": "m", "angleUnit": "deg", "massUnit": "kg", "timeUnit": "s",
               "upAxis": "+Z", "handedness": "right", "colorSpace": "sRGB"}
WORLD = "World"
GEOMETRY_TYPES = ("Box",)


def vector(el, keys):
    return [float(el.get(k)) for k in keys]


def load_root(path):
    root = ET.parse(path).getroot()
    if root.get("version") != SCHEMA_VERSION:
        raise ValueError(f"version={root.get('version')} is not supported (expected {SCHEMA_VERSION})")
    for key, expected in CONVENTIONS.items():
        if root.get(key) != expected:
            raise ValueError(f"{key}={root.get(key)} is not supported (expected {expected})")
    sources = {s.get("id") for s in root.findall("Sources/Source")}
    for el in root.iter():
        if el.get("source") is not None and el.get("source") not in sources:
            raise ValueError(f"<{el.tag}> refers to unknown source {el.get('source')}")
    return root


def read_pose(el):
    pose = el.find("Pose")
    return (pose.get("relativeTo"), vector(pose.find("Position"), "xyz"),
            vector(pose.find("Orientation"), "wxyz"))


def read_box(el):
    geometry = el.find("Geometry")
    if geometry.get("type") not in GEOMETRY_TYPES:
        raise ValueError(f"{el.get('id')}: geometry type {geometry.get('type')} is not supported")
    return vector(geometry.find("Size"), "xyz")


def read_scene(path):
    root = load_root(path)
    objects = []
    for obj in root.findall("Object"):
        if obj.find("Geometry") is None:
            continue
        relative_to, position, orientation = read_pose(obj)
        if relative_to != WORLD:
            raise ValueError(f"{obj.get('id')}: Pose relativeTo={relative_to} is not supported for Object")
        objects.append({
            "id": obj.get("id"),
            "size": read_box(obj),
            "position": position,
            "orientation": orientation,
            "color": vector(obj.find("Appearance/Color"), "rgba"),
        })
    return objects


def numbers(values):
    return " ".join(str(v) for v in values)
