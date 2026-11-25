import csv
import math
import sys

import mujoco
from PIL import Image, ImageDraw

from display_aids import load_with_display_aids

TILE_WIDTH, TILE_HEIGHT, COLUMNS = 480, 400, 4


def render_mujoco_robot(mjcf_path, csv_path, png_path):
    model = load_with_display_aids(mjcf_path)
    data = mujoco.MjData(model)
    with open(csv_path, encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    camera = mujoco.MjvCamera()
    mujoco.mjv_defaultFreeCamera(model, camera)
    camera.azimuth, camera.elevation, camera.distance = -60.0, -15.0, 7.5
    camera.lookat[:] = [0.2, 0.0, 0.6]
    sheet = Image.new("RGB", (TILE_WIDTH * COLUMNS, TILE_HEIGHT * math.ceil(len(rows) / COLUMNS)), "white")
    with mujoco.Renderer(model, TILE_HEIGHT, TILE_WIDTH) as renderer:
        for k, row in enumerate(rows):
            for i in range(model.njnt):
                data.qpos[model.jnt_qposadr[i]] = math.radians(float(row[model.joint(i).name]))
            mujoco.mj_forward(model, data)
            renderer.update_scene(data, camera)
            tile = Image.fromarray(renderer.render())
            ImageDraw.Draw(tile).text((10, 10), row["pose_id"], fill="white")
            sheet.paste(tile, ((k % COLUMNS) * TILE_WIDTH, (k // COLUMNS) * TILE_HEIGHT))
    sheet.save(png_path)


if __name__ == "__main__":
    render_mujoco_robot(sys.argv[1], sys.argv[2], sys.argv[3])
