from vcScript import *

app = getApplication()


def place_box(box_id, size_mm, origin_mm, axis, angle_deg, rgba):
    comp = app.findComponent(box_id)
    if comp is None:
        comp = app.createComponent()
        comp.Name = box_id
    block = comp.findFeature(box_id)
    if block is None:
        block = comp.RootFeature.createFeature(VC_BLOCK, box_id)
    block.Length = str(size_mm[0])
    block.Width = str(size_mm[1])
    block.Height = str(size_mm[2])

    material = app.findMaterial(box_id + "_material", True)
    if material is None:
        material = app.createMaterial(box_id + "_material")
        app.addMaterial(material)
    diffuse = material.Diffuse
    diffuse.X, diffuse.Y, diffuse.Z = rgba[0], rgba[1], rgba[2]
    material.Diffuse = diffuse
    material.Opacity = rgba[3]
    block.Material = material
    block.rebuild()

    matrix = comp.PositionMatrix
    matrix.setAxisAngle(axis[0], axis[1], axis[2], angle_deg)
    position = matrix.P
    position.X, position.Y, position.Z = origin_mm
    matrix.P = position
    comp.PositionMatrix = matrix
    comp.rebuild()

    p = comp.PositionMatrix.P
    print("%s position (mm): %.3f %.3f %.3f" % (box_id, p.X, p.Y, p.Z))
    print("%s WPR (deg): %s" % (box_id, comp.PositionMatrix.WPR))
    print("%s block L/W/H (mm): %s %s %s" % (box_id, block.Length, block.Width, block.Height))
    if hasattr(comp, "BoundCenter"):
        print("%s bound center in component frame (mm): %s" % (box_id, comp.BoundCenter))

place_box('Box_01', (1150.0, 850.0, 280.0), (500.0, 200.0, 0.0), (0.0, 0.0, 1.0), 30.0, (0.95, 0.64, 0.12, 1.0))
app.render()
