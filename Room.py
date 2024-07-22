from typing import Any
from Constant import CustomRoomDirection

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

        


    