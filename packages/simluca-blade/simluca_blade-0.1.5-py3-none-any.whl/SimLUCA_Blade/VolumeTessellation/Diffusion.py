# Compute diffusion-related properties for each triangle (3D toroidal volume) and border edge (lateral surface).
# Due to rotational symmetry, each border edge corresponds to the lateral surface of a circular frustum/cylinder,
# and each triangle revolves around the axis to form a toroidal frustum. Diffusion factors follow from these geometries.

from .Container import Container
import numpy as np

# For each triangle, the neighbor index (0,1,2) corresponds to the opposite edge,
# given by the two local vertex indices below.
neighbor2edge = np.array([[1, 2], [0, 2], [0, 1]])

# Calculate the surface area of the lateral surface of a section of frustum given by two points
# (using the formular of the area of the lateral surface of a section of frustum,
# but not times \theta as the rotation degree will be cancelled out with volume)
def SurfaceArea(coord1: np.ndarray, coord2: np.ndarray):
    """
    Lateral surface contribution for a frustum section defined by two points (x, r).
    Uses s = (r1 + r2) * L / 2, where L is the edge length in (x, r)-space.
    Note: The rotational angle cancels with the volume term later.

    Args:
        coord1: First endpoint (x, r).
        coord2: Second endpoint (x, r).
    Returns:
        Scalar surface contribution (nm^2).
    """
    diff = coord2 - coord1
    L = np.linalg.norm(diff)
    s = (coord1[1] + coord2[1]) * L / 2
    return s

# Calculate the diffusion factor $Df$, which determines the diffusion flux $I$ as $I=-Df*\Delta C$
# So, here, we calculate the diffusion factor for each interacting mesh and border edge, meaning a factor for each neighbor.
# the diffusion factor of tri-mesh $Df$ = DiffConst * InteractingSurface Area / Volume / centroids distance
# the diffusion factor of border edge $Df$ = DiffConst * InteractingCurve Length / Surface / centroids distance
def DiffusionProperties(trimesh: Container.TriMesh):
    """
    Compute diffusion factors for triangle-triangle and border-border interactions, and
    the triangle-to-membrane transfer coefficient for border-adjacent triangles.

    Definitions:
      - Triangle diffusion factor Df_tri = D * A_interface / (V_triangle * d_centroids)
      - Border diffusion factor Df_bor = D * L_interface / (S_border * d_centroids)
      - Triangle-to-membrane coefficient k = A_border / V_triangle

    Args:
        trimesh: Container.TriMesh with centroids and adjacency available/derivable.
    Returns:
        (mesh_diffusion, border_diffusion, to_membrane)
        mesh_diffusion: (n_tri, 3) array of triangle diffusion factors (masked where no neighbor).
        border_diffusion: (n_bor, 2) array of border diffusion factors (masked where no neighbor).
        to_membrane: (n_bor,) array, coefficient for triangles adjacent to each border edge.
    """
    # Calculate the centroids of each triangle and border edge, which will then be used to calculate delta distances
    trimesh.calculate_centroids()
    # Calculate the mask for valid neighbors
    trimesh.calculate_valid_neighbors_mask()
    # Calculate the volumes of each triangular frustum
    tri_volumes = trimesh.calculate_tri_volumes()

    # Vectorized calculation of interface surface areas between neighboring triangles using numpy.vectorize and SurfaceArea
    tri_edge_vertex_indices = trimesh.simplices[:, neighbor2edge]  # shape (n_tri, 3, 2)
    # Get the coordinates for each edge's two vertices
    edge_coords_1 = trimesh.vertices[tri_edge_vertex_indices[:, :, 0]]  # shape (n_tri, 3, 2)
    edge_coords_2 = trimesh.vertices[tri_edge_vertex_indices[:, :, 1]]  # shape (n_tri, 3, 2)
    # Use numpy.vectorize to apply SurfaceArea to each edge
    surface_area_vec = np.vectorize(SurfaceArea, signature='(n),(n)->()')
    inter_surface_areas = surface_area_vec(edge_coords_1, edge_coords_2)  # shape (n_tri, 3)

    # Vectorized calculation of diffusion factors for each mesh
    ## the diffusion factor of tri-mesh $Df$ = DiffConst * InteractingSurface Area / Volume / centroids distance
    tri_centroids_dis = np.linalg.norm(trimesh.tri_centroids[:, np.newaxis, :] - trimesh.tri_centroids[trimesh.tri_neighbors], axis=-1) # shape (n_tri, n_neighbors(3)), unmasked
    mesh_diffusion = inter_surface_areas / np.where(trimesh.tri_neighbors_mask, tri_volumes[:, np.newaxis] * tri_centroids_dis, 1) * trimesh.tri_neighbors_mask

    # Vectorized calculation of the diffusion factors for each border edge
    ## the diffusion factor of border edge $Df$ = DiffConst * InteractingCurve Length / Surface / centroids distance
    bor_centroids_dis = np.linalg.norm(trimesh.bor_centroids[:, np.newaxis] - trimesh.bor_centroids[trimesh.bor_neighbors], axis=-1)    # shape (n_bor, n_bor_neighbors(2)), unmasked
    border_coords_1 = trimesh.vertices[trimesh.borders[:, 0]]  # shape (n_bor, 2)
    border_coords_2 = trimesh.vertices[trimesh.borders[:, 1]]  # shape (n_bor, 2)
    bor_areas = surface_area_vec(border_coords_1, border_coords_2)  # shape (n_bor,)
    border_diffusion = trimesh.vertices[trimesh.borders][:, :, 1] / bor_areas[:, np.newaxis] / np.where(trimesh.bor_neighbors_mask, bor_centroids_dis, 1) * trimesh.bor_neighbors_mask

    # Vectorize the to_membrane calculation
    # Calculate the concentration transfer coefficient for each mesh that is connected to the border
    # This coefficient is calculated as $k$ = Surface Area / Volume
    to_membrane = bor_areas / tri_volumes[trimesh.adjacent_tri]

    return mesh_diffusion, border_diffusion, to_membrane

if __name__ == "__main__":
    # Example usage
    container = Container('shape.txt', resolution=2000)
    container.establish(animation_dir=None)

    tri, bor, to_mem = DiffusionProperties(container.trimesh)

    print("simplices:", container.trimesh.simplices[-1], "\n")
    # print("borders:", container.trimesh.borders, "\n")
    print("neighbors:", container.trimesh.tri_neighbors[-1], "\n")
    # print("adjacent:", container.trimesh.adjacent_tri, "\n")

    print("Mesh Diffusion Properties:", tri[-1], "\n")
    # print("Border Diffusion Properties:", bor, "\n")
    # print("To Membrane Properties:", to_mem, "\n")