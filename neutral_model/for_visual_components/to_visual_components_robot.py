import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from neutral_robot import read_robot

M_TO_MM = 1000.0

SCRIPT = """from vcScript import *
import math

app = getApplication()

MODEL_KEYWORD = %(keyword)r
NEUTRAL_JOINTS = %(joints)r
TEST_POSES = %(poses)r
TOLERANCE_MM = 0.1


def report(results, label, passed, detail):
    results.append(passed)
    print("[%%s] %%s: %%s" %% ("PASS" if passed else "FAIL", label, detail))


def find_robot():
    for comp in app.Components:
        if MODEL_KEYWORD in comp.Name and comp.findBehavioursByType(VC_ROBOTCONTROLLER):
            return comp
    return None


def to_base(base, point):
    d = (point.X - base.P.X, point.Y - base.P.Y, point.Z - base.P.Z)
    return [d[0] * axis.X + d[1] * axis.Y + d[2] * axis.Z for axis in (base.N, base.O, base.A)]


def value_of(expression):
    try:
        return float(expression)
    except (TypeError, ValueError):
        return None


def check_robot():
    results = []
    comp = find_robot()
    report(results, "robot found", comp is not None,
           comp.Name if comp else "no robot whose name contains %%s" %% MODEL_KEYWORD)
    if comp is None:
        return
    controller = comp.findBehavioursByType(VC_ROBOTCONTROLLER)[0]
    joints = controller.Joints
    report(results, "joint count", len(joints) == len(NEUTRAL_JOINTS),
           "VC %%d / neutral %%d" %% (len(joints), len(NEUTRAL_JOINTS)))

    for joint, (joint_id, lower, upper, velocity) in zip(joints, NEUTRAL_JOINTS):
        vc_lower, vc_upper = value_of(joint.MinValue), value_of(joint.MaxValue)
        same_range = (vc_lower is not None and vc_upper is not None and
                      abs(vc_lower - lower) < 1e-6 and abs(vc_upper - upper) < 1e-6)
        report(results, "%%s (VC %%s) range deg" %% (joint_id, joint.Name), same_range,
               "VC [%%s, %%s] / neutral [%%s, %%s]" %% (joint.MinValue, joint.MaxValue, lower, upper))
        report(results, "%%s max speed deg/s" %% joint_id, abs(joint.MaxSpeed - velocity) < 1e-6,
               "VC %%s / neutral %%s" %% (joint.MaxSpeed, velocity))

    flange = getattr(controller, "FlangeNode", None) or controller.Tools[0].Node
    original = [joint.CurrentValue for joint in joints]
    distances = []
    for pose_id, q, wrist_mm, j6_axis in TEST_POSES:
        for joint, value in zip(joints, q):
            joint.CurrentValue = value
        if hasattr(flange, "update"):
            flange.update()
        f = to_base(comp.WorldPositionMatrix, flange.WorldPositionMatrix.P)
        delta = [f[i] - wrist_mm[i] for i in range(3)]
        distance = math.sqrt(sum(c * c for c in delta))
        off_axis = max(abs(delta[i] - distance * j6_axis[i]) for i in range(3))
        distances.append(distance)
        report(results, "%%s flange on J6 axis" %% pose_id, off_axis < TOLERANCE_MM,
               "flange %%.3f %%.3f %%.3f mm, distance from wrist centre %%.3f mm, off-axis %%.4f mm"
               %% (f[0], f[1], f[2], distance, off_axis))
    for joint, value in zip(joints, original):
        joint.CurrentValue = value

    spread = max(distances) - min(distances)
    report(results, "flange distance constant", spread < TOLERANCE_MM,
           "min %%.3f / max %%.3f mm" %% (min(distances), max(distances)))
    print("VC flange lies %%.3f mm from the neutral wrist centre along the J6 axis"
          %% (sum(distances) / len(distances)))
    print("")
    print("%%d/%%d passed" %% (sum(results), len(results)))


check_robot()
app.render()


def OnSignal( signal ):
  pass

def OnRun():
  pass
"""


def to_visual_components_robot(neutral_path, csv_path, py_path):
    robot = read_robot(neutral_path)
    joints = [(j["id"], j["lower"], j["upper"], j["velocity"]) for j in robot["joints"]]
    with open(csv_path, encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    poses = [(row["pose_id"],
              [float(row[j["id"]]) for j in robot["joints"]],
              [round(float(row[k]) * M_TO_MM, 9) for k in ("wc_x", "wc_y", "wc_z")],
              [round(float(row[k]), 12) for k in ("j6_axis_x", "j6_axis_y", "j6_axis_z")])
             for row in rows]
    keyword = robot["model"].split()[1].split("-")[0]
    with open(py_path, "w", encoding="utf-8") as fp:
        fp.write(SCRIPT % {"keyword": keyword, "joints": joints, "poses": poses})


if __name__ == "__main__":
    to_visual_components_robot(sys.argv[1], sys.argv[2], sys.argv[3])
