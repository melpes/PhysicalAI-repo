import mujoco

FLOOR_HALF_SIZE = 3.0
FLOOR_RGBA = [0.8, 0.85, 0.9, 0.4]


def load_with_display_aids(mjcf_path):
    """Load an MJCF and add a floor grid and a light for viewing only.

    These are not part of the neutral model, so they are added here and never
    written back into the converted MJCF.
    """
    spec = mujoco.MjSpec.from_file(mjcf_path)
    floor = spec.worldbody.add_geom()
    floor.name = "DisplayFloor"
    floor.type = mujoco.mjtGeom.mjGEOM_PLANE
    floor.size = [FLOOR_HALF_SIZE, FLOOR_HALF_SIZE, 0.05]
    floor.rgba = FLOOR_RGBA
    floor.contype = 0
    floor.conaffinity = 0
    light = spec.worldbody.add_light()
    light.name = "DisplayLight"
    light.pos = [1.0, -2.0, 5.0]
    light.dir = [-0.2, 0.4, -1.0]
    return spec.compile()
