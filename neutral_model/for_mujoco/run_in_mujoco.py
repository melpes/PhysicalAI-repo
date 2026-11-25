import sys
from pathlib import Path

import mujoco
import mujoco.viewer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from neutral_scene import read_scene


def build_model(neutral_path):
    spec = mujoco.MjSpec()
    for obj in read_scene(neutral_path):
        geom = spec.worldbody.add_geom()
        geom.name = obj["id"]
        geom.type = mujoco.mjtGeom.mjGEOM_BOX
        geom.size = [s / 2 for s in obj["size"]]
        geom.pos = obj["position"]
        geom.quat = obj["orientation"]
        geom.rgba = obj["color"]
    return spec.compile()


if __name__ == "__main__":
    mujoco.viewer.launch(build_model(sys.argv[1]))
