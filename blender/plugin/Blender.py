import bpy
import bmesh
import os


class MyUtil:
    def solidify_mod(self, object, mode, thickness, offset):
        mod = object.modifiers.new("SOLIDIFY", 'SOLIDIFY')
        mod.solidify_mode = mode
        mod.thickness = thickness
        mod.offset = offset
        dg = bpy.context.evaluated_depsgraph_get()
        bm = bmesh.new()
        bm.from_object(object, dg)
        bm.to_mesh(object.data)
        object.modifiers.clear()


class CustomMesh:
    def __init__(self, vertices=[], edges=[], faces=[], name="CustomObject"):
        self.vertices = vertices
        self.edges = edges
        self.faces = faces
        self.name = name
        self.create_mesh()

    def create_mesh(self):
        # Create a new mesh
        mesh = bpy.data.meshes.new(name=self.name)

        # Create a new object with the mesh
        obj = bpy.data.objects.new(name=self.name, object_data=mesh)

        # Link the object to the scene collection
        bpy.context.collection.objects.link(obj)

        # Set the object as active and select it
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Create a BMesh object and fill it with the mesh data
        bm = bmesh.new()

        # Add the vertices to the BMesh
        for vert in self.vertices:
            bm.verts.new(vert)

        # Ensure all vertices are used
        bm.verts.ensure_lookup_table()

        # Add the edges to the BMesh
        for edge in self.edges:
            bm.edges.new([bm.verts[i] for i in edge])

        # Add the faces to the BMesh
        for face in self.faces:
            bm.faces.new([bm.verts[i] for i in face])

        # Update the BMesh and write it to the mesh
        bm.to_mesh(mesh)
        bm.free()

        # Assign the object to self so it can be accessed for modifiers
        self.blender_object = obj

    def add_modifier(self, modifier_type, **kwargs):
        modifier = self.blender_object.modifiers.new(name=modifier_type, type=modifier_type)
        for key, value in kwargs.items():
            setattr(modifier, key, value)
        return modifier


def create_hole(hole_position, hole_object, target_object, hole_orientation):
    # Move the hole object to the specified position
    hole_object.blender_object.location = hole_position

    hole_object.blender_object.rotation_euler = hole_orientation

    # Add a boolean modifier to the target object to subtract the hole
    bool_modifier = target_object.add_modifier('BOOLEAN', operation='DIFFERENCE')
    bool_modifier.use_self = True
    bool_modifier.object = hole_object.blender_object

    # Recalculate normals for the hole object

    bpy.ops.object.mode_set(mode='EDIT')  # Switch to Edit Mode
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)  # Recalculate normals
    bpy.ops.object.mode_set(mode='OBJECT')  # Switch back to Object Mode

    # Hide the hole object
    bpy.context.view_layer.objects.active = hole_object.blender_object
    bpy.context.view_layer.objects.active.hide_set(True)


# Optionally, add a solidify modifier to give walls some thickness
util = MyUtil()
# Elimina todos los objetos en la escena
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj, do_unlink=True)

# Define vertices and edges for a simple apartment floor plan
vertices= [(6, 0, 0), (5, 14, 0), (30, 12, 0), (12, 14, 0), (18, 14, 0), (5, 20, 0), (18, 7, 0), (0, 14, 0), (18, 20, 0), (25, 12, 0), (6, 8, 0), (0, 20, 0), (30, 20, 0), (12, 20, 0), (12, 0, 0), (18, 0, 0), (25, 20, 0), (25, 7, 0), (0, 0, 0), (25, 0, 0), (30, 0, 0), (5, 8, 0), (18, 8, 0), (0, 8, 0), (12, 8, 0), (25, 6, 0), (30, 6, 0), (18, 12, 0)]
holes= [((2.0, 8.0, 0), (3.0, 8.0, 0)), ((6.0, 3.5, 0), (6.0, 4.5, 0)), ((8.5, 8.0, 0), (9.5, 8.0, 0)), ((14.5, 8.0, 0), (15.5, 8.0, 0)), ((18.0, 3.0, 0), (18.0, 4.0, 0)), ((5.0, 10.5, 0), (5.0, 11.5, 0)), ((5.0, 16.5, 0), (5.0, 17.5, 0)), ((8.0, 14.0, 0), (9.0, 14.0, 0)), ((18.0, 9.5, 0), (18.0, 10.5, 0)), ((18.0, 12.5, 0), (18.0, 13.5, 0)), ((21.0, 7.0, 0), (22.0, 7.0, 0)), ((25.0, 2.5, 0), (25.0, 3.5, 0)), ((25.0, 9.0, 0), (25.0, 10.0, 0)), ((25.0, 15.5, 0), (25.0, 16.5, 0)), ((27.0, 6.0, 0), (28.0, 6.0, 0))]
edges= [(18, 23), (23, 7), (3, 4), (23, 10), (6, 27), (17, 9), (5, 13), (20, 26), (3, 13), (9, 2), (11, 5), (0, 14), (1, 3), (26, 2), (25, 26), (13, 8), (7, 1), (10, 24), (22, 4), (6, 17), (4, 8), (21, 24), (23, 21), (27, 9), (14, 15), (14, 24), (9, 16), (0, 10), (19, 17), (1, 5), (25, 9), (19, 20), (18, 0), (16, 12), (24, 22), (15, 19), (15, 22), (27, 8), (8, 16), (24, 3), (19, 25), (15, 6), (2, 12), (7, 11), (21, 1)]



# Create the floor plan mesh
floor_plan = CustomMesh(vertices=vertices, edges=edges, name="ApartmentFloorPlan")

bpy.context.view_layer.objects.active = floor_plan.blender_object
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.extrude_region_move(
    MESH_OT_extrude_region={"use_normal_flip": False, "use_dissolve_ortho_edges": False, "mirror": False},
    TRANSFORM_OT_translate={"value": (0, 0, 3), "orient_type": 'GLOBAL',
                            "orient_matrix": ((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type": 'GLOBAL',
                            "constraint_axis": (False, False, True), "mirror": False, "use_proportional_edit": False,
                            "proportional_edit_falloff": 'SMOOTH', "proportional_size": 1,
                            "use_proportional_connected": False, "use_proportional_projected": False, "snap": False,
                            "snap_elements": {'INCREMENT'}, "use_snap_project": False, "snap_target": 'CLOSEST',
                            "use_snap_self": True, "use_snap_edit": True, "use_snap_nonedit": True,
                            "use_snap_selectable": False, "snap_point": (0, 0, 0), "snap_align": False,
                            "snap_normal": (0, 0, 0), "gpencil_strokes": False, "cursor_transform": False,
                            "texture_space": False, "remove_on_cancel": False, "use_duplicated_keyframes": False,
                            "view2d_edge_pan": False, "release_confirm": False, "use_accurate": False,
                            "use_automerge_and_split": False})
bpy.ops.object.editmode_toggle()
util.solidify_mod(floor_plan.blender_object, mode='NON_MANIFOLD', thickness=0.2, offset=0)

# Define the vertices and faces for the door hole (assuming a simple rectangular hole)
door_vertices = [
    (-0.5, -0.3, 0.0),  # 0 - Bottom vertices
    (0.5, -0.3, 0.0),  # 1
    (0.5, 0.3, 0.0),  # 2
    (-0.5, 0.3, 0.0),  # 3
    (-0.5, -0.3, 2.0),  # 4 - Top vertices
    (0.5, -0.3, 2.0),  # 5
    (0.5, 0.3, 2.0),  # 6
    (-0.5, 0.3, 2.0)  # 7
]

door_faces = [
    (0, 1, 2, 3),  # Front
    (4, 5, 6, 7),  # Back
    (0, 1, 5, 4),  # Bottom
    (2, 3, 7, 6),  # Top
    (0, 3, 7, 4),  # Left
    (1, 2, 6, 5)  # Right
]

for hole in holes:
    # Create an instance of CustomMesh for the door hole with the defined vertices and faces
    doorHole = CustomMesh(vertices=door_vertices, faces=door_faces, name="DoorHole")
    print("HOLE", hole, "is vertical", abs(hole[0][1] - hole[1][1]) > 0)
    if abs(hole[0][1] - hole[1][1]) > 0:
    # Create the hole in the room
        create_hole(hole_position=((hole[0][0] + hole[1][0]) / 2, (hole[0][1] + hole[1][1]) / 2, 0.0), hole_object=doorHole,
                target_object=floor_plan, hole_orientation=(0.0, 0.0, 1.57))
    else:
        create_hole(hole_position=((hole[0][0] + hole[1][0]) / 2, (hole[0][1] + hole[1][1]) / 2, 0.0), hole_object=doorHole,
                target_object=floor_plan, hole_orientation=(0.0, 0.0, 0.0))

# Hacer que el objeto sea el objeto activo y seleccionarlo
bpy.context.view_layer.objects.active = floor_plan
floor_plan.select_set(True)
for modifier in floor_plan.blender_object.modifiers:
    bpy.ops.object.modifier_apply(modifier=modifier.name)

# deselect all objects
bpy.ops.object.select_all(action='DESELECT')    

# loop through all the objects in the scene
for ob in bpy.context.scene.objects:
    # make the current object active and select it
    bpy.context.view_layer.objects.active = ob
    ob.select_set(state=True)

    # make sure that we only export meshes
    if ob.type == 'MESH':
        # export the currently selected object to its own file based on its name
        bpy.ops.export_mesh.stl(filepath=os.path.join(
            '/home/usuario/robocomp/Repositories/proceduralRoomGeneration/generatedRooms/', 
            ob.name + '.stl'
            ), use_selection=True)

    # deselect the object and move on to another if any more are left
    ob.select_set(state=False)

