from enum import Enum

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