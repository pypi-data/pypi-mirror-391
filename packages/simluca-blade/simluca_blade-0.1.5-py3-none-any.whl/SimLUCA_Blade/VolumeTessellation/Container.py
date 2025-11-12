# The simulation is performed in 2D, representing a radial slice of a rotationally symmetric container.
# We use cylindrical coordinates (x, r, φ); φ is not used because of rotational symmetry.
# Length is measured in nm and time is measured in seconds.
# !!!!!!   Both volume and surface area should * 2 pi to get the real values.   !!!!!!

import numpy as np
from shapely.geometry import Polygon
import time

class Container:
    """
    Container mesh generator.
    - Reads a 1D shape profile (maximum radius r for each integer x position).
    - Builds border and interior nodes, relaxes interior nodes via Voronoi iterations,
      and constructs a triangulated mesh with neighbor and border adjacency.
    """

    # init a container with shape parameters stored in a file
    # shape_file: a file containing the shape parameters of the container, one parameter per line, representing the maximum r along the x axis. starting from x=0, x+=1 nm per line.
    # here, the resolution should not be less than 1 nm, which is the base unit of length
    def __init__(self, shape_file: str, resolution: float = 10):
        """
        Initialize a container from a shape profile.

        Args:
            shape_file: Path to a text file containing shape parameters; each line is the
                        maximum radius r at integer x starting from x=0 (step 1 nm per line).
            resolution: Target spatial resolution (nm). Should be >= 1 nm.
        """

        self.resolution = resolution

        # Read shape parameters from a file using numpy
        self.shape = np.loadtxt(shape_file, dtype=float)

    def establish(self, Voronoi_iterations: int = 100, animation_dir: str = None):
        """
        Build the full mesh:
        1) Create border nodes, 2) seed interior nodes, 3) relax interior nodes with Voronoi Lloyd iterations,
        4) triangulate and compute neighbor/border adjacencies.

        Args:
            Voronoi_iterations: Number of relaxation iterations.
            animation_dir: If provided, saves a relaxation animation (mp4) to this directory.
        """
        print("Initializing mesh")
        # Initialize the container by generating border nodes and inner nodes
        self.init_border_nodes()
        self.init_inner_nodes()

        # Relax inner nodes to make them evenly distributed
        self.relax_inner_nodes(Voronoi_iterations=Voronoi_iterations, animation_dir=animation_dir)

        # Triangulate the container
        self.triangulate()
        print("Mesh initialization complete\n", flush=True)

    class TriMesh:
        """
        Lightweight container for triangulation and adjacency data.
        Provides utilities to compute centroids, areas, volumes, and neighbor masks.
        """
        def __init__(self, vertices, simplices, tri_neighbors, borders, bor_neighbors, adjacent_tri, adjacent_bor):
            # Coordinates of all triangulation vertices
            self.vertices = vertices
            # Indices (into vertices) of the three vertices of each triangle
            self.simplices = simplices
            # Indices of neighboring triangles for each triangle (size 3, -1 if no neighbor)
            self.tri_neighbors = tri_neighbors
            # Indices (into vertices) of the endpoints of each border edge
            self.borders = borders
            # Neighboring border edges for each border edge (size 2, -1 if no neighbor)
            self.bor_neighbors = bor_neighbors
            # For each border edge, the index of the adjacent triangle (-1 if none)
            self.adjacent_tri = adjacent_tri
            # For each triangle, the index of the adjacent border edge (-1 if none)
            self.adjacent_bor = adjacent_bor
            # Centroids of triangles and border edges (computed on demand)
            self.tri_centroids = None
            self.bor_centroids = None

        @property
        def total_volume(self):
            """
            Compute the total volume of the container by summing triangle volumes.
            Returns:
                float: Total volume.
            """
            tri_volumes = self.calculate_tri_volumes()
            return np.sum(tri_volumes) * 2 * np.pi  # account for revolution around the axis
        
        @property
        def total_area(self):
            """
            Compute the total surface area of the container by summing border areas.
            Returns:
                float: Total surface area.
            """
            bor_areas = self.calculate_bor_areas()
            return np.sum(bor_areas) * 2 * np.pi  # account for revolution around the axis

        def calculate_centroids(self):
            """
            Compute centroids for all triangles and border edges.
            """
            self.tri_centroids = np.array([
                np.mean(self.vertices[simplex], axis=0) for simplex in self.simplices
            ])
            self.bor_centroids = np.array([
                np.mean(self.vertices[edge], axis=0) for edge in self.borders
            ])
            
        def calculate_tri_areas(self):
            """
            Compute the scalar area of each triangle (2D).
            Returns:
                np.ndarray of shape (n_tri,)
            """
            areas = []
            for simplex in self.simplices:
                v0, v1, v2 = self.vertices[simplex]
                area = 0.5 * np.abs((v1[0] - v0[0]) * (v2[1] - v0[1]) - (v2[0] - v0[0]) * (v1[1] - v0[1]))
                areas.append(area)
            return np.array(areas)
        
        def calculate_tri_volumes(self):
            """
            Compute the volume of each triangle when revolved (as a toroidal frustum).
            Equivalent to triangle area times the centroid's radial coordinate.
            Returns:
                np.ndarray of shape (n_tri,)
            """
            # the volume is equivalent to the area times the distance that the centroid travels
            return self.calculate_tri_areas() * self.tri_centroids[:, 1]

        def calculate_bor_areas(self):
            """
            Compute the length of each border edge (2D).
            Returns:
                np.ndarray of shape (n_bor,)
            """
            areas = []
            for edge in self.borders:
                v0, v1 = self.vertices[edge]
                length = np.sqrt((v1[0] - v0[0])**2 + (v1[1] - v0[1])**2)
                area = length * (v0[1]+v1[1]) / 2  # surface area when revolved
                areas.append(area)
            return np.array(areas)

        def calculate_valid_neighbors_mask(self):
            """
            Build boolean masks indicating which neighbor indices are valid (not -1)
            for both triangles and border edges.
            """
            # A valid neighbor is one that is not -1 (indicating no neighbor)
            self.tri_neighbors_mask = np.array([[neighbor != -1 for neighbor in neighbors] for neighbors in self.tri_neighbors])
            self.bor_neighbors_mask = np.array([[neighbor != -1 for neighbor in neighbors] for neighbors in self.bor_neighbors])

    # generate critical nodes on the border of the container
    def init_border_nodes(self):
        """
        Generate critical nodes along the container border (roof and axis).
        Populates:
            - self.border_nodes: ordered loop around the shape boundary including r=0 axis points.
            - self.roof_nodes: nodes along the outer (roof) boundary.
        """
        print("\t--Initializing border nodes", flush=True)
        border_length = [self.shape[0]]
        for i in range(len(self.shape) - 1):
            border_length.append(np.sqrt((self.shape[i + 1] - self.shape[i]) **2 + 1))
        border_length.append(self.shape[-1])

        num_border_nodes = int(np.ceil(sum(border_length) / self.resolution))
        border_edge_length = sum(border_length) / num_border_nodes

        self.border_nodes = [[0, 0]]
        self.roof_nodes = []
        current_length = 0
        for i in range(len(border_length)):
            current_length += border_length[i]
            delta_length = current_length - (len(self.border_nodes)-1) * border_edge_length
            while delta_length >= border_edge_length:
                delta_length -= border_edge_length
                if i == 0:
                    x = 0
                    r = self.shape[0] - delta_length
                    self.border_nodes.append([x, r])
                elif i == len(border_length) - 1:
                    x = len(self.shape) - 1
                    r = delta_length
                    self.border_nodes.append([x, r])
                else:
                    x = i - delta_length / border_length[i]
                    r = self.shape[i] - delta_length / border_length[i] * (self.shape[i] - self.shape[i-1])
                    self.border_nodes.append([x, r])
                    self.roof_nodes.append([x, r])

        # handle the error of floating point precision
        # Handle floating-point precision near the end cap
        if (len(self.shape)-1 - self.border_nodes[-1][0])**2 + self.border_nodes[-1][1]**2 < 1e-6:
            # if the last node is too close to the end of the container, make it exactly at the end
            self.border_nodes[-1] = [len(self.shape) - 1, 0]
        else:
            # if the last node is not at the end of the container, add a node at the end
            self.border_nodes.append([len(self.shape) - 1, 0])

        # "True" border nodes are those with indices in [1, self.border_number]; used to define border edges.
        self.border_number = len(self.border_nodes) - 2

        # add r=0 nodes list
        num_of_r0_nodes = int((np.ceil(len(self.shape)-1) / self.resolution))
        real_r0_resolution = (len(self.shape)-1) / num_of_r0_nodes
        for i in range(1, num_of_r0_nodes):
            x = i * real_r0_resolution
            r = 0
            self.border_nodes.append([x, r])
    
        self.border_nodes = np.array(self.border_nodes)
        self.shape_polygon = Polygon([(x, r) for x, r in self.border_nodes])

    # generate inner nodes of the container using halton sequence
    def init_inner_nodes(self):
        """
        Seed interior nodes column-wise beneath roof nodes to approximate uniform area coverage.
        """
        print("\t--Initializing inner nodes", flush=True)
        self.inner_nodes = []
        max_height = [node[1] for node in self.roof_nodes]
        num_inner_nodes = int(np.ceil((sum(self.shape)-(self.shape[0]+self.shape[-1])/2) / self.resolution**2))
        single_section_length = sum(max_height) / (num_inner_nodes + len(max_height))
        for node in self.roof_nodes:
            num_nodes_in_column = int(np.ceil(node[1] / single_section_length))
            section_length_in_column = node[1] / num_nodes_in_column
            for i in range(num_nodes_in_column-1):
                r = section_length_in_column * (i + 1)
                self.inner_nodes.append([node[0], r])
        self.inner_nodes = np.array(self.inner_nodes)

    # make inner nodes evenly distributed in the container
    def relax_inner_nodes(self, Voronoi_iterations: int = 100, animation_dir: str = None):
        """
        Relax interior nodes via Lloyd iterations on the Voronoi diagram clipped to the container polygon.

        Args:
            Voronoi_iterations: Number of relaxation iterations.
            animation_dir: Directory to save an mp4 of the relaxation; if None, no animation is saved.
        """
        print("\t--Relaxing inner nodes", end=' ', flush=True)
        # Relax inner nodes to make them evenly distributed
        from scipy.spatial import Voronoi, voronoi_plot_2d
        import copy

        max_x = max(self.border_nodes[:, 0]) + 10
        max_r = max(self.border_nodes[:, 1]) + 10
        min_x = -10
        min_r = -10
        far_away_nodes = []
        # Generate sufficiently distant points outside the container to bound Voronoi regions
        for angle in [0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi, 5*np.pi/4, 3*np.pi/2, 7*np.pi/4]:
            x = 10* max_x * np.cos(angle) + max(self.border_nodes[:, 0])/2
            r = 10* max_r * np.sin(angle) + max(self.border_nodes[:, 1])/2
            far_away_nodes.append([x, r])

        data_frames = []
        for i in range(Voronoi_iterations):
            # Create Voronoi diagram using both inner nodes and far away nodes
            vor = Voronoi(np.vstack((self.inner_nodes, far_away_nodes)))

            # clip Voronoi regions to the shape of the container
            vor_polygons = []
            for region in vor.regions:
                if not -1 in region and len(region) > 0:  # ignore empty regions
                    polygon = Polygon([vor.vertices[i] for i in region])
                    if polygon.intersects(self.shape_polygon):
                        vor_polygons.append(polygon.intersection(self.shape_polygon))
                    else:
                        print(f"Invalid polygon found in Voronoi region {region}, skipping it.")
                        print(f"Vertices: {[vor.vertices[i] for i in region]}")

            # update inner nodes to the centroids of the Voronoi regions
            self.inner_nodes = []
            for poly in vor_polygons:
                centroid = poly.centroid
                self.inner_nodes.append([centroid.x, centroid.y])
            self.inner_nodes = np.array(self.inner_nodes)

            # Gather frame for animation
            if animation_dir is not None:
                data_frames.append((copy.deepcopy(vor), copy.deepcopy(vor_polygons)))
            
            if i % (Voronoi_iterations // 10) == 0 or i == Voronoi_iterations - 1:
                print(".", end='', flush=True)

        if animation_dir is not None:
            print("\n\t\t--Saving animation", flush=True, end='')
            from matplotlib import animation
            import matplotlib.pyplot as plt
            fig = plt.figure()
            ax = fig.add_subplot(111)
            def update(frame_data):
                frame_num, (vor, vor_polygons) = frame_data
                ax.clear()
                for poly in vor_polygons:
                    x, y = poly.exterior.xy
                    ax.fill(x, y, alpha=0.5)
                voronoi_plot_2d(vor, ax=ax)
                ax.set_xlim(min_x, max_x)
                ax.set_ylim(min_r, max_r)
                ax.set_title(f"Voronoi Iteration {frame_num}")
                ax.set_xlabel('x (nm)')
                ax.set_ylabel('r (nm)')
                ax.set_aspect('equal', adjustable='box')
                return ax,

            ani = animation.FuncAnimation(fig, update, frames=enumerate(data_frames), repeat=False, cache_frame_data=False)
            ani.save(f"{animation_dir}/relaxation.mp4", fps=24, writer='ffmpeg')
            plt.close(fig)
        
        print("")

    # Triangulation
    def triangulate(self):
        """
        Perform Delaunay triangulation on border + interior nodes, discard triangles outside the polygon,
        and assemble neighbor/border adjacency structures.
        """
        print("\t--Triangulating the container", flush=True)
        from scipy.spatial import Delaunay
        points = np.vstack((self.border_nodes, self.inner_nodes))
        tri = Delaunay(points)
        # print("Delaunay triangulation complete, simplices found:", tri.neighbors, "\n", flush=True)
        
        # Discard triangles whose centroids lie outside the container polygon
        valid_simplices_index_mapping = np.full(len(tri.simplices)+1, -1, dtype=int)
        valid_simplices = []
        for i, simplex in enumerate(tri.simplices):
            if self.shape_polygon.contains(Polygon(tri.points[simplex]).centroid):
                valid_simplices_index_mapping[i] = len(valid_simplices)
                valid_simplices.append(simplex)
            else:
                valid_simplices_index_mapping[i] = -1
        valid_simplices_index_mapping[-1] = -1  # we need to have a -1 at the end to match that -1 indicates no neighbor

        tri.simplices = np.array(valid_simplices)
        # update neighbors to match the valid simplices
        valid_neighbors_raw = []
        for i, neighbors in enumerate(tri.neighbors):
            if valid_simplices_index_mapping[i] != -1:
                valid_neighbors_raw.append([valid_simplices_index_mapping[n] for n in neighbors])
        tri.neighbors = np.array(valid_neighbors_raw)

        # determine border edges using numpy
        border_edges = np.column_stack((np.arange(self.border_number + 1), np.arange(1, self.border_number + 2)))
        bor_neighbors = np.column_stack((np.arange(-1, self.border_number), np.arange(1, self.border_number + 2)))
        bor_neighbors[-1, 1] = -1  # last border edge has no neighbor

        # determine adjacent triangles for each border edge
        ## Build a mapping from each triangle edge to its triangle index
        edge_to_tri = {}
        for tri_idx, simplex in enumerate(tri.simplices):
            for i in range(3):
                edge = frozenset([simplex[i], simplex[(i+1)%3]])
                edge_to_tri[edge] = tri_idx

        ## determine adjacent triangles for each border edge efficiently
        adjacent_tri = np.full(len(border_edges), -1, dtype=int)
        for edge_idx, edge in enumerate(border_edges):
            edge_set = frozenset(edge)
            if edge_set in edge_to_tri:
                adjacent_tri[edge_idx] = edge_to_tri[edge_set]

        ## determine the adjacent border edges for each triangles
        adjacent_bor = np.full((len(tri.simplices)), -1, dtype=int)
        for bor_idx, tri_idx in enumerate(adjacent_tri):
            if tri_idx != -1:
                adjacent_bor[tri_idx] = bor_idx
        
        # Create the TriMesh object to store the triangulation data
        self.trimesh = self.TriMesh(
            vertices=np.array(tri.points),
            simplices=tri.simplices,
            tri_neighbors=tri.neighbors,
            borders= border_edges,
            bor_neighbors=bor_neighbors,
            adjacent_tri=adjacent_tri,
            adjacent_bor=adjacent_bor
        )

        # Sanity-check that triangulation vertices equal input points
        for i in range(len(self.trimesh.vertices)):
            if (self.trimesh.vertices[i] != points[i]).any():
                # raise error
                raise ValueError(f"Vertex {i} has been modified from {points[i]} to {self.trimesh.vertices[i]} during triangulation.")

if __name__ == "__main__":
    time_start = time.time()
    container = Container('shape.txt', resolution=100)
    container.establish(animation_dir=None)
    time_end = time.time()
    print("Container established in {:.2f} seconds".format(time_end - time_start))

    print("Number of border nodes:", len(container.border_nodes))
    print("Number of inner nodes:", len(container.inner_nodes))

    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 5))
    plt.plot(np.arange(len(container.shape)), np.array(container.shape), label='Container Shape', color='green', linewidth=3, alpha=0.7)
    plt.plot([node[0] for node in container.border_nodes]+[container.border_nodes[0][0]], [node[1] for node in container.border_nodes]+[container.border_nodes[0][1]], color='blue', markersize=5, label='border Nodes')
    plt.scatter([node[0] for node in container.border_nodes], [node[1] for node in container.border_nodes], marker='o', s=50)
    plt.scatter([node[0] for node in container.inner_nodes], [node[1] for node in container.inner_nodes], marker='x', color='red', label='Inner Nodes')

    # plot triangulation
    plt.triplot(container.trimesh.vertices[:, 0], container.trimesh.vertices[:, 1], container.trimesh.simplices.copy(), color='orange', alpha=0.5)
    # put simplices indexs on the center of each triangle on the plot
    for i, simplex in enumerate(container.trimesh.simplices):
        centroid = np.mean(container.trimesh.vertices[simplex], axis=0)
        plt.text(centroid[0], centroid[1], str(i), fontsize=8, ha='center', va='center', color='black')

    # plot border edges
    for edge in container.trimesh.borders:
        x = [container.trimesh.vertices[edge[0]][0], container.trimesh.vertices[edge[1]][0]]
        r = [container.trimesh.vertices[edge[0]][1], container.trimesh.vertices[edge[1]][1]]
        plt.plot(x, r, color='red', linewidth=2)
    
    # plot triangular meshes that have border neighbors using adjacent_tri
    print("adjacent_tri:", container.trimesh.adjacent_tri)
    for tri_idx in container.trimesh.adjacent_tri:
        if tri_idx != -1:
            simplex = container.trimesh.simplices[tri_idx]
            plt.fill(
                [container.trimesh.vertices[simplex[0]][0],
                 container.trimesh.vertices[simplex[1]][0],
                 container.trimesh.vertices[simplex[2]][0]],
                [container.trimesh.vertices[simplex[0]][1],
                 container.trimesh.vertices[simplex[1]][1],
                 container.trimesh.vertices[simplex[2]][1]],
                color='yellow', alpha=0.3
            )

    plt.title('Container Shape and border Nodes')
    plt.xlabel('x (nm)')
    plt.ylabel('r (nm)')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()