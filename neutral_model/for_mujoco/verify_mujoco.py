import sys
from pathlib import Path

import mujoco
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from neutral_scene import read_scene
from rotation import quat_to_matrix

CORNERS = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], dtype=float)
SETTLE_SECONDS = 2.0




def report(results, label, passed, detail):
    results.append(passed)
    print(f"[{'PASS' if passed else 'FAIL'}] {label}: {detail}")


def verify_object(model, data, obj, results):
    gid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, obj["id"])
    report(results, f"{obj['id']} 존재", gid >= 0, f"geom id = {gid}")
    if gid < 0:
        return
    report(results, f"{obj['id']} 형상", model.geom_type[gid] == mujoco.mjtGeom.mjGEOM_BOX,
           f"type = {mujoco.mjtGeom(model.geom_type[gid]).name}")
    half = np.array(obj["size"]) / 2
    report(results, f"{obj['id']} 크기(절반 길이)", np.allclose(model.geom_size[gid], half),
           f"MuJoCo {model.geom_size[gid]} / 중립 Size÷2 {half}")
    report(results, f"{obj['id']} 위치", np.allclose(model.geom_pos[gid], obj["position"]),
           f"MuJoCo {model.geom_pos[gid]} / 중립 {obj['position']}")
    q = np.array(obj["orientation"]) / np.linalg.norm(obj["orientation"])
    same_rotation = np.allclose(model.geom_quat[gid], q) or np.allclose(model.geom_quat[gid], -q)
    report(results, f"{obj['id']} 회전", same_rotation, f"MuJoCo {model.geom_quat[gid]} / 중립 {q}")
    report(results, f"{obj['id']} 색", np.allclose(model.geom_rgba[gid], obj["color"], atol=1e-6),
           f"MuJoCo {model.geom_rgba[gid]} / 중립 {obj['color']}")

    mujoco.mj_forward(model, data)
    simulated = (CORNERS * model.geom_size[gid]) @ data.geom_xmat[gid].reshape(3, 3).T + data.geom_xpos[gid]
    expected = (CORNERS * half) @ np.array(quat_to_matrix(q)).T + obj["position"]
    error = np.abs(simulated - expected).max()
    report(results, f"{obj['id']} 꼭짓점 8개", error < 1e-9, f"최대 오차 {error:.2e} m")

    start = data.geom_xpos[gid].copy()
    for _ in range(int(SETTLE_SECONDS / model.opt.timestep)):
        mujoco.mj_step(model, data)
    moved = np.abs(data.geom_xpos[gid] - start).max()
    report(results, f"{obj['id']} 고정 물체 유지", moved < 1e-12,
           f"{SETTLE_SECONDS}초 시뮬레이션 후 이동량 {moved:.2e} m")


def main(neutral_path, mjcf_path):
    model = mujoco.MjModel.from_xml_path(mjcf_path)
    data = mujoco.MjData(model)
    results = []
    report(results, "MJCF 불러오기", True, f"MuJoCo {mujoco.__version__}, geom {model.ngeom}개")
    for obj in read_scene(neutral_path):
        mujoco.mj_resetData(model, data)
        verify_object(model, data, obj, results)
    print(f"\n{sum(results)}/{len(results)} 통과")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
