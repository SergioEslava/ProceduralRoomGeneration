from Room import Room
from typing import Iterator
from Constant import CustomRoomDirection, CustomCardinalDirection
import random

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
