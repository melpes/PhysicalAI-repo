import sys

import mujoco
from PIL import Image


def render_mujoco(mjcf_path, png_path):
    model = mujoco.MjModel.from_xml_path(mjcf_path)
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    camera = mujoco.MjvCamera()
    mujoco.mjv_defaultFreeCamera(model, camera)
    camera.azimuth, camera.elevation, camera.distance = -38.0, -24.0, 3.5
    with mujoco.Renderer(model, 480, 640) as renderer:
        renderer.update_scene(data, camera)
        Image.fromarray(renderer.render()).save(png_path)


if __name__ == "__main__":
    render_mujoco(sys.argv[1], sys.argv[2])
