import csv
import math
import sys
from pathlib import Path

import mujoco
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from neutral_robot import read_robot
from rotation import quat_to_matrix

ABB_PUBLISHED_MM = {
    "abb_max_reach": ("앞쪽 수평 도달거리", 2552.0, "horizontal"),
    "abb_max_back_reach": ("뒤쪽 수평 도달거리", 2202.0, "horizontal"),
    "abb_max_height": ("최고 높이", 2872.0, "height"),
    "abb_max_depth": ("베이스 아래 최저 깊이", 1735.0, "depth"),
}


def report(results, label, passed, detail):
    results.append(passed)
    print(f"[{'PASS' if passed else 'FAIL'}] {label}: {detail}")


def main(neutral_path, mjcf_path, csv_path):
    robot = read_robot(neutral_path)
    model = mujoco.MjModel.from_xml_path(mjcf_path)
    data = mujoco.MjData(model)
    results = []
    report(results, "MJCF 불러오기", True, f"MuJoCo {mujoco.__version__}")
    report(results, "관절 수", model.njnt == len(robot["joints"]),
           f"MuJoCo {model.njnt} / 중립 {len(robot['joints'])}")

    for joint in robot["joints"]:
        jid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, joint["id"])
        mj_range = np.degrees(model.jnt_range[jid])
        report(results, f"{joint['id']} 범위(deg)", np.allclose(mj_range, [joint["lower"], joint["upper"]]),
               f"MuJoCo {np.round(mj_range, 6)} / 중립 [{joint['lower']}, {joint['upper']}]")

    placement_position, placement_orientation = robot["placement"]
    placement_R = np.array(quat_to_matrix(placement_orientation))
    site = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "WristCenter")
    joint_ids = [mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, j["id"]) for j in robot["joints"]]
    j6_body = model.jnt_bodyid[joint_ids[-1]]
    with open(csv_path, encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    for row in rows:
        for jid, joint in zip(joint_ids, robot["joints"]):
            data.qpos[model.jnt_qposadr[jid]] = math.radians(float(row[joint["id"]]))
        mujoco.mj_kinematics(model, data)
        expected = np.array([float(row[k]) for k in ("wc_x", "wc_y", "wc_z")])
        wrist = placement_R.T @ (data.site_xpos[site] - placement_position)
        error = np.abs(wrist - expected).max()
        report(results, f"{row['pose_id']} 손목중심 위치", error < 1e-9,
               f"MuJoCo {np.round(wrist, 6)} / 기준 {np.round(expected, 6)} (오차 {error:.1e} m)")
        j6_axis = placement_R.T @ data.xmat[j6_body].reshape(3, 3) @ model.jnt_axis[joint_ids[-1]]
        expected_axis = np.array([float(row[k]) for k in ("j6_axis_x", "j6_axis_y", "j6_axis_z")])
        axis_error = np.abs(j6_axis - expected_axis).max()
        report(results, f"{row['pose_id']} J6 축 방향", axis_error < 1e-9, f"오차 {axis_error:.1e}")
        if row["pose_id"] in ABB_PUBLISHED_MM:
            label, published, measure = ABB_PUBLISHED_MM[row["pose_id"]]
            wc = wrist * 1000
            value = {"horizontal": math.hypot(wc[0], wc[1]), "height": wc[2], "depth": -wc[2]}[measure]
            report(results, f"ABB 공개값 {label}", abs(value - published) < 1.0,
                   f"MuJoCo {value:.1f} mm / ABB {published:.0f} mm")

    print(f"\n{sum(results)}/{len(results)} 통과")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
