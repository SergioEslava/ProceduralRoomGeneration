from House import House
import matplotlib.pyplot as plt
import numpy as np

house = House(50)
house.start_building()

coors = house.get_all_coors()
np_coors = None
if len(coors) > 0:
    np_coors = np.array(coors)
    plt.scatter(np_coors[:,0], np_coors[:,1], color="gray")

entrance_to_center = house.get_route_from_room(house.get_room_type(0))
np_entrance_to_center = None

if len(entrance_to_center) > 0:
    np_entrance_to_center = np.array(entrance_to_center)
    plt.plot(np_entrance_to_center[:,0], np_entrance_to_center[:,1], color="red", linewidth=3)

exit_to_center = house.get_route_from_room(house.get_room_type(1))
np_exit_to_center = None

if len(exit_to_center) > 0:
    np_exit_to_center = np.array(exit_to_center)
    plt.plot(np_exit_to_center[:,0], np_exit_to_center[:,1], color="blue", linewidth=3)

plt.show()