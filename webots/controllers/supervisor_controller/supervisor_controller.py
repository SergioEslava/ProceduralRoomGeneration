from controller import Supervisor
import random

# Inicializa el Supervisor
supervisor = Supervisor()
timeStep = int(supervisor.getBasicTimeStep())

# Identifica el nodo y el campo que deseas modificar
node = supervisor.getFromDef("WALLS")
urlField = node.getField("url")

# Lista de rutas de los meshes para cambiar (ejemplo)
mesh_paths = [
    "../../generatedRooms/0/ApartmentFloorPlan.stl",
    "../../generatedRooms/1/ApartmentFloorPlan.stl",
    "../../generatedRooms/2/ApartmentFloorPlan.stl",
    "../../generatedRooms/3/ApartmentFloorPlan.stl",
    "../../generatedRooms/4/ApartmentFloorPlan.stl",
    "../../generatedRooms/5/ApartmentFloorPlan.stl"
]


# Función para modificar el campo url
def update_mesh():
    new_mesh_path = random.choice(mesh_paths)
    urlField.setMFString(0, new_mesh_path)
    print(f"Nuevo mesh configurado: {new_mesh_path}")

# Habilita la captura de eventos del teclado
supervisor.keyboard.enable(timeStep)
    
while supervisor.step(timeStep) != -1:
        # Verifica si se ha pulsado alguna tecla
    key = supervisor.keyboard.getKey()
    if key == ord('R'):
        update_mesh()
        supervisor.simulationReset()

supervisor.simulationQuit(0)
