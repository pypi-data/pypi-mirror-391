# cubeforge/model.py
import logging
from .constants import CubeAnchor
from .writers import get_writer # Use the generalized writer system

# --- Logging Configuration Removed ---
# Get a logger instance for this module. Configuration is left to the application.
logger = logging.getLogger(__name__)


class VoxelModel:
    """
    Represents a 3D model composed of voxels.
    Each voxel can have independent dimensions (width, height, depth).

    Allows adding voxels based on coordinates and anchor points, and exporting
    the resulting shape using various mesh writers. Logging messages are emitted
    via the standard 'logging' module; configuration is up to the application.
    """
    def __init__(self, voxel_dimensions=(1.0, 1.0, 1.0), coordinate_system='y_up'):
        """
        Initializes the VoxelModel.

        Args:
            voxel_dimensions (tuple): A tuple of three positive numbers representing the
                                     default size of each voxel.
                                     - In Y-up mode: (width, height, depth) = (x, y, z)
                                     - In Z-up mode: (width, depth, height) = (x, y, z)
            coordinate_system (str): The coordinate system to use. Either 'y_up' (default)
                                    or 'z_up'. Use 'z_up' for 3D printing to ensure correct
                                    orientation in most slicers.
        """
        if not (isinstance(voxel_dimensions, (tuple, list)) and
                len(voxel_dimensions) == 3 and
                all(isinstance(dim, (int, float)) and dim > 0 for dim in voxel_dimensions)):
            raise ValueError("voxel_dimensions must be a tuple or list of three positive numbers.")
        if coordinate_system not in ('y_up', 'z_up'):
            raise ValueError("coordinate_system must be either 'y_up' or 'z_up'.")

        self.voxel_dimensions = tuple(float(dim) for dim in voxel_dimensions)
        # Stores voxel data as a dictionary:
        # key: integer grid coordinate (ix, iy, iz)
        # value: tuple of dimensions (width, height, depth) for that voxel
        self._voxels = {}
        # Coordinate system: 'y_up' (default) or 'z_up'
        self._coordinate_system = coordinate_system
        logger.info(f"VoxelModel initialized with default voxel_dimensions={self.voxel_dimensions}, coordinate_system={coordinate_system}")

    def set_y_up(self):
        """
        Sets the coordinate system to Y-up mode.

        .. deprecated::
            Prefer setting coordinate_system='y_up' in __init__() instead.
            Changing coordinate systems after initialization can be confusing.

        In Y-up mode (default):
        - Y axis represents vertical/height
        - Coordinates are (x, y, z) where y is up
        - Dimensions are (width, height, depth) = (x, y, z)
        - BOTTOM_CENTER/TOP_CENTER refer to Y faces
        """
        if self._coordinate_system == 'z_up':
            # Swap voxel_dimensions from Z-up back to Y-up
            self.voxel_dimensions = (self.voxel_dimensions[0], self.voxel_dimensions[2], self.voxel_dimensions[1])
        self._coordinate_system = 'y_up'
        logger.info("Coordinate system set to Y-up")

    def set_z_up(self):
        """
        Sets the coordinate system to Z-up mode.

        .. deprecated::
            Prefer setting coordinate_system='z_up' in __init__() instead.
            Changing coordinate systems after initialization can be confusing.

        In Z-up mode (common for STL viewers/slicers):
        - Z axis represents vertical/height
        - Coordinates are (x, y, z) where z is up
        - Dimensions are (width, depth, height) = (x, y, z)
        - BOTTOM_CENTER/TOP_CENTER refer to Z faces

        This mode ensures exported STL files appear correctly oriented
        in most 3D printing slicers and CAD programs.
        """
        if self._coordinate_system == 'y_up':
            # Swap voxel_dimensions from Y-up to Z-up
            self.voxel_dimensions = (self.voxel_dimensions[0], self.voxel_dimensions[2], self.voxel_dimensions[1])
        self._coordinate_system = 'z_up'
        logger.info("Coordinate system set to Z-up")

    def _swap_yz_if_needed(self, x, y, z):
        """Helper method to swap Y and Z coordinates when in Z-up mode."""
        if self._coordinate_system == 'z_up':
            return x, z, y
        return x, y, z

    def _swap_yz_dims_if_needed(self, dimensions):
        """Helper method to swap Y and Z in dimension tuples when in Z-up mode."""
        if self._coordinate_system == 'z_up':
            return (dimensions[0], dimensions[2], dimensions[1])
        return dimensions

    def _calculate_min_corner(self, x, y, z, anchor, dimensions):
        """
        Calculates the minimum corner coordinates based on anchor point and voxel dimensions.

        Internal helper method used by add_voxel and remove_voxel.

        Args:
            x (float): X-coordinate of the anchor point.
            y (float): Y-coordinate of the anchor point.
            z (float): Z-coordinate of the anchor point.
            anchor (CubeAnchor): The anchor type.
            dimensions (tuple): The (width, height, depth) of the voxel.

        Returns:
            tuple: (min_x, min_y, min_z) coordinates of the voxel's minimum corner.

        Raises:
            ValueError: If an invalid anchor point is provided.
        """
        size_x, size_y, size_z = dimensions
        half_x, half_y, half_z = size_x / 2.0, size_y / 2.0, size_z / 2.0

        if anchor == CubeAnchor.CORNER_NEG:
            min_x, min_y, min_z = x, y, z
        elif anchor == CubeAnchor.CENTER:
            min_x, min_y, min_z = x - half_x, y - half_y, z - half_z
        elif anchor == CubeAnchor.CORNER_POS:
            min_x, min_y, min_z = x - size_x, y - size_y, z - size_z
        elif anchor == CubeAnchor.BOTTOM_CENTER:
            # In Y-up: center of min Y face; In Z-up: center of min Z face
            if self._coordinate_system == 'z_up':
                min_x, min_y, min_z = x - half_x, y - half_y, z
            else:
                min_x, min_y, min_z = x - half_x, y, z - half_z
        elif anchor == CubeAnchor.TOP_CENTER:
            # In Y-up: center of max Y face; In Z-up: center of max Z face
            if self._coordinate_system == 'z_up':
                min_x, min_y, min_z = x - half_x, y - half_y, z - size_z
            else:
                min_x, min_y, min_z = x - half_x, y - size_y, z - half_z
        else:
            raise ValueError(f"Invalid anchor point: {anchor}")

        return min_x, min_y, min_z

    def add_voxel(self, x, y, z, anchor=CubeAnchor.CORNER_NEG, dimensions=None):
        """
        Adds a voxel to the model. Replaces add_cube.

        Args:
            x (float): X-coordinate of the voxel's anchor point.
            y (float): Y-coordinate of the voxel's anchor point (Y-up mode) or
                      depth coordinate (Z-up mode).
            z (float): Z-coordinate of the voxel's anchor point (Y-up mode) or
                      vertical coordinate (Z-up mode).
            anchor (CubeAnchor): The reference point within the voxel that
                                (x, y, z) corresponds to. Defaults to
                                CubeAnchor.CORNER_NEG.
            dimensions (tuple, optional): In Y-up mode: (width, height, depth).
                                          In Z-up mode: (width, depth, height).
                                          If None, the model's default dimensions are used.
        """
        # Swap coordinates and dimensions if in Z-up mode
        x, y, z = self._swap_yz_if_needed(x, y, z)

        voxel_dims = self.voxel_dimensions if dimensions is None else tuple(float(d) for d in dimensions)
        voxel_dims = self._swap_yz_dims_if_needed(voxel_dims)
        if dimensions is not None and not (isinstance(voxel_dims, (tuple, list)) and
                                           len(voxel_dims) == 3 and
                                           all(isinstance(d, (int, float)) and d > 0 for d in voxel_dims)):
            raise ValueError("Custom dimensions must be a tuple or list of three positive numbers.")

        min_x, min_y, min_z = self._calculate_min_corner(x, y, z, anchor, voxel_dims)

        # Calculate grid coordinates based on minimum corner and *default* dimensions
        # This ensures voxels snap to a consistent grid.
        raw_x = min_x / self.voxel_dimensions[0]
        raw_y = min_y / self.voxel_dimensions[1]
        raw_z = min_z / self.voxel_dimensions[2]
        grid_x = round(raw_x)
        grid_y = round(raw_y)
        grid_z = round(raw_z)
        # Warn if rounding actually occurred (i.e., not exactly on grid)
        if (grid_x != raw_x) or (grid_y != raw_y) or (grid_z != raw_z):
            logger.warning(
                f"Voxel at ({x}, {y}, {z}) with anchor {anchor} and dimensions {voxel_dims} "
                f"does not align exactly to grid; rounded from ({raw_x:.6f}, {raw_y:.6f}, {raw_z:.6f}) "
                f"to ({grid_x}, {grid_y}, {grid_z})"
            )

        grid_coord = (grid_x, grid_y, grid_z)
        self._voxels[grid_coord] = voxel_dims
        # logger.debug(f"Added voxel at grid {grid_coord} (from anchor {anchor} at ({x},{y},{z}))")

    # Alias add_cube to add_voxel for backward compatibility (optional, but can be helpful)
    add_cube = add_voxel

    def add_voxels(self, coordinates, anchor=CubeAnchor.CORNER_NEG, dimensions=None):
        """
        Adds multiple voxels from an iterable. Replaces add_cubes.

        Args:
            coordinates (iterable): An iterable of (x, y, z) tuples or lists.
            anchor (CubeAnchor): The anchor point to use for all voxels added
                                in this call.
            dimensions (tuple, optional): The dimensions to apply to all voxels
                                          in this call. If None, defaults are used.
        """
        for x_coord, y_coord, z_coord in coordinates:
            self.add_voxel(x_coord, y_coord, z_coord, anchor, dimensions)

    # Alias add_cubes to add_voxels
    add_cubes = add_voxels

    def remove_voxel(self, x, y, z, anchor=CubeAnchor.CORNER_NEG):
        """
        Removes a voxel from the model based on its anchor coordinates. Replaces remove_cube.

        Args:
            x (float): X-coordinate of the voxel's anchor point.
            y (float): Y-coordinate of the voxel's anchor point (Y-up mode) or
                      depth coordinate (Z-up mode).
            z (float): Z-coordinate of the voxel's anchor point (Y-up mode) or
                      vertical coordinate (Z-up mode).
            anchor (CubeAnchor): The reference point within the voxel that
                                (x, y, z) corresponds to.
        """
        # Swap coordinates if in Z-up mode
        x, y, z = self._swap_yz_if_needed(x, y, z)

        # Note: Removal does not need custom dimensions, as it identifies the
        # voxel by its position on the grid, which is calculated using default dimensions.
        min_x, min_y, min_z = self._calculate_min_corner(x, y, z, anchor, self.voxel_dimensions)

        raw_x = min_x / self.voxel_dimensions[0]
        raw_y = min_y / self.voxel_dimensions[1]
        raw_z = min_z / self.voxel_dimensions[2]
        grid_x = round(raw_x)
        grid_y = round(raw_y)
        grid_z = round(raw_z)
        if (grid_x != raw_x) or (grid_y != raw_y) or (grid_z != raw_z):
            logger.warning(
                f"Voxel removal at ({x}, {y}, {z}) with anchor {anchor} "
                f"does not align exactly to grid; rounded from "
                f"({raw_x:.6f}, {raw_y:.6f}, {raw_z:.6f}) to "
                f"({grid_x}, {grid_y}, {grid_z})"
            )

        grid_coord = (grid_x, grid_y, grid_z)
        if grid_coord in self._voxels:
            del self._voxels[grid_coord]
        # logger.debug(f"Attempted removal at grid {grid_coord}")

    # Alias remove_cube to remove_voxel
    remove_cube = remove_voxel

    def clear(self):
        """Removes all voxels from the model."""
        self._voxels.clear()
        logger.info("VoxelModel cleared.")

    def _greedy_mesh(self):
        """
        Generates an optimized mesh using greedy meshing algorithm.
        Merges adjacent coplanar faces into larger rectangles to reduce triangle count.

        Returns:
            list: A list of tuples, where each tuple is a triangle defined as
                (normal, vertex1, vertex2, vertex3).
        """
        if not self._voxels:
            return []

        logger.info(f"Generating optimized mesh using greedy meshing for {len(self._voxels)} voxels...")
        triangles = []

        # For each axis direction, collect exposed faces and merge them
        # Axes: 0=X, 1=Y, 2=Z; Directions: 0=negative, 1=positive
        for axis in range(3):  # X, Y, Z
            for direction in [0, 1]:  # negative, positive
                # Get all exposed faces for this direction
                faces = self._collect_faces_for_direction(axis, direction)

                # Group faces by their position along the normal axis (slices)
                slices = {}
                for face in faces:
                    slice_pos = face['pos_on_axis']
                    if slice_pos not in slices:
                        slices[slice_pos] = []
                    slices[slice_pos].append(face)

                # Apply greedy meshing to each slice
                for slice_pos, slice_faces in slices.items():
                    merged = self._greedy_merge_slice(slice_faces, axis)
                    triangles.extend(merged)

        logger.info(f"Greedy mesh generation complete. Optimized to {len(triangles)} triangles.")
        return triangles

    def _collect_faces_for_direction(self, axis, direction):
        """
        Collects all exposed faces for a given axis direction.

        Args:
            axis (int): 0=X, 1=Y, 2=Z
            direction (int): 0=negative face, 1=positive face

        Returns:
            list: List of face dictionaries with position and size information
        """
        faces = []
        offset = [0, 0, 0]
        offset[axis] = -1 if direction == 0 else 1

        for (gx, gy, gz), (size_x, size_y, size_z) in self._voxels.items():
            neighbor_coord = (gx + offset[0], gy + offset[1], gz + offset[2])
            neighbor_dims = self._voxels.get(neighbor_coord)

            # Face is exposed if no neighbor or neighbor has different dimensions
            if not neighbor_dims or neighbor_dims != (size_x, size_y, size_z):
                # Calculate face position in world coordinates
                min_cx = gx * self.voxel_dimensions[0]
                min_cy = gy * self.voxel_dimensions[1]
                min_cz = gz * self.voxel_dimensions[2]

                # Position along the normal axis
                pos_on_axis = [min_cx, min_cy, min_cz][axis]
                if direction == 1:  # Positive face
                    pos_on_axis += [size_x, size_y, size_z][axis]

                # The two axes perpendicular to the normal
                u_axis = (axis + 1) % 3
                v_axis = (axis + 2) % 3

                u_pos = [min_cx, min_cy, min_cz][u_axis]
                v_pos = [min_cx, min_cy, min_cz][v_axis]
                u_size = [size_x, size_y, size_z][u_axis]
                v_size = [size_x, size_y, size_z][v_axis]

                faces.append({
                    'axis': axis,
                    'direction': direction,
                    'pos_on_axis': pos_on_axis,
                    'u_pos': u_pos,
                    'v_pos': v_pos,
                    'u_size': u_size,
                    'v_size': v_size,
                    'grid_coord': (gx, gy, gz),
                    'dimensions': (size_x, size_y, size_z)
                })

        return faces

    def _greedy_merge_slice(self, faces, axis):
        """
        Merges coplanar faces in a slice using greedy meshing algorithm.

        Args:
            faces (list): List of face dictionaries in the same slice
            axis (int): The normal axis (0=X, 1=Y, 2=Z)

        Returns:
            list: List of triangles for the merged faces
        """
        if not faces:
            return []

        triangles = []
        direction = faces[0]['direction']
        pos_on_axis = faces[0]['pos_on_axis']

        # Build a grid of faces by their u,v positions and sizes
        # For uniform voxels, we can use a simpler greedy algorithm
        face_grid = {}
        for face in faces:
            # Use grid coordinates for lookup (only works for uniform voxels)
            u_idx = int(round(face['u_pos'] / self.voxel_dimensions[(axis + 1) % 3]))
            v_idx = int(round(face['v_pos'] / self.voxel_dimensions[(axis + 2) % 3]))
            u_size = face['u_size']
            v_size = face['v_size']

            key = (u_idx, v_idx, u_size, v_size)
            face_grid[key] = face

        # Greedy meshing: merge adjacent faces with same dimensions
        used = set()
        sorted_faces = sorted(face_grid.items(), key=lambda x: (x[0][1], x[0][0]))  # Sort by v, then u

        for (u_idx, v_idx, u_size, v_size), face in sorted_faces:
            if (u_idx, v_idx) in used:
                continue

            # Try to extend in u direction
            u_end = u_idx
            while (u_end + 1, v_idx, u_size, v_size) in face_grid and (u_end + 1, v_idx) not in used:
                u_end += 1

            # Try to extend in v direction
            v_end = v_idx
            can_extend = True
            while can_extend:
                # Check if entire row exists for v_end + 1
                for u in range(u_idx, u_end + 1):
                    if (u, v_end + 1, u_size, v_size) not in face_grid or (u, v_end + 1) in used:
                        can_extend = False
                        break
                if can_extend:
                    v_end += 1

            # Mark all merged faces as used
            for v in range(v_idx, v_end + 1):
                for u in range(u_idx, u_end + 1):
                    used.add((u, v))

            # Create merged rectangle
            u_axis_idx = (axis + 1) % 3
            v_axis_idx = (axis + 2) % 3

            u_start = u_idx * self.voxel_dimensions[u_axis_idx]
            v_start = v_idx * self.voxel_dimensions[v_axis_idx]
            u_length = (u_end - u_idx + 1) * u_size
            v_length = (v_end - v_idx + 1) * v_size

            # Build vertices for the merged rectangle
            verts = self._build_rect_vertices(axis, direction, pos_on_axis,
                                              u_start, v_start, u_length, v_length)

            # Create normal
            normal = [0, 0, 0]
            normal[axis] = 1 if direction == 1 else -1
            normal = tuple(normal)

            # Swap Y/Z for Z-up mode
            if self._coordinate_system == 'z_up':
                verts = [(v[0], v[2], v[1]) for v in verts]
                normal = (normal[0], normal[2], normal[1])

            # Create triangles with proper winding
            if self._coordinate_system == 'z_up':
                triangles.append((normal, verts[0], verts[2], verts[1]))
                triangles.append((normal, verts[0], verts[3], verts[2]))
            else:
                triangles.append((normal, verts[0], verts[1], verts[2]))
                triangles.append((normal, verts[0], verts[2], verts[3]))

        return triangles

    def _build_rect_vertices(self, axis, direction, pos_on_axis, u_start, v_start, u_length, v_length):
        """
        Builds the 4 vertices of a rectangle for a given axis direction.

        Returns:
            list: List of 4 vertex tuples in counter-clockwise order
        """
        u_axis = (axis + 1) % 3
        v_axis = (axis + 2) % 3

        # Build 4 corners
        verts = []
        for v_offset in [0, v_length]:
            for u_offset in [0, u_length]:
                vert = [0, 0, 0]
                vert[axis] = pos_on_axis
                vert[u_axis] = u_start + u_offset
                vert[v_axis] = v_start + v_offset
                verts.append(tuple(vert))

        # Reorder for CCW winding based on axis and direction
        # Order: bottom-left, bottom-right, top-right, top-left
        if axis == 0:  # X axis (YZ plane)
            if direction == 0:  # -X face
                verts = [verts[0], verts[2], verts[3], verts[1]]
            else:  # +X face
                verts = [verts[0], verts[1], verts[3], verts[2]]
        elif axis == 1:  # Y axis (XZ plane)
            if direction == 0:  # -Y face (looking up from below)
                verts = [verts[0], verts[2], verts[3], verts[1]]
            else:  # +Y face (looking down from above)
                verts = [verts[0], verts[1], verts[3], verts[2]]
        else:  # Z axis (XY plane)
            if direction == 0:  # -Z face
                verts = [verts[0], verts[2], verts[3], verts[1]]
            else:  # +Z face
                verts = [verts[0], verts[1], verts[3], verts[2]]

        return verts

    def generate_mesh(self, optimize=True):
        """
        Generates a list of triangles representing the exposed faces of the voxels.

        Ensures consistent counter-clockwise winding order (right-hand rule)
        for outward-facing normals.

        Args:
            optimize (bool): If True, uses greedy meshing algorithm to merge adjacent
                           coplanar faces, significantly reducing triangle count.
                           Default: True (recommended for most use cases).

        Returns:
            list: A list of tuples, where each tuple is a triangle defined as
                (normal, vertex1, vertex2, vertex3). Coordinates are in
                the model's world space. Returns an empty list if no voxels
                have been added.
        """
        if not self._voxels:
            return []

        # Use greedy meshing if optimize=True
        if optimize:
            return self._greedy_mesh()

        logger.info(f"Generating mesh for {len(self._voxels)} voxels...")
        triangles = []
        # Voxel dimensions are now fetched per-voxel, so size_x, etc. are defined inside the loop.

        # Define faces by normal, neighbor offset, and vertex indices (0-7)
        # Vertex indices correspond to relative positions scaled by dimensions:
        # 0: (0,0,0), 1: (Wx,0,0), 2: (0,Hy,0), 3: (Wx,Hy,0)
        # 4: (0,0,Dz), 5: (Wx,0,Dz), 6: (0,Hy,Dz), 7: (Wx,Hy,Dz)
        # Indices are ordered CCW when looking from outside the voxel.
        faces_data = [
            # Normal, Neighbor Offset, Vertex Indices (Tri1: v0,v1,v2; Tri2: v0,v2,v3)
            ((1, 0, 0), (1, 0, 0), [1, 3, 7, 5]), # +X face
            ((-1, 0, 0), (-1, 0, 0), [4, 6, 2, 0]), # -X face
            ((0, 1, 0), (0, 1, 0), [2, 6, 7, 3]), # +Y face
            ((0, -1, 0), (0, -1, 0), [0, 1, 5, 4]), # -Y face
            ((0, 0, 1), (0, 0, 1), [4, 5, 7, 6]), # +Z face
            ((0, 0, -1), (0, 0, -1), [3, 1, 0, 2]), # -Z face
        ]

        processed_faces = 0
        for (gx, gy, gz), (size_x, size_y, size_z) in self._voxels.items():
            # Calculate the minimum corner based on grid coordinates and *default* dimensions
            min_cx = gx * self.voxel_dimensions[0]
            min_cy = gy * self.voxel_dimensions[1]
            min_cz = gz * self.voxel_dimensions[2]

            # Calculate the 8 absolute vertex coordinates for this voxel using its specific dimensions
            verts = [
                (min_cx + (i % 2) * size_x, min_cy + ((i // 2) % 2) * size_y, min_cz + (i // 4) * size_z)
                for i in range(8)
            ]

            # If in Z-up mode, swap Y and Z in vertices for output
            if self._coordinate_system == 'z_up':
                verts = [(v[0], v[2], v[1]) for v in verts]

            for normal, offset, indices in faces_data:
                neighbor_coord = (gx + offset[0], gy + offset[1], gz + offset[2])
                neighbor_dims = self._voxels.get(neighbor_coord)

                # A face is exposed if there is no neighbor, OR if the neighbor
                # has different dimensions, which would create a complex partial
                # surface. For simplicity and correctness of the outer shell,
                # we will generate the face in the latter case.
                if not neighbor_dims or neighbor_dims != (size_x, size_y, size_z): # Exposed face
                    processed_faces += 1
                    # Get the four vertices for this face using the indices
                    v0 = verts[indices[0]]
                    v1 = verts[indices[1]]
                    v2 = verts[indices[2]]
                    v3 = verts[indices[3]]
                    # Swap normal Y and Z if in Z-up mode
                    output_normal = (normal[0], normal[2], normal[1]) if self._coordinate_system == 'z_up' else normal

                    # In Z-up mode, swapping Y and Z creates a reflection which reverses
                    # handedness, so we must reverse the winding order to keep normals outward
                    if self._coordinate_system == 'z_up':
                        triangles.append((output_normal, v0, v2, v1)) # Triangle 1 (reversed)
                        triangles.append((output_normal, v0, v3, v2)) # Triangle 2 (reversed)
                    else:
                        triangles.append((output_normal, v0, v1, v2)) # Triangle 1
                        triangles.append((output_normal, v0, v2, v3)) # Triangle 2

        logger.info(f"Mesh generation complete. Found {processed_faces} exposed faces, resulting in {len(triangles)} triangles.")
        return triangles

    def save_mesh(self, filename, format='stl_binary', optimize=True, **kwargs):
        """
        Generates the mesh and saves it to a file using the specified format.

        Args:
            filename (str): The path to the output file.
            format (str): The desired output format identifier (e.g/,
                        'stl_binary', 'stl_ascii'). Case-insensitive.
                        Defaults to 'stl_binary'.
            optimize (bool): If True, uses greedy meshing to reduce triangle count
                           by merging adjacent coplanar faces. Can reduce file size
                           by 10-100x for regular voxel structures. Default: True.
            **kwargs: Additional arguments passed directly to the specific
                    file writer (e.g., 'solid_name' for STL formats).
        """
        triangles = self.generate_mesh(optimize=optimize)
        if not triangles:
            logger.warning("No voxels in the model. Mesh file will not be generated.")
            return

        try:
            writer = get_writer(format)
            writer.write(triangles, filename, **kwargs)
            # No need for logger.info here, the writer handles its own success message
        except ValueError as e:
            logger.error(f"Failed to save mesh: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred during mesh saving to '{filename}': {e}")
            raise
