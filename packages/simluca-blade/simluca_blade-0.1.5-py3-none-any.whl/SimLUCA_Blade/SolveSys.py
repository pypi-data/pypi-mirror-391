from tqdm import tqdm
from .ReactionSys import ReactionSys
from scipy.integrate import solve_ivp
import numpy as np

def SolveSystem(reaction_sys: ReactionSys, t_span, y0=None, rtol=1e-4, atol=1e-2, save_every=0.04, method='BDF', progress_bar=True):
    """
    Solve the reaction system ODEs over the specified time span.

    Parameters:
    - reaction_sys: ReactionSys object defining the system.
    - t_span: tuple (t_start, t_end) defining the time interval.
    - y0: initial concentrations array. (follows the species indexing in ReactionSys)
        The order of species in y0 should be:
        - [number of cytosolic mesh] * number of cytosolic species +
        - [number of membrane mesh] * number of membrane species
    - rtol: relative tolerance for the solver.
    - atol: absolute tolerance for the solver.
    - save_every: time interval to save results.
    - method: integration method (default 'BDF' for stiff systems).

    Returns:
    - t_eval: array of time points where solution is evaluated.
    - y_sol: array of solution concentrations at each time point.
    """

    if y0 is None:
        y0 = GetInitialConditions(reaction_sys)

    t_start, t_end = t_span
    t_eval = np.arange(t_start, t_end + save_every, save_every)
    pbar = tqdm(total=t_span[1], desc="Integrating reaction system", unit="s", bar_format="{l_bar}{bar}| {n:.2f}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]")

    reaction_sys.AddProgressBar(pbar, time_init=t_start)

    if not reaction_sys.is_prepared:
        raise RuntimeError("Reaction system must be prepared before solving.")

    sol = solve_ivp(reaction_sys.RHS, t_span=t_span, y0=y0, method=method,
                    jac=reaction_sys.Jacobian,
                    jac_sparsity=reaction_sys.JacobianSparsity,
                    t_eval=t_eval, rtol=rtol, atol=atol)
    pbar.close()
    if not sol.success:
        raise RuntimeError("ODE solver failed: " + sol.message)

    return sol

def GetInitialConditions(reaction_sys: ReactionSys):
    """
    Generate the initial conditions array for the reaction system based on species initial distributions.
    To generate y0 using this function, 
    ensure that each species in the reaction system has its initial distribution function set via ChemSubs.SetInitDistribution.
    """

    y0 = np.zeros(reaction_sys.N_Cyt * reaction_sys.N_Tri + reaction_sys.N_Mem * reaction_sys.N_Bor, dtype=np.float64)

    cyt_off = reaction_sys.CytOffset
    mem_off = reaction_sys.MemOffset

    # Set initial conditions for cytosolic species
    for species in reaction_sys.CytSpecies:
        for i in range(reaction_sys.N_Tri):
            if species.init_distribution is None:
                y0[cyt_off[species.index] + i] = 0
            else:
                if species.init_scope is not None:
                    # If an initial scope is defined, apply the init_distribution only within that scope
                    coords = reaction_sys.container.trimesh.tri_centroids[i]
                    if species.init_scope(coords[0], coords[1]):
                        y0[cyt_off[species.index] + i] = species.init_distribution()
                    else:
                        y0[cyt_off[species.index] + i] = 0
                else:
                    y0[cyt_off[species.index] + i] = species.init_distribution()
    
    # Set initial conditions for membrane species
    for species in reaction_sys.MemSpecies:
        for i in range(reaction_sys.N_Bor):
            if species.init_distribution is None:
                y0[mem_off[species.index] + i] = 0
            else:
                if species.init_scope is not None:
                    # If an initial scope is defined, apply the init_distribution only within that scope
                    coords = reaction_sys.container.trimesh.bor_centroids[i]
                    if species.init_scope(coords[0], coords[1]):
                        y0[mem_off[species.index] + i] = species.init_distribution()
                    else:
                        y0[mem_off[species.index] + i] = 0
                else:
                    y0[mem_off[species.index] + i] = species.init_distribution()

    return y0

