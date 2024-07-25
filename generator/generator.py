import matplotlib.pyplot as plt
import random
import numpy as np

def divide_rectangle(x, y, width, height, min_room_size, room_id_counter):
    if width <= min_room_size and height <= min_room_size:
        room = (x, y, width, height, room_id_counter[0])
        room_id_counter[0] += 1
        return [room]

    rooms = []
    if width <= min_room_size:
        if height > 2 * min_room_size:
            split = random.randint(min_room_size, height - min_room_size)
            rooms += divide_rectangle(x, y, width, split, min_room_size, room_id_counter)
            rooms += divide_rectangle(x, y + split, width, height - split, min_room_size, room_id_counter)
        else:
            room = (x, y, width, height, room_id_counter[0])
            room_id_counter[0] += 1
            rooms.append(room)

    elif height <= min_room_size:
        if width > 2 * min_room_size:
            split = random.randint(min_room_size, width - min_room_size)
            rooms += divide_rectangle(x, y, split, height, min_room_size, room_id_counter)
            rooms += divide_rectangle(x + split, y, width - split, height, min_room_size, room_id_counter)
        else:
            room = (x, y, width, height, room_id_counter[0])
            room_id_counter[0] += 1
            rooms.append(room)

    else:
        if width > height:
            if width > 2 * min_room_size:
                split = random.randint(min_room_size, width - min_room_size)
                rooms += divide_rectangle(x, y, split, height, min_room_size, room_id_counter)
                rooms += divide_rectangle(x + split, y, width - split, height, min_room_size, room_id_counter)
            else:
                room = (x, y, width, height, room_id_counter[0])
                room_id_counter[0] += 1
                rooms.append(room)
        else:
            if height > 2 * min_room_size:
                split = random.randint(min_room_size, height - min_room_size)
                rooms += divide_rectangle(x, y, width, split, min_room_size, room_id_counter)
                rooms += divide_rectangle(x, y + split, width, height - split, min_room_size, room_id_counter)
            else:
                room = (x, y, width, height, room_id_counter[0])
                room_id_counter[0] += 1
                rooms.append(room)

    return rooms

def generate_flat_layout(main_width, main_height, min_room_size):
    return divide_rectangle(0, 0, main_width, main_height, min_room_size, [1])

def find_adjacent_rooms(room, rooms):
    x, y, width, height, room_id = room
    adjacent = {"bottom": [], "left": [], "top": [], "right": []}

    for other in rooms:
        if other == room:
            continue
        ox, oy, owidth, oheight, other_id = other
        if y == oy + oheight and x < ox + owidth and x + width > ox:
            adjacent["bottom"].append(other_id)
        if y + height == oy and x < ox + owidth and x + width > ox:
            adjacent["top"].append(other_id)
        if x == ox + owidth and y < oy + oheight and y + height > oy:
            adjacent["left"].append(other_id)
        if x + width == ox and y < oy + oheight and y + height > oy:
            adjacent["right"].append(other_id)

    return adjacent

def plot_flat(main_width, main_height, rooms):
    fig, ax = plt.subplots()
    main_rect = plt.Rectangle((0, 0), main_width, main_height, fill=None, edgecolor='r', linewidth=2)
    ax.add_patch(main_rect)

    colors = ['b', 'g', 'y', 'c', 'm']
    corner_points = set()
    walls = []
    doors = []  # To store door positions
    for i, rect in enumerate(rooms):
        x, y, width, height, room_id = rect
        room_rect = plt.Rectangle((x, y), width, height, fill=None, edgecolor=colors[i % len(colors)], linewidth=1)
        ax.add_patch(room_rect)

        plt.text(x + width / 2, y + height / 2, str(room_id), color='black', fontsize=12, ha='center', va='center')

        corners = [(x, y, 0), (x + width, y, 0), (x, y + height, 0), (x + width, y + height, 0)]
        print(corners)
        corner_points.update(corners)

        # Collect wall segments
        walls.append(((x, y, 0), (x + width, y, 0), room_id))  # bottom wall
        walls.append(((x, y, 0), (x, y + height, 0), room_id))  # left wall
        walls.append(((x, y + height, 0), (x + width, y + height, 0), room_id))  # top wall
        walls.append(((x + width, y, 0), (x + width, y + height, 0), room_id))  # right wall

    plotted_doors = []
    for point in corner_points:
        plt.plot(point[0], point[1], 'ro')

    # Place doors in the shared walls between adjacent rooms
    min_distance_from_corner = 0.5
    door_width = 1

    wall_pairs = []  # To store pairs of corner points forming the same wall
    for room in rooms:
        adjacent_rooms = find_adjacent_rooms(room, rooms)
        x, y, width, height, room_id = room

        for direction, adj_ids in adjacent_rooms.items():
            if adj_ids:
                for adj_id in adj_ids:
                    adj_room = next((r for r in rooms if r[4] == adj_id), None)
                    if not adj_room:
                        continue

                    ax1, ay1, awidth, aheight, adj_room_id = adj_room

                    if direction == "bottom":
                        shared_wall = ((max(x, ax1), y), (min(x + width, ax1 + awidth), y))
                    elif direction == "top":
                        shared_wall = ((max(x, ax1), y + height), (min(x + width, ax1 + awidth), y + height))
                    elif direction == "left":
                        shared_wall = ((x, max(y, ay1)), (x, min(y + height, ay1 + aheight)))
                    elif direction == "right":
                        shared_wall = ((x + width, max(y, ay1)), (x + width, min(y + height, ay1 + aheight)))
                    else:
                        continue

                    (x1, y1), (x2, y2) = shared_wall
                    length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

                    if length >= 1.3:
                        if abs(x1 - x2) >= door_width:  # horizontal wall
                            mid_point = ((x1 + x2) / 2, (y1 + y2) / 2)
                            if x1 + min_distance_from_corner <= mid_point[0] - door_width / 2 and x2 - min_distance_from_corner >= mid_point[0] + door_width / 2:
                                door_start = mid_point[0] - door_width / 2
                                door_end = mid_point[0] + door_width / 2
                                overlap = any(door_start < x < door_end for x, _ in plotted_doors)
                                if not overlap:
                                    plt.plot([door_start, door_end], [mid_point[1], mid_point[1]], 'go-')
                                    plotted_doors.append((mid_point[0], mid_point[1]))
                                    doors.append(((door_start, mid_point[1], 0), (door_end, mid_point[1], 0)))

                        elif abs(y1 - y2) >= door_width:  # vertical wall
                            mid_point = ((x1 + x2) / 2, (y1 + y2) / 2)
                            if y1 + min_distance_from_corner <= mid_point[1] - door_width / 2 and y2 - min_distance_from_corner >= mid_point[1] + door_width / 2:
                                door_start = mid_point[1] - door_width / 2
                                door_end = mid_point[1] + door_width / 2
                                overlap = any(door_start < y < door_end for _, y in plotted_doors)
                                if not overlap:
                                    plt.plot([mid_point[0], mid_point[0]], [door_start, door_end], 'go-')
                                    plotted_doors.append((mid_point[0], mid_point[1]))
                                    doors.append(((mid_point[0], door_start, 0), (mid_point[0], door_end, 0)))

    plt.xlim(0, main_width)
    plt.ylim(0, main_height)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

    return rooms, corner_points, walls, doors

# Main rectangle (flat) dimensions
main_width = 20
main_height = 15

# Minimum room size
min_room_size = 4

# Generate the flat layout
rooms = generate_flat_layout(main_width, main_height, min_room_size)

# Plot the flat layout and obtain rooms
rooms, corner_points, walls, doors = plot_flat(main_width, main_height, rooms)


# Crear el mapeo de coordenadas a índices
coord_to_index = {coord: idx for idx, coord in enumerate(corner_points)}

# Crear la lista con los índices en lugar de coordenadas
indexed_wall_pairs = set(
    (coord_to_index[start], coord_to_index[end])
    for start, end, length in walls
)

# Imprimir el resultado

# Find adjacent rooms for each room
adjacent_rooms = {room: find_adjacent_rooms(room, rooms) for room in rooms}

# Print adjacent rooms for each room by their IDs
for room, adjacent in adjacent_rooms.items():
    x, y, width, height, room_id = room
    print(f"Room ID {room_id} at {room} has adjacent rooms: {adjacent}")

# Print corner points
print("vertices=", list(corner_points))
print("holes=", doors)
print("edges=", list(indexed_wall_pairs))