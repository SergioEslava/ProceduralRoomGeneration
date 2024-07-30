from controller import Supervisor
import random
import os
import time

# Inicializa el Supervisor
supervisor = Supervisor()
timeStep = int(supervisor.getBasicTimeStep())
mesh_index = 0

# Identifica el nodo y el campo que deseas modificar
node = supervisor.getFromDef("WALLS")
urlField = node.getField("url")

base_path = '/home/robocomp/robocomp/components/proceduralRoomGeneration/generatedRooms/'
# Lista de rutas de los meshes para cambiar (ejemplo)
folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
mesh_paths = [os.path.join(base_path, f, 'ApartmentFloorPlan.stl') for f in folders]
# order the list of meshes by numerical order (10 goes after 9)
mesh_paths.sort(key=lambda x: int(x.split('/')[-2]))

print(f"Meshes disponibles: {mesh_paths}")



# Función para modificar el campo url
def update_mesh_random():
    new_mesh_path = random.choice(mesh_paths)
    urlField.setMFString(0, new_mesh_path)
    time.sleep(0.1)
    print(f"Nuevo mesh configurado: {new_mesh_path}")

def update_mesh(mesh_index):
    new_mesh_path = mesh_paths[mesh_index]
    urlField.setMFString(0, new_mesh_path)
    time.sleep(0.1)
    print(f"Nuevo mesh configurado: {new_mesh_path}")


# Habilita la captura de eventos del teclado
supervisor.keyboard.enable(timeStep)
    
while supervisor.step(timeStep) != -1:
        # Verifica si se ha pulsado alguna tecla
    key = supervisor.keyboard.getKey()
    if key == ord('R'):
        update_mesh_random()
        supervisor.simulationReset()
    if key == ord('A'):
        mesh_index -= 1
        if mesh_index < 0:
            mesh_index = len(mesh_paths) - 1
        update_mesh(mesh_index)

        supervisor.simulationReset()
    if key == ord('D'):
        mesh_index += 1
        if mesh_index > len(mesh_paths) - 1:
            mesh_index = 0
        update_mesh(mesh_index)

        supervisor.simulationReset()


supervisor.simulationQuit(0)
