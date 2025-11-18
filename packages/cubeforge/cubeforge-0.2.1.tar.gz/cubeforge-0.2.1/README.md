# CubeForge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**CubeForge** is a Python library designed to easily generate 3D mesh files (currently STL format) by defining models voxel by voxel. It allows for flexible voxel dimensions and positioning using various anchor points.

## Features

- [x] **Voxel-based Modeling:** Define 3D shapes by adding individual voxels (cubes).
- [x] **Non-Uniform Voxel Dimensions:** Specify default non-uniform dimensions for a model, and override dimensions on a per-voxel basis.
- [x] **Flexible Anchoring:** Position voxels using different anchor points ([`cubeforge.CubeAnchor`](cubeforge/constants.py)) like corners or centers.
- [x] **Configurable Coordinate Systems:** Choose between Y-up (default) or Z-up coordinate systems for compatibility with different tools.
- [x] **Mesh Optimization:** Optional greedy meshing algorithm reduces file sizes by 10-100× for regular structures.
- [x] **STL Export:** Save the generated mesh to both ASCII and Binary STL file formats.
- [x] **Simple API:** Easy-to-use interface with the core [`cubeforge.VoxelModel`](cubeforge/model.py) class.

## Installation

**Install from PyPI:**
You can install CubeForge directly from [PyPI](https://pypi.org/project/cubeforge/) using `pip`:

```bash
pip install cubeforge
```

**Install from source:**
You can also clone the repository and install the package using `pip`:

```bash
pip install .
```

## Usage

Here's a basic example of how to create a simple shape and save it as an STL file:

```python
import cubeforge
import os

# Create a model with default 1x1x1 voxel dimensions
model = cubeforge.VoxelModel()

# Add some voxels using the default CORNER_NEG anchor
model.add_voxel(0, 0, 0)
model.add_voxel(1, 0, 0)
model.add_voxel(1, 1, 0)

# --- Or add multiple voxels at once ---
# model.add_voxels([(0, 0, 0), (1, 0, 0), (1, 1, 0)])

# --- Example with custom dimensions per voxel ---
tower_model = cubeforge.VoxelModel(voxel_dimensions=(1.0, 1.0, 1.0))
# Add a 1x1x1 base cube centered at (0,0,0)
tower_model.add_voxel(0, 0, 0, anchor=cubeforge.CubeAnchor.CENTER)
# Stack a wide, flat 3x0.5x3 cube on top of it
tower_model.add_voxel(0, 0.5, 0, anchor=cubeforge.CubeAnchor.BOTTOM_CENTER, dimensions=(3.0, 0.5, 3.0))

# Define output path
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)
output_filename = os.path.join(output_dir, "my_shape.stl")

# Save the mesh as a binary STL file
model.save_mesh(output_filename, format='stl_binary', solid_name="MyCustomShape")

print(f"Saved mesh to {output_filename}")
```

## Coordinate Systems

CubeForge supports two coordinate system modes:

### Y-up Mode (Default)
In Y-up mode, the Y axis represents the vertical/height direction:
- Coordinates: `(x, y, z)` where y is up
- Dimensions: `(width, height, depth)` maps to `(x, y, z)`
- `BOTTOM_CENTER`/`TOP_CENTER` anchors refer to Y faces

**Note:** Models created in Y-up mode will appear rotated 90° in most STL viewers and 3D printing slicers, which expect Z-up orientation.

### Z-up Mode (Recommended for 3D Printing)
In Z-up mode, the Z axis represents the vertical/height direction:
- Coordinates: `(x, y, z)` where z is up
- Dimensions: `(width, depth, height)` maps to `(x, y, z)`
- `BOTTOM_CENTER`/`TOP_CENTER` anchors refer to Z faces

**This mode ensures exported STL files appear correctly oriented in most 3D printing slicers and CAD programs.**

### Example: Creating a Vertical Tower for 3D Printing

```python
import cubeforge

# Create model in Z-up mode for correct STL orientation
model = cubeforge.VoxelModel(voxel_dimensions=(1.0, 1.0, 1.0), coordinate_system='z_up')

# Stack voxels vertically along Z axis
model.add_voxel(0, 0, 0)  # Bottom
model.add_voxel(0, 0, 1)  # Middle
model.add_voxel(0, 0, 2)  # Top

# Save - will appear correctly oriented in slicers!
model.save_mesh("tower.stl", format='stl_binary')
```

## Mesh Optimization

CubeForge uses **greedy meshing** optimization by default to dramatically reduce file sizes for voxel-based models.

### How It Works

Instead of creating separate triangles for each voxel face, the optimizer merges adjacent coplanar faces into larger rectangles:

```
Without optimization (9 voxels):     With optimization:
[■][■][■]  9 quads = 18 triangles    [■■■■■■■]  1 quad = 2 triangles
[■][■][■]                            [■■■■■■■]
[■][■][■]                            [■■■■■■■]
```

### Usage

Optimization is **enabled by default** - just use `save_mesh()`:

```python
import cubeforge

model = cubeforge.VoxelModel(coordinate_system='z_up')

# Create a large flat surface
for x in range(20):
    for y in range(20):
        model.add_voxel(x, y, 0)

# Save - optimization enabled by default, 99% smaller!
model.save_mesh("surface.stl")

# To disable optimization (not recommended):
# model.save_mesh("surface.stl", optimize=False)
```

**When to disable:** Only if you specifically need individual voxel faces preserved (rare).

## Examples

### Basic Shapes Example
The [`examples/create_shapes.py`](examples/create_shapes.py) script demonstrates various features, including:
*   Creating simple and complex shapes.
*   Using different default voxel dimensions.
*   Overriding dimensions for individual voxels.
*   Utilizing various [`CubeAnchor`](cubeforge/constants.py) options.
*   Saving in both ASCII and Binary STL formats.
*   Generating a surface with random heights.

### Coordinate Systems Example
The [`examples/coordinate_systems.py`](examples/coordinate_systems.py) script demonstrates:
*   Comparing Y-up vs Z-up coordinate systems
*   Creating vertical towers in both modes
*   Using `BOTTOM_CENTER` and `TOP_CENTER` anchors correctly in Z-up mode
*   Custom dimensions in Z-up mode for 3D printing

### Mesh Optimization Example
The [`examples/mesh_optimization.py`](examples/mesh_optimization.py) script demonstrates:
*   Comparing file sizes with and without optimization
*   Greedy meshing on various model types (surfaces, cubes, towers)
*   Real-world performance measurements
*   When optimization provides the most benefit

To run the examples:

```bash
python examples/create_shapes.py
python examples/coordinate_systems.py
python examples/mesh_optimization.py
```

The output STL files will be saved in the [`examples`](examples) directory.

## API Overview

*   **[`cubeforge.VoxelModel`](cubeforge/model.py):** The main class for creating and managing the voxel model.
    *   [`__init__(self, voxel_dimensions=(1.0, 1.0, 1.0), coordinate_system='y_up')`](cubeforge/model.py): Initializes the model with default voxel dimensions and coordinate system. Use `coordinate_system='z_up'` for 3D printing.
    *   [`add_voxel(self, x, y, z, anchor=CubeAnchor.CORNER_NEG, dimensions=None)`](cubeforge/model.py): Adds a single voxel, optionally with custom dimensions.
    *   [`add_voxels(self, coordinates, anchor=CubeAnchor.CORNER_NEG, dimensions=None)`](cubeforge/model.py): Adds multiple voxels, optionally with custom dimensions.
    *   [`remove_voxel(self, x, y, z, anchor=CubeAnchor.CORNER_NEG)`](cubeforge/model.py): Removes a voxel.
    *   [`clear(self)`](cubeforge/model.py): Removes all voxels.
    *   [`generate_mesh(self, optimize=True)`](cubeforge/model.py): Generates the triangle mesh data. Optimization enabled by default. Set `optimize=False` to disable.
    *   [`save_mesh(self, filename, format='stl_binary', optimize=True, **kwargs)`](cubeforge/model.py): Generates and saves the mesh to a file. Optimization enabled by default for smaller files.
*   **[`cubeforge.CubeAnchor`](cubeforge/constants.py ):** An [`enum`](/opt/homebrew/Cellar/python@3.13/3.13.2/Frameworks/Python.framework/Versions/3.13/lib/python3.13/enum.py ) defining the reference points for voxel placement ([`CORNER_NEG`](cubeforge/constants.py ), [`CENTER`](cubeforge/constants.py ), [`CORNER_POS`](cubeforge/constants.py ), [`BOTTOM_CENTER`](cubeforge/constants.py ), [`TOP_CENTER`](cubeforge/constants.py )).
*   **[`cubeforge.get_writer(format_id)`](cubeforge/writers.py ):** Factory function to get mesh writer instances (used internally by [`save_mesh`](cubeforge/model.py )). Supports `'stl'`, `'stl_binary'`, `'stl_ascii'`.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests on the [GitHub repository](https://github.com/Teddy-van-Jerry/cubeforge).

## License

This project is licensed under the [MIT License](LICENSE).

This project is developed and maintained by [Teddy van Jerry](https://github.com/Teddy-van-Jerry) ([Wuqiong Zhao](https://wqzhao.org)).
The development is assisted by *Gemini 2.5 Pro* and *Claude Code*.
