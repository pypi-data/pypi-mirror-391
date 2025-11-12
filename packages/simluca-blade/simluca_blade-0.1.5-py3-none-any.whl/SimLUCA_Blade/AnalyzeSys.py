from .ReactionSys import ReactionSys
from .ReactionLan import ChemSubs
import numpy as np

def Average_X (ReactionSys: ReactionSys, solution, species: ChemSubs) -> np.ndarray:
    """
    Calculate the average x position of a given species in the reaction system over time. (weighted by concentration and volume/area)
    Args:
        ReactionSys: The reaction system containing the species.
        solution: The solution object returned by the ODE solver, containing time points and concentrations.
        species: The species (CytSubs or MemSubs) for which to calculate the average x position.
    Returns:
        A list of average x positions at each time point in the solution.
    """
    name2kind_index = ReactionSys.NameToKindIndex
    s_kind, s_index = name2kind_index[str(species)]
    ave_x = []
    if s_kind == 0 :  # cytosolic
        tri_volumes = ReactionSys.container.trimesh.calculate_tri_volumes()
        c_off = ReactionSys.CytOffset[s_index]
        for i in range(len(solution.t)):
            sum_molecule = 0.0
            sum_x = 0.0
            for j in range(ReactionSys.N_Tri):
                conc = solution.y[c_off + j, i]
                vol = tri_volumes[j]
                sum_molecule += conc * vol
                sum_x += conc * vol * ReactionSys.container.trimesh.tri_centroids[j, 0]
            ave_x.append(sum_x / sum_molecule if sum_molecule > 0 else 0.0)

    elif s_kind == 1 :  # membrane
        bor_areas = ReactionSys.container.bor_mesh.calculate_bor_areas()
        m_off = ReactionSys.MemOffset[s_index]
        for i in range(len(solution.t)):
            sum_molecule = 0.0
            sum_x = 0.0
            for j in range(ReactionSys.N_Bor):
                conc = solution.y[m_off + j, i]
                area = bor_areas[j]
                sum_molecule += conc * area
                sum_x += conc * area * ReactionSys.container.bor_mesh.bor_centroids[j, 0]
            ave_x.append(sum_x / sum_molecule if sum_molecule > 0 else 0.0)
    
    else :
        raise ValueError(f"Species '{species}' is neither cytosolic nor membrane-bound.")

    return np.array(ave_x, dtype=np.float64)

def SpectralComplexity(x, y, p=2, s=1):
    """
    Compute Effective frequency C_p and Sobolev norm H^s for sampled function f(x).
    
    Parameters
    ----------
    x : np.ndarray
        1D array of sample locations (assumed uniform spacing).
    y : np.ndarray
        1D array of function values f(x).
    p : int or float, optional
        Order of effective frequency moment (default=2).
    s : int or float, optional
        Sobolev order (default=1).
    
    Returns
    -------
    C_p : float
        Effective frequency of order p.
    Hs_norm : float
        Sobolev H^s norm.
    """
    
    # --- step 1: FFT ---
    N = len(x)
    dx = x[1] - x[0]  # sampling interval
    Y = np.fft.fft(y)
    freqs = np.fft.fftfreq(N, d=dx) * 2*np.pi  # angular frequency ω
    
    # --- step 2: Power spectrum ---
    S = np.abs(Y)**2 / N  # normalize energy
    
    # --- step 3: Effective frequency ---
    C_p = np.sum((np.abs(freqs)**p) * S)
    
    # --- step 4: Sobolev norm ---
    Hs_norm = np.sqrt(np.sum((1 + np.abs(freqs)**2)**s * S) * (freqs[1]-freqs[0]))
    
    return C_p, Hs_norm

