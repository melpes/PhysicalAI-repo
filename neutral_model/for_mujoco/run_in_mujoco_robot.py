import csv
import math
import sys
import time

import mujoco
import mujoco.viewer

from display_aids import load_with_display_aids

SECONDS_PER_POSE = 3.0


def read_poses(csv_path, joint_names):
    with open(csv_path, encoding="utf-8") as fp:
        return [(row["pose_id"], [math.radians(float(row[name])) for name in joint_names])
                for row in csv.DictReader(fp)]


def show(model, data, qpos_addresses, q):
    for address, value in zip(qpos_addresses, q):
        data.qpos[address] = value
    data.ctrl[:] = q
    mujoco.mj_forward(model, data)


def main(mjcf_path, csv_path, pose_id=None):
    model = load_with_display_aids(mjcf_path)
    data = mujoco.MjData(model)
    joint_names = [model.joint(i).name for i in range(model.njnt)]
    qpos_addresses = [model.jnt_qposadr[i] for i in range(model.njnt)]
    poses = read_poses(csv_path, joint_names)
    if pose_id is not None:
        poses = [p for p in poses if p[0] == pose_id]
        if not poses:
            raise ValueError(f"pose_id {pose_id} is not in {csv_path}")

    with mujoco.viewer.launch_passive(model, data) as viewer:
        index = 0
        while viewer.is_running():
            name, q = poses[index % len(poses)]
            show(model, data, qpos_addresses, q)
            print(f"{name}: {[round(math.degrees(v), 3) for v in q]} deg")
            started = time.time()
            while viewer.is_running() and (len(poses) == 1 or time.time() - started < SECONDS_PER_POSE):
                viewer.sync()
                time.sleep(0.02)
            index += 1


if __name__ == "__main__":
    main(*sys.argv[1:4])
