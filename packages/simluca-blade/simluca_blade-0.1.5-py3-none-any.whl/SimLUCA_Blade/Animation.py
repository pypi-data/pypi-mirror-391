import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation
from matplotlib import animation
from matplotlib.collections import LineCollection
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as mcolors

from tqdm import tqdm

from .ReactionSys import ReactionSys

# ---- helpers ---------------------------------------------------------------

def _build_border_segments(vertices, borders):
    """
    Build list of 2-point segments for LineCollection from vertex array and border index pairs.
    """
    return [[vertices[i], vertices[j]] for i, j in borders]

def _make_lognorm(arr, eps=1e-12):
    """
    Create a LogNorm for an array, guarding against non-positive values.
    If no positive values exist, fall back to [eps, eps].
    """
    if arr.size == 0:
        return mcolors.LogNorm(vmin=eps, vmax=eps)
    pos = arr[arr > 0]
    if pos.size == 0:
        return mcolors.LogNorm(vmin=eps, vmax=max(float(arr.max()), eps))
    vmin = float(max(pos.min(), eps))
    vmax = float(max(arr.max(), vmin * (1 + 1e-9)))
    return mcolors.LogNorm(vmin=vmin, vmax=vmax)

# ---- main API --------------------------------------------------------------

def MakeAnimation(
    reaction_sys: ReactionSys,
    solution,
    tri_species=None,
    bor_species=None,
    mesh_label='',
    border_label='',
    mirror=False,
    save_dir=None,
    interval_ms: int = 40,
    fps: int = 25
):
    """
    Create an animation of concentrations over time:
    - Triangles (mesh) are colored by tri_species values.
    - Border edges are colored by bor_species values.
    - Optional mirrored display across r=0 for symmetric visualization.

    Args:
        reaction_sys: Prepared ReactionSys instance.
        solution: scipy.integrate solution with fields t and y.
        tri_species: cytosolic species name or object used on triangles.
        bor_species: membrane species name or object used on borders.
        mesh_label: colorbar label for mesh.
        border_label: colorbar label for border.
        mirror: if True, draw a mirrored copy across r=0.
        save_dir: output filepath for the video (e.g., 'out.mp4'); if None, do not save.
        interval_ms: animation frame interval in milliseconds.
        fps: output video frames-per-second when saving.

    Returns:
        matplotlib.animation.FuncAnimation
    """
    # --- geometry and data lookup
    container = reaction_sys.container
    verts = container.trimesh.vertices
    triang = Triangulation(verts[:, 0], verts[:, 1], container.trimesh.simplices)

    t = solution.t
    name2kind_n_index = reaction_sys.NameToKindIndex

    # Species -> indices (we only need indices; 'kind' is unused here)
    _, tri_index = name2kind_n_index[str(tri_species)]
    _, bor_index = name2kind_n_index[str(bor_species)]

    # Extract per-site time series
    y_mesh = solution.y[
        reaction_sys.CytOffset[tri_index] : reaction_sys.CytOffset[tri_index] + reaction_sys.N_Tri,
        :
    ]
    y_border = solution.y[
        reaction_sys.MemOffset[bor_index] : reaction_sys.MemOffset[bor_index] + reaction_sys.N_Bor,
        :
    ]

    # --- figure and artists
    fig, ax = plt.subplots(figsize=(10, 5))

    # Initial LogNorms
    mesh_norm = _make_lognorm(y_mesh[:, 0])
    border_norm = _make_lognorm(y_border[:, 0])

    # Mesh
    c_mesh = ax.tripcolor(triang, y_mesh[:, 0], shading='flat', cmap='viridis', norm=mesh_norm)

    # Border edges
    border_segments = _build_border_segments(verts, container.trimesh.borders)
    c_border = LineCollection(border_segments, array=y_border[:, 0], cmap='plasma', linewidths=3, norm=border_norm)
    border_coll = ax.add_collection(c_border)

    # Optional mirrored artists (mirror across r=0 by flipping y)
    c_mesh_mirror = None
    c_border_mirror = None
    if mirror:
        verts_m = verts.copy()
        verts_m[:, 1] = -verts_m[:, 1]
        triang_mirror = Triangulation(verts_m[:, 0], verts_m[:, 1], container.trimesh.simplices)

        c_mesh_mirror = ax.tripcolor(triang_mirror, y_mesh[:, 0], shading='flat', cmap='viridis', norm=mesh_norm)

        border_segments_m = _build_border_segments(verts_m, container.trimesh.borders)
        c_border_mirror = LineCollection(border_segments_m, array=y_border[:, 0], cmap='plasma', linewidths=3, norm=border_norm)
        ax.add_collection(c_border_mirror)

        # Symmetric y-limits for mirrored view
        rmax = float(max(abs(verts[:, 1].min()), abs(verts[:, 1].max())))
        ax.set_ylim(-rmax * 1.2, rmax * 1.2)

    # --- colorbars on both sides (keep same height as main plot)
    divider = make_axes_locatable(ax)
    cax_right = divider.append_axes("right", size="2%", pad=0.05)
    cax_left = divider.append_axes("left", size="2%", pad=1.2)

    cb_mesh = fig.colorbar(c_mesh, cax=cax_right, label=f'{mesh_label} (Mesh)')
    cb_border = fig.colorbar(c_border, cax=cax_left, label=f'{border_label} (Border)')
    cax_left.yaxis.set_label_position('left')
    cax_left.yaxis.tick_left()

    # --- axes styling
    ax.set_title(f"t = {t[0]:.2f} s")
    ax.set_xlabel('x (nm)')
    ax.set_ylabel('r (nm)')
    ax.set_aspect('equal', adjustable='box')

    # --- per-frame updater
    def update(frame):
        data_mesh = y_mesh[:, frame]
        data_bor = y_border[:, frame]

        # Recompute norms to keep log scaling meaningful over time
        mesh_norm = _make_lognorm(data_mesh)
        border_norm = _make_lognorm(data_bor)

        # Update arrays and norms
        c_mesh.set_array(data_mesh)
        c_mesh.set_norm(mesh_norm)
        cb_mesh.update_normal(c_mesh)

        c_border.set_array(data_bor)
        c_border.set_norm(border_norm)
        cb_border.update_normal(c_border)

        # Mirrored
        if mirror:
            c_mesh_mirror.set_array(data_mesh)
            c_mesh_mirror.set_norm(mesh_norm)
            c_border_mirror.set_array(data_bor)
            c_border_mirror.set_norm(border_norm)

        ax.set_title(f"t = {t[frame]:.2f}")
        return (c_mesh, c_border) if not mirror else (c_mesh, c_border, c_mesh_mirror, c_border_mirror)

    ani = animation.FuncAnimation(fig, update, frames=len(t), interval=interval_ms, blit=False)
    plt.tight_layout()

    # --- optional saving
    if save_dir is not None:
        print(f"Saving animation to {save_dir}...")
        progress_bar = tqdm(total=len(t), desc='Saving animation', unit='frame')
        update_func = lambda _i, _n: progress_bar.update(1)

        writer = animation.FFMpegWriter(fps=fps)

        ani.save(save_dir, writer=writer, dpi=100, progress_callback=update_func)
        progress_bar.close()
        print('Animation saved successfully.')

    return ani