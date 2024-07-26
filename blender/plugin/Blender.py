import bpy
import bmesh
import os
import json

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

    # Hacer que el objeto sea el objeto activo y seleccionarlo
    bpy.context.view_layer.objects.active = target_object.blender_object
    target_object.blender_object.select_set(True)
    bpy.ops.object.modifier_apply(modifier=bool_modifier.name)
    
    # Hide the hole object
    bpy.context.view_layer.objects.active = hole_object.blender_object
    bpy.context.view_layer.objects.active.hide_set(True)

def process_apartment(file_path):

    util = MyUtil()
    
    with open(file_path, 'r') as file:
        data = json.load(file)

    vertices = data['vertices']
    edges = data['edges']
    holes = data['holes']

    # Elimina todos los objetos en la escena
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

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
        if abs(hole[0][1] - hole[1][1]) > 0:
            # Create the hole in the room
            create_hole(hole_position=((hole[0][0] + hole[1][0]) / 2, (hole[0][1] + hole[1][1]) / 2, 0.0), hole_object=doorHole,
                        target_object=floor_plan, hole_orientation=(0.0, 0.0, 1.57))
        else:
            create_hole(hole_position=((hole[0][0] + hole[1][0]) / 2, (hole[0][1] + hole[1][1]) / 2, 0.0), hole_object=doorHole,
                        target_object=floor_plan, hole_orientation=(0.0, 0.0, 0.0))

    # deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # make the current object active and select it
    bpy.context.view_layer.objects.active = floor_plan.blender_object
    floor_plan.blender_object.select_set(state=True)

    # make sure that we only export meshes
    if floor_plan.blender_object.type == 'MESH':
        # export the currently selected object to its own file based on its name
        bpy.ops.export_mesh.stl(filepath=os.path.join(
            os.path.dirname(file_path), 
            floor_plan.blender_object.name + '.stl'
            ), use_selection=True)

# Main loop to process multiple apartments
base_path = '/home/usuario/robocomp/components/proceduralRoomGeneration/generatedRooms/'
for i in range(0, 6):
    file_path = os.path.join(base_path, str(i), 'apartmentData.json')
    if os.path.exists(file_path):
        process_apartment(file_path)
    else:
        print(f"File {file_path} does not exist. Skipping.")