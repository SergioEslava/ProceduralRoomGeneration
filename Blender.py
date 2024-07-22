from enum import Enum
from typing import Iterator
import random
from typing import Any
import bpy
import bmesh
import math
import os


class CustomRoomDirection(Enum):
    SOUTH = 0
    EAST = 1
    NORTH = 2
    WEST = 3

class CustomCardinalDirection(Enum):
    CENTER = [0,0]
    SOUTH = [0,-1]
    SOUTH_EAST = [1,-1]
    EAST = [1,0]
    NORTH_EAST = [1,1]
    NORTH = [0,1]
    NORTH_WEST = [-1,1]
    WEST = [-1,0]
    SOUTH_WEST = [-1,-1]

class Room:

    walls : list[Any] = None
    parent : "Room" = None
    coor : list[int] = None
    type : int = None

    def __init__(self) -> None:
        self.parent = None
        self.walls = [None] * 4 
        self.coor = None
        self.type = None 

    def create_default() -> "Room":
        new_room = Room()
        new_room.type = -1
        new_room.coor = [0,0]
        return new_room
    
    def add_room(
            self,
            room: "Room",
            position: list[int],
            parent_direction: CustomRoomDirection,
            child_direction: CustomRoomDirection
        ):
        self.walls[child_direction.value] = room
        self.walls[child_direction.value].parent = self
        self.walls[child_direction.value].coor = position
        self.walls[child_direction.value].walls[parent_direction.value] = self

    def reconnect(self, room: "Room"):
        root = self.get_root(room)
        if room.walls[CustomRoomDirection.SOUTH.value] == None:
            room.connect_room(self.find_room_by_coor(root, room.coor[0], room.coor[1] -1), CustomRoomDirection.NORTH, CustomRoomDirection.SOUTH)
        if room.walls[CustomRoomDirection.EAST.value] == None:
            room.connect_room(self.find_room_by_coor(root, room.coor[0] +1, room.coor[1]), CustomRoomDirection.WEST, CustomRoomDirection.EAST)
        if room.walls[CustomRoomDirection.NORTH.value] == None:
            room.connect_room(self.find_room_by_coor(root, room.coor[0], room.coor[1] +1), CustomRoomDirection.SOUTH, CustomRoomDirection.NORTH)
        if room.walls[CustomRoomDirection.WEST.value] == None:
            room.connect_room(self.find_room_by_coor(root, room.coor[0] -1, room.coor[1]), CustomRoomDirection.EAST, CustomRoomDirection.WEST)
        
    def add_north(self, room:"Room"):
        new_coor = self.coor.copy()
        new_coor[1] += 1
        self.add_room(room, new_coor, CustomRoomDirection.SOUTH, CustomRoomDirection.NORTH)

    def add_south(self, room:"Room"):
        new_coor = self.coor.copy()
        new_coor[1] -= 1
        self.add_room(room, new_coor, CustomRoomDirection.NORTH, CustomRoomDirection.SOUTH)

    def add_east(self, room:"Room"):
        new_coor = self.coor.copy()
        new_coor[0] += 1
        self.add_room(room, new_coor, CustomRoomDirection.WEST, CustomRoomDirection.EAST)

    def add_west(self, room:"Room"):
        new_coor = self.coor.copy()
        new_coor[0] -= 1
        self.add_room(room, new_coor, CustomRoomDirection.EAST, CustomRoomDirection.WEST)

    def get_root(self, room:"Room"):
        if room.parent == None:
            return room
        else:
            return self.get_root(room.parent)
        
    def find_room_by_cort(self, room: "Room", x:int, y:int):
        result = None
        if room.coor[0] == x and room.coor[1] == y:
            result = room
        else:
            possible_rooms = list(filter(lambda x:(isinstance(x,Room) and x.parent == room), room.walls))
            for e in possible_rooms:
                result = self.find_room_by_cort(e,x,y)
                if result != None:
                    break
        return result
    
    def connect_room(self, room:"Room", from_direction:CustomRoomDirection, to_direction:CustomRoomDirection):
        if room != None:
            self.walls[to_direction.value] = room
            room.walls[from_direction.value] = self

    def get_cardinal_direction(self) -> list[int]:
        x = 0 if self.coor[0] == 0 else (self.coor[0]/abs(self.coor[0]))
        y = 0 if self.coor[1] == 0 else (self.coor[1]/abs(self.coor[1]))
        return [x,y]
    

class House:
    # Atributos de clase
    array_ref: list[Room] = None  # Referencia a una lista de habitaciones
    entrance: Room = None  # Referencia a la habitación de entrada
    room_itr: Iterator = None  # Iterador para recorrer las habitaciones

    def __init__(self, size=1):
        # Inicializa la lista de habitaciones con el tamaño especificado (o al menos 1)
        self.array_ref = [None] * (size if size > 0 else 1)
        # Crea la habitación de entrada por defecto
        self.entrance = Room.create_default()
        # Añade la habitación de entrada a la lista de habitaciones
        self.add_room_to_array(self.entrance)

    def add_room_to_array(self, room: Room):
        # Añade una habitación a la lista de habitaciones en la primera posición disponible (None)
        self.array_ref[self.array_ref.index(None)] = room

    def start_building(self):
        # Inicia el proceso de construcción
        self.room_itr = iter(self.array_ref)  # Crea un iterador para la lista de habitaciones
        next_room = next(self.room_itr, None)  # Obtiene la primera habitación del iterador
        if next_room is not None:
            self.build(next_room)  # Construye la habitación y sus conexiones
            self.assign_entrance_exit()  # Asigna las habitaciones de entrada y salida

    def build(self, room=None):
        # Construye las habitaciones conectadas a la habitación actual
        current_room = room if room is not None else self.entrance  # Usa la habitación actual o la entrada por defecto
        walls_max_limit = current_room.walls.count(None)  # Cuenta las paredes vacías (None) en la habitación actual
        rooms_max_limit = self.array_ref.count(None)  # Cuenta las habitaciones vacías (None) en la lista de habitaciones
        room_wall_limits = 0
        if rooms_max_limit > 0 and walls_max_limit > 0:
            # Determina el número máximo de habitaciones que se pueden añadir
            room_wall_limits = random.randint(
                1,
                min(rooms_max_limit, walls_max_limit)
            )
        # Encuentra los índices de las paredes vacías (None) en la habitación actual
        empty_wall_indices = [i for i, x in enumerate(current_room.walls) if x is None]
        for n in range(room_wall_limits):
            new_room = Room.create_default()  # Crea una nueva habitación por defecto
            self.array_ref[self.array_ref.index(None)] = new_room  # Añade la nueva habitación a la lista de habitaciones
            random_pos = random.randint(0, len(empty_wall_indices) - 1)  # Selecciona un índice aleatorio de las paredes vacías
            index = empty_wall_indices.pop(random_pos)  # Obtiene y elimina el índice seleccionado de la lista
            direction = CustomRoomDirection(index)  # Obtiene la dirección correspondiente al índice
            # Añade la nueva habitación en la dirección especificada
            if direction == CustomRoomDirection.SOUTH:
                current_room.add_south(new_room)
            if direction == CustomRoomDirection.EAST:
                current_room.add_east(new_room)
            if direction == CustomRoomDirection.NORTH:
                current_room.add_north(new_room)
            if direction == CustomRoomDirection.WEST:
                current_room.add_west(new_room)

        # Obtiene la siguiente habitación del iterador y continúa construyendo
        next_room = next(self.room_itr, None)
        if next_room is not None:
            self.build(next_room)

    def assign_entrance_exit(self):
        # Asigna las habitaciones de entrada y salida en la casa
        far = []
        # Obtiene las habitaciones más lejanas en varias direcciones cardinales y las añade a la lista 'far'
        far += self.get_farest_room(self.get_rooms_from_direction(CustomCardinalDirection.SOUTH_EAST))
        far += self.get_farest_room(self.get_rooms_from_direction(CustomCardinalDirection.NORTH_EAST))
        far += self.get_farest_room(self.get_rooms_from_direction(CustomCardinalDirection.NORTH_WEST))
        far += self.get_farest_room(self.get_rooms_from_direction(CustomCardinalDirection.SOUTH_WEST))
        far += self.get_farest_room(self.get_rooms_from_direction(CustomCardinalDirection.SOUTH))
        far += self.get_farest_room(self.get_rooms_from_direction(CustomCardinalDirection.EAST))
        far += self.get_farest_room(self.get_rooms_from_direction(CustomCardinalDirection.WEST))
        far += self.get_farest_room(self.get_rooms_from_direction(CustomCardinalDirection.NORTH))
        random.shuffle(far)  # Mezcla aleatoriamente las habitaciones en la lista 'far'
        far.append(self.entrance)  # Añade la habitación de entrada al final de la lista
        far[0].type = 0  # Asigna la primera habitación como la entrada (type 0)
        far[0].walls[far[0].walls.index(None)] = 0
        far.append(far.pop(0))  # Mueve la entrada al final de la lista
        far[0].type = 1  # Asigna la primera habitación como la salida (type 1)
        far[0].walls[far[0].walls.index(None)] = 1

    def get_rooms_from_direction(self, direction: CustomCardinalDirection):
        # Obtiene las habitaciones que están en una dirección cardinal específica
        rooms = []
        for e in self.array_ref:
            d = e.get_cardinal_direction()
            if d[0] == direction.value[0] and d[1] == direction.value[1]:
                rooms.append(e)
        return rooms

    def get_farest_room(self, rooms: list[Room]):
        # Obtiene la habitación más lejana de una lista de habitaciones
        result = []
        index = -1
        max_sum = 0
        for i, e in enumerate(rooms):
            sum_coords = abs(e.coor[0]) + abs(e.coor[1])  # Calcula la suma de las coordenadas absolutas
            if sum_coords > max_sum:
                max_sum = sum_coords
                index = i
        if index >= 0:
            result.append(rooms[index])
        return result
    
    def get_room_type(self, type):
        rooms = list(filter(lambda x : (x.type == type), self.array_ref))
        return None if len(rooms) == 0 else rooms[0]
    
    def get_all_coors(self):
        result = []
        for e in self.array_ref:
            result.append(e.coor.copy())
        return result
    
    def get_route_from_room(self, room:Room):
        result = []
        current_room = room
        while current_room != None:
            result.append(current_room.coor.copy())
            current_room = current_room.parent
        return result


# ---------------------------------------------------------------

class MyUtil():
    def assign_material(self, obj, slot = -1, material = None):
        mat = material if material != None else self.get_new_material()
        if slot >= 0:
            obj.data.materials[slot] = mat
        else:
            obj.data.materials.append(mat)
        

    def get_new_material(self):
        material = bpy.data.materials.new(name="Material")
        material.diffuse_color = (random.random(), random.random(), random.random(), 1)
        material.specular_intensity = 0
        material.roughness = 1
        return material
    
    def get_new_empty_mesh(self, name):
        mesh = bpy.data.meshes.new(name)
        object = bpy.data.objects.new(mesh.name, mesh)
        mesh.from_pydata([], [], [])
        return object
    
    def get_bound_box_size(self, ref):
        obj = ref.copy()
        room_size = (obj.bound_box[0][0] - obj.bound_box[4][0]) * 1.01
        return room_size
    
    def get_custom_copy(self, ref, location):
        obj = ref.copy()
        obj.data = obj.data.copy()
        obj.location = location
        return obj
    
    def joined(self, main, arr):
        bpy.context.view_layer.objects.active = main
        main.select_set(True)
        for e in arr:
            bpy.data.objects[e].select_set(True)
        bpy.ops.object.join()
        main.select_set(False)

    def merge_vertices_by_distance(self, object,distance):
        dg = bpy.context.evaluated_depsgraph_get()
        bm = bmesh.new()
        bm.from_object(object, dg)
        bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=distance)
        bm.to_mesh(object.data)
    
    def boolean_mod(self, object, target):
        mod = object.modifiers.new("BOOLEAN",'BOOLEAN')
        mod.object = target
        dg = bpy.context.evaluated_depsgraph_get()
        bm = bmesh.new()
        bm.from_object(object, dg)
        bm.to_mesh(object.data)
        object.modifiers.clear()
        bpy.data.objects.remove(target)

    def solidify_mod(self, object,mode,thickness,offset):
        mod = object.modifiers.new("SOLIDIFY",'SOLIDIFY')
        mod.solidify_mode = mode
        mod.thickness = thickness
        mod.offset = offset
        dg = bpy.context.evaluated_depsgraph_get()
        bm = bmesh.new()
        bm.from_object(object, dg)
        bm.to_mesh(object.data)
        object.modifiers.clear()
    
    def bevel_mod(self, object):
        mod = object.modifiers.new("BEVEL",'BEVEL')
        mod.width  =0.5
        dg = bpy.context.evaluated_depsgraph_get()
        bm = bmesh.new()
        bm.from_object(object, dg)
        bm.to_mesh(object.data)
        object.modifiers.clear()



# ---------------------------------------------------------------

# Elimina todos los objetos en la escena
for i in bpy.data.objects:
    bpy.data.objects.remove(i)

col = bpy.data.collections["Collection"]
objs = {}

with bpy.data.libraries.load("/home/usuario/cursoGeneracionProcedural/resources/Save1.blend") as (data_from, data_to):
    for e in data_from.objects:
        data_to.objects.append(e)
for e in data_to.objects:
    objs[e.name] = e

util = MyUtil()
house = House(5)
house.start_building()

out_material = util.get_new_material()
ceiling_material = util.get_new_material()

wall_object = util.get_new_empty_mesh("wall_object")
col.objects.link(wall_object)

roof_object = util.get_new_empty_mesh("roof_object")
col.objects.link(roof_object)

door_object = util.get_new_empty_mesh("door_object")
col.objects.link(door_object)

door_visual_object = util.get_new_empty_mesh("door_visual_object")
col.objects.link(door_visual_object)

window_visual_object = util.get_new_empty_mesh("window_visual_object")
col.objects.link(window_visual_object)

ground_object = util.get_new_empty_mesh("ground_object")
col.objects.link(ground_object)

furniture = util.get_new_empty_mesh("furniture")
col.objects.link(furniture)

room_size = util.get_bound_box_size(objs["Room"])

names_ref=[]
for i, e in enumerate(house.array_ref):
    obj = util.get_custom_copy(objs["Room"], (e.coor[0] * room_size, e.coor[1] * room_size, 0))
    col.objects.link(obj)
    names_ref.append(obj.name)

    util.assign_material(obj, 0, out_material)
    util.assign_material(obj, 1)
    util.assign_material(obj, 2)
    util.assign_material(obj, 3)

util.joined(wall_object, names_ref)

names_ref =[]

ground_locations =[]
for i, e in enumerate(house.array_ref):
    ground_locations.append((e.coor[0] * room_size, e.coor[1] * room_size, -0.15))
    if e.walls[0] == None or e.walls[0] in [0,1]:
        ground_locations.append((e.coor[0] * room_size, (e.coor[1] - 1) * room_size, -0.15))
        ground_locations.append(((e.coor[0] + 1) * room_size, (e.coor[1] - 1) * room_size, -0.15))
        ground_locations.append(((e.coor[0] - 1) * room_size, (e.coor[1] - 1) * room_size, -0.15))
    if e.walls[1] == None or e.walls[0] in [0,1]:
        ground_locations.append(((e.coor[0] + 1) * room_size, e.coor[1] * room_size, -0.15))
        ground_locations.append(((e.coor[0] + 1) * room_size, (e.coor[1] + 1) * room_size, -0.15))
        ground_locations.append(((e.coor[0] + 1) * room_size, (e.coor[1] - 1) * room_size, -0.15))
    if e.walls[2] == None or e.walls[0] in [0,1]:
        ground_locations.append((e.coor[0] * room_size, (e.coor[1] + 1) * room_size, -0.15))
        ground_locations.append(((e.coor[0] + 1) * room_size, (e.coor[1] + 1) * room_size, -0.15))
        ground_locations.append(((e.coor[0] - 1) * room_size, (e.coor[1] + 1) * room_size, -0.15))
    if e.walls[3] == None or e.walls[0] in [0,1]:
        ground_locations.append(((e.coor[0] - 1) * room_size, e.coor[1] * room_size, -0.15))
        ground_locations.append(((e.coor[0] - 1) * room_size, (e.coor[1] + 1) * room_size, -0.15))
        ground_locations.append(((e.coor[0] - 1) * room_size, (e.coor[1] - 1) * room_size, -0.15))

ground_locations_filter = list(set(ground_locations))
for e in ground_locations_filter:
    obj = util.get_custom_copy(objs["Ground"], e)
    col.objects.link(obj)
    names_ref.append(obj.name)
util.joined(ground_object, names_ref)

names_ref=[]
for i, e in enumerate(house.array_ref):
    obj = util.get_custom_copy(objs["Ceiling"], (e.coor[0] * room_size, e.coor[1] * room_size, 0.25))
    col.objects.link(obj)
    names_ref.append(obj.name)
    util.assign_material(obj, 0, ceiling_material)
util.joined(roof_object, names_ref)

names_ref=[]
names_window_visual_ref=[]
names_door_visual_ref=[]

door_locations_a = []
door_locations_b = []
window_locations_a = []
window_locations_b = []

for i, e in enumerate(house.array_ref):
    if (e.parent == e.walls[0] and e.parent != None) or (isinstance(e.walls[0],Room) and bool(random.getrandbits(1))) or (e.walls[0] in [0,1]):
        door_locations_a.append(((e.coor[0] * room_size), (e.coor[1] * room_size) - ( (room_size/2) + 0), 0))
    if (e.parent == e.walls[1] and e.parent != None) or (isinstance(e.walls[1],Room) and bool(random.getrandbits(1))) or (e.walls[1] in [0,1]): 
        door_locations_b.append(((e.coor[0] * room_size) + ( (room_size/2) + 0), (e.coor[1] * room_size), 0))
    if (e.parent == e.walls[2] and e.parent != None) or (isinstance(e.walls[2],Room) and bool(random.getrandbits(1))) or (e.walls[2] in [0,1]):
        door_locations_a.append(((e.coor[0] * room_size), (e.coor[1] * room_size) + ( (room_size/2) + 0), 0))
    if (e.parent == e.walls[3] and e.parent != None) or (isinstance(e.walls[3],Room) and bool(random.getrandbits(1))) or (e.walls[3] in [0,1]): 
        door_locations_b.append(((e.coor[0] * room_size) - ( (room_size/2) + 0), (e.coor[1] * room_size), 0))
    
    if bool(random.getrandbits(1)) and e.walls[0] == None:
        window_locations_a.append(((e.coor[0] * room_size), (e.coor[1] * room_size) - ( (room_size/2) + 0), 0))
    if bool(random.getrandbits(1)) and e.walls[1] == None:
        window_locations_b.append(((e.coor[0] * room_size) + ( (room_size/2) + 0), (e.coor[1] * room_size), 0))
    if bool(random.getrandbits(1)) and e.walls[2] == None:
        window_locations_a.append(((e.coor[0] * room_size), (e.coor[1] * room_size) + ( (room_size/2) + 0), 0))
    if bool(random.getrandbits(1)) and e.walls[3] == None:
        window_locations_b.append(((e.coor[0] * room_size) - ( (room_size/2) + 0), (e.coor[1] * room_size), 0))

door_locations_filter_a = list(set(door_locations_a))
door_locations_filter_b = list(set(door_locations_b))
window_locations_filter_a = list(set(window_locations_a))
window_locations_filter_b = list(set(window_locations_b))

for e in door_locations_filter_a:
    obj1 = util.get_custom_copy(objs["Door1"],e) 
    col.objects.link(obj1)
    obj2 = util.get_custom_copy(objs["DoorD1"],e) 
    col.objects.link(obj2)
    names_ref.append(obj1.name)
    names_door_visual_ref.append(obj2.name)

for e in door_locations_filter_b:
    obj1 = util.get_custom_copy(objs["Door2"],e) 
    col.objects.link(obj1)
    obj2 = util.get_custom_copy(objs["DoorD2"],e) 
    col.objects.link(obj2)
    names_ref.append(obj1.name)
    names_door_visual_ref.append(obj2.name)

for e in window_locations_filter_a:
    obj1 = util.get_custom_copy(objs["Window1"],e) 
    col.objects.link(obj1)
    obj2 = util.get_custom_copy(objs["WindowD1"],e) 
    col.objects.link(obj2)
    names_ref.append(obj1.name)
    names_window_visual_ref.append(obj2.name)

for e in window_locations_filter_b:
    obj1 = util.get_custom_copy(objs["Window2"],e) 
    col.objects.link(obj1)
    obj2 = util.get_custom_copy(objs["WindowD2"],e) 
    col.objects.link(obj2)
    names_ref.append(obj1.name)
    names_window_visual_ref.append(obj2.name)

util.joined(door_object,names_ref)
util.joined(door_visual_object,names_door_visual_ref)
util.joined(window_visual_object,names_window_visual_ref)

util.merge_vertices_by_distance(door_object,0.01)
util.merge_vertices_by_distance(ground_object,0.5)
util.boolean_mod(wall_object,door_object)
util.merge_vertices_by_distance(wall_object,0.2)

room_obj = [objs["Lamp"],objs["Books"],objs["Sofa"],objs["Table"]]
furniture_locations_a = []
furniture_locations_b = []
names_ref=[]

for e in house.array_ref:
    if bool(random.getrandbits(1)):
        furniture_locations_a.append(((e.coor[0] * room_size) + ( (room_size/4) ) , (e.coor[1] * room_size) + ( (room_size/4) ), 0.25))
    if bool(random.getrandbits(1)):
        furniture_locations_a.append(((e.coor[0] * room_size) - ( (room_size/4) ) , (e.coor[1] * room_size) + ( (room_size/4) ), 0.25))
    if bool(random.getrandbits(1)):
        furniture_locations_b.append(((e.coor[0] * room_size) - ( (room_size/4) ) , (e.coor[1] * room_size) - ( (room_size/4) ), 0.25))
    if bool(random.getrandbits(1)):
        furniture_locations_b.append(((e.coor[0] * room_size) + ( (room_size/4) ) , (e.coor[1] * room_size) - ( (room_size/4) ), 0.25))

for e in furniture_locations_a:
    obj = util.get_custom_copy(room_obj[random.randint(0,3)],e)
    obj.delta_rotation_euler = (0,0,math.pi)
    col.objects.link(obj)
    names_ref.append(obj.name)

for e in furniture_locations_b:
    obj = util.get_custom_copy(room_obj[random.randint(0,3)],e)
    col.objects.link(obj)
    names_ref.append(obj.name)

util.joined(furniture,names_ref)

util.solidify_mod(ground_object,"NON_MANIFOLD",1,-0.8)
util.bevel_mod(ground_object)

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
            '~/robocomp/components/proceduralRoomGeneration/meshes/', 
            ob.name + '.obj'
            ), use_selection=True)

    # deselect the object and move on to another if any more are left
    ob.select_set(state=False)