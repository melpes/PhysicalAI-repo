import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))

from neutral_scene import read_scene
from rotation import quat_to_matrix

CORNERS = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], dtype=float)


def sorted_rows(vertices):
    return np.array(sorted(map(tuple, np.round(vertices, 9))))


def main(neutral_path, blender_script_path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with open(blender_script_path, encoding="utf-8") as fp:
        exec(fp.read(), {"__name__": "__main__"})
    bpy.context.view_layer.update()
    results = []
    for obj in read_scene(neutral_path):
        expected = (CORNERS * np.array(obj["size"]) / 2) @ np.array(quat_to_matrix(obj["orientation"])).T + obj["position"]
        blender_obj = bpy.data.objects.get(obj["id"])
        if blender_obj is None:
            results.append(False)
            print(f"[FAIL] {obj['id']} 존재: Blender 객체 없음")
            continue
        vertices = np.array([list(blender_obj.matrix_world @ v.co) for v in blender_obj.data.vertices])
        error = np.abs(sorted_rows(vertices) - sorted_rows(expected)).max()
        results.append(error < 1e-6)
        print(f"[{'PASS' if error < 1e-6 else 'FAIL'}] {obj['id']} 꼭짓점 8개: 최대 오차 {error:.2e} m")
    print(f"\n{sum(results)}/{len(results)} 통과")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
