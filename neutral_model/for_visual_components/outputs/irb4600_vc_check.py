from vcScript import *
import math

app = getApplication()

MODEL_KEYWORD = '4600'
NEUTRAL_JOINTS = [('J1', -180.0, 180.0, 175.0), ('J2', -90.0, 150.0, 175.0), ('J3', -180.0, 75.0, 175.0), ('J4', -400.0, 400.0, 250.0), ('J5', -125.0, 120.0, 250.0), ('J6', -400.0, 400.0, 360.0)]
TEST_POSES = [('home', [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [1445.0, 0.0, 1765.0], [1.0, 0.0, 0.0]), ('abb_max_reach', [0.0, 90.0, -82.15432002858054, 0.0, 0.0, 0.0], [2552.000390016, 0.0, 495.0], [0.990639324208, 0.0, -0.13650541869]), ('abb_max_height', [0.0, 0.0, -82.15432002858054, 0.0, 0.0, 0.0], [175.0, 0.0, 2872.000390016], [0.13650541869, 0.0, 0.990639324208]), ('abb_max_back_reach', [0.0, -90.0, -82.15432002858054, 0.0, 0.0, 0.0], [-2202.000390016, 0.0, 495.0], [-0.990639324208, 0.0, 0.13650541869]), ('abb_max_depth', [0.0, 150.0, -52.15432002858054, 0.0, 0.0, 0.0], [722.5, 0.0, -1735.29820716], [-0.13650541869, 0.0, -0.990639324208]), ('general_1', [30.0, 20.0, -10.0, 40.0, 30.0, 60.0], [1585.351589883, 915.303167179, 1475.771590901], [0.520308600768, 0.6715139102, -0.527586986548]), ('general_2', [-120.0, -60.0, 50.0, -200.0, -100.0, 300.0], [-223.509799045, -387.130327935, 1435.374542414], [-0.286541632916, 0.177343510973, -0.94151111078]), ('general_3', [175.0, 140.0, -170.0, 390.0, 115.0, -390.0], [-1884.008090577, 164.829349917, 442.735780447], [-0.065838967197, -0.449124704526, -0.891039971148])]
TOLERANCE_MM = 0.1


def report(results, label, passed, detail):
    results.append(passed)
    print("[%s] %s: %s" % ("PASS" if passed else "FAIL", label, detail))


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
           comp.Name if comp else "no robot whose name contains %s" % MODEL_KEYWORD)
    if comp is None:
        return
    controller = comp.findBehavioursByType(VC_ROBOTCONTROLLER)[0]
    joints = controller.Joints
    report(results, "joint count", len(joints) == len(NEUTRAL_JOINTS),
           "VC %d / neutral %d" % (len(joints), len(NEUTRAL_JOINTS)))

    for joint, (joint_id, lower, upper, velocity) in zip(joints, NEUTRAL_JOINTS):
        vc_lower, vc_upper = value_of(joint.MinValue), value_of(joint.MaxValue)
        same_range = (vc_lower is not None and vc_upper is not None and
                      abs(vc_lower - lower) < 1e-6 and abs(vc_upper - upper) < 1e-6)
        report(results, "%s (VC %s) range deg" % (joint_id, joint.Name), same_range,
               "VC [%s, %s] / neutral [%s, %s]" % (joint.MinValue, joint.MaxValue, lower, upper))
        report(results, "%s max speed deg/s" % joint_id, abs(joint.MaxSpeed - velocity) < 1e-6,
               "VC %s / neutral %s" % (joint.MaxSpeed, velocity))

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
        report(results, "%s flange on J6 axis" % pose_id, off_axis < TOLERANCE_MM,
               "flange %.3f %.3f %.3f mm, distance from wrist centre %.3f mm, off-axis %.4f mm"
               % (f[0], f[1], f[2], distance, off_axis))
    for joint, value in zip(joints, original):
        joint.CurrentValue = value

    spread = max(distances) - min(distances)
    report(results, "flange distance constant", spread < TOLERANCE_MM,
           "min %.3f / max %.3f mm" % (min(distances), max(distances)))
    print("VC flange lies %.3f mm from the neutral wrist centre along the J6 axis"
          % (sum(distances) / len(distances)))
    print("")
    print("%d/%d passed" % (sum(results), len(results)))


check_robot()
app.render()


def OnSignal( signal ):
  pass

def OnRun():
  pass
