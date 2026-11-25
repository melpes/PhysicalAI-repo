import bpy


def add_box(obj_id, size, position, quaternion, rgba_linear):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=position)
    obj = bpy.context.active_object
    obj.name = obj_id
    obj.scale = size
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = quaternion
    material = bpy.data.materials.new(obj_id + "_material")
    if material.node_tree is None:
        material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba_linear
    material.diffuse_color = rgba_linear
    obj.data.materials.append(material)

add_box('Box_01', (1.15, 0.85, 0.28), (0.5, 0.2, 0.14), (0.9659258262890683, 0.0, 0.0, 0.25881904510252074), (0.8900054069935289, 0.3672464682101826, 0.01341174889765847, 1.0))
