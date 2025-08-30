# Procedural Room Generation System

This repository contains a procedural room generation system designed for dynamic environment creation, with integration into both **Blender** for 3D visualization and **Webots** for simulation. The system is based on the division of a main space into multiple rooms, which can then be processed into 3D models and used in robotics environments.

## Overview

The system consists of three main components:

1. **Room Generation Algorithm (Python)**: This generates procedural layouts of rooms within a defined space, producing a JSON representation of the room configurations.
2. **Blender Script (Python)**: A Blender script that imports the generated layout data, creates 3D models of the rooms, and incorporates doors and openings.
3. **Webots Integration (Controller)**: A Webots controller that dynamically loads the generated 3D meshes (rooms) during the simulation.

## Components

### 1. Room Generation Algorithm
The core of the system is a Python-based algorithm that divides a given rectangular area into smaller rooms. The process follows a recursive strategy to split the space based on minimum room sizes, creating random layouts. The rooms are saved as JSON data with coordinates, wall definitions, and door positions.

This process generates a set of rooms and their respective walls and doors. The JSON file containing this data is saved for use in the Blender and Webots components.

### 2. Blender Script
The Blender script is responsible for importing the room layout data (from the JSON file generated earlier) and creating 3D meshes of the rooms. Additionally, it adds holes for doors and windows by subtracting portions of the room meshes using **Boolean modifiers**.

### 3. Webots Controller
The Webots controller enables the dynamic loading of generated 3D models during simulation. The controller can switch between different room layouts by modifying the mesh URL for the walls in the Webots environment.

#### Usage
- **Keyboard Events**: Allows the user to control the loaded room layout by pressing the keys 'R' (random), 'A' (previous), or 'D' (next).

The controller allows for dynamic simulation in Webots, with the ability to load new room configurations during the simulation.

## Requirements

### Python:
- `matplotlib` (for room plotting)
- `numpy` (for numerical operations)
- `json` (for saving room data)
- `os` (for file management)
  
### Blender:
- Blender 2.8 or higher
- Python scripting enabled in Blender

### Webots:
- Webots 2023 or higher
- Python Controller API enabled

Run the `room_generation.py` script to generate a procedural room layout:

  ```bash
  python room_generation.py
