
from .ReactionLan import Reaction, ReactionRateExpression, CytSubs, MemSubs
from .VolumeTessellation import Container, DiffusionProperties

import numpy as np
from scipy.sparse import csr_matrix

from numba import njit, prange
from numba.typed import List
from numba import types

class ReactionSys:
    """
    Reaction system class for managing chemical reactions and species.
    Supports adding reactions, preparing the system for simulation, and computing RHS and Jacobian for ODE solvers.

    To use:
    1. Create an instance with a shape file and resolution.
    2. Add reactions using AddReaction().
    3. Call Establish() to prepare the system (build mesh, precompute diffusion, compile reaction plans).
    4. Use RHS() and Jacobian() methods during ODE solving.
    """

    def __init__(self, shape_file: str, resolution:int):
        """Initialize the reaction system with a container defined by the shape file and resolution."""
        self.reactions = []
        self.container = Container(shape_file, resolution=resolution)
        self.CytSpecies = []
        self.MemSpecies = []

        # prepare
        self._prepared = False

        # runtime data
        self._n_tri = None
        self._n_bor = None
        self._cyt_offset = None
        self._mem_offset = None
        self._n_vars = None
        self._mesh_diffusion = None
        self._border_diffusion = None
        self._to_membrane = None
        self._tri_neighbors = None
        self._tri_neighbors_mask = None
        self._bor_neighbors = None
        self._bor_neighbors_mask = None
        self._adjacent_tri = None
        self._name_to_kind_index = None
        self._plans_cyt = None
        self._plans_mem = None
        self._jac_indptr = None
        self._jac_indices = None
        self._jac_data = None
        self._jac_data_diffusion = None
        self._jacobian_csr = None
        self._jacobian_sparsity = None
        self._cyt_diff_coeff = None
        self._mem_diff_coeff = None

        # Integrating output settings
        self._progress_bar = None
        self._last_time = None

    def AddReaction(self, reaction: Reaction, rate_expression: ReactionRateExpression):
        """Add a reaction with its associated rate expression to the system."""
        self.reactions.append(reaction)
        self.reactions[-1].SetRate(rate_expression)
        for species in reaction.AllSpecies():
            if species not in self.CytSpecies and species not in self.MemSpecies:
                if isinstance(species, CytSubs):
                    self.CytSpecies.append(species)
                elif isinstance(species, MemSubs):
                    self.MemSpecies.append(species)
                else:
                    raise TypeError("Species must be either CytSubs or MemSubs.")
    
    def AddProgressBar(self, progress_bar, time_init = 0.0):
        """Set a progress bar for simulation output."""
        self._progress_bar = progress_bar
        self._last_time = time_init
    
    @property
    def CytOffset(self):
        """Return the cytosolic species offsets array."""
        return self._cyt_offset
    @property
    def MemOffset(self):
        """Return the membrane species offsets array."""
        return self._mem_offset
    @property
    def NameToKindIndex(self):
        """Return the name to (kind, index) mapping dictionary."""
        return self._name_to_kind_index
    @property
    def N_Cyt(self):
        """Return the number of cytosolic species."""
        return len(self.CytSpecies)
    @property
    def N_Mem(self):
        """Return the number of membrane species."""
        return len(self.MemSpecies)
    @property
    def N_Tri(self):
        """Return the number of triangles in the mesh."""
        return self._n_tri
    @property
    def N_Bor(self):
        """Return the number of borders in the mesh."""
        return self._n_bor

    def Establish(self, animation_dir: str = None):
        """
        Assign global indices, build mesh, precompute diffusion arrays and compile reaction plans.
        Call once before simulation.
        """

        # assign global species indices: cytosolic first, then membrane
        n_cyt = len(self.CytSpecies)
        for index, species in enumerate(self.CytSpecies):
            species.IndexChem(index)
        for index, species in enumerate(self.MemSpecies):
            species.IndexChem(index)

        # Build mesh and diffusion geometry
        self.container.establish(animation_dir=animation_dir)

        self._prepare()

    def _prepare(self):
        tm = self.container.trimesh
        self._n_tri = len(tm.simplices)
        self._n_bor = len(tm.borders)
        print(f"ReactionSys: Mesh has {self._n_tri} triangles and {self._n_bor} border edges.")
        
        # Species indexing, offsets and diffusion coefficients
        n_cyt = len(self.CytSpecies)
        n_mem = len(self.MemSpecies)
        self._cyt_offset = np.empty(n_cyt, dtype=np.int64)
        self._cyt_diff_coeff = np.empty(n_cyt, dtype=np.float64)
        for s in self.CytSpecies:
            self._cyt_offset[s.index] = s.index * self._n_tri
            self._cyt_diff_coeff[s.index] = s.diffusion_coeff
        cyt_size = n_cyt * self._n_tri

        self._mem_offset = np.empty(n_mem, dtype=np.int64)
        self._mem_diff_coeff = np.empty(n_mem, dtype=np.float64)
        for s in self.MemSpecies:
            self._mem_offset[s.index] = s.index * self._n_bor + cyt_size
            self._mem_diff_coeff[s.index] = s.diffusion_coeff
        self._n_vars = cyt_size + n_mem * self._n_bor

        # Geometry and diffusion constants
        mesh_diffusion, border_diffusion, to_membrane = DiffusionProperties(tm)
        self._mesh_diffusion = mesh_diffusion.astype(np.float64)            # (n_tri, 3)
        self._border_diffusion = border_diffusion.astype(np.float64)        # (n_bor, 2)
        self._to_membrane = to_membrane.astype(np.float64)                  # (n_bor,)

        self._tri_neighbors = tm.tri_neighbors.astype(np.int32)             # (n_tri, 3)
        self._tri_neighbors_mask = tm.tri_neighbors_mask.astype(np.uint8)   # (n_tri, 3)
        self._bor_neighbors = tm.bor_neighbors.astype(np.int32)             # (n_bor, 2)
        self._bor_neighbors_mask = tm.bor_neighbors_mask.astype(np.uint8)   # (n_bor, 2)
        self._adjacent_tri = tm.adjacent_tri.astype(np.int32)               # (n_bor,)

        # check if all membrane sites have adjacent cytosolic sites
        if np.any(self._adjacent_tri < 0):
            raise ValueError("Some membrane sites have no adjacent cytosolic sites.")
        print(f"ReactionSys: Total container volume is {self.container.trimesh.total_volume / 1e9} µm^3.")
        print(f"ReactionSys: Total container surface area is {self.container.trimesh.total_area / 1e6} µm^2.\n")

        # Name -> (kind, species_index)
        self._name_to_kind_index = {}
        for s in self.CytSpecies:
            self._name_to_kind_index[s.name] = (0, s.index)
        for s in self.MemSpecies:
            self._name_to_kind_index[s.name] = (1, s.index)
        
        print(f"ReactionSys: Preparing with {len(self.reactions)} reactions, {n_cyt} cytosolic species, {n_mem} membrane species.")
        # Precompile reaction rate plans for numba
        self._plans_cyt, self._plans_mem = self._compile_rate_plans_numba()

        print(f"ReactionSys: Calculating Jacobian sparsity structure and allocating buffers.")
        # Build CSR sparsity structure for Jacobian (diffusion + reactions)
        self._jac_indptr, self._jac_indices = self._build_jac_sparsity()

        # Allocate data buffers
        self._jac_data = np.zeros_like(self._jac_indices, dtype=np.float64)         # mutable values for full Jacobian
        self._jac_data_diffusion = np.zeros_like(self._jac_indices, dtype=np.float64)  # constant diffusion part

        # Fill the constant diffusion part of the Jacobian
        _fill_diffusion_jac_data(self._n_tri, self._n_bor,
                                 self._cyt_offset, self._mem_offset,
                                 self._cyt_diff_coeff, self._mesh_diffusion, self._tri_neighbors, self._tri_neighbors_mask,
                                 self._mem_diff_coeff, self._border_diffusion, self._bor_neighbors, self._bor_neighbors_mask,
                                 self._jac_indptr, self._jac_indices, self._jac_data_diffusion)
        
        # SciPy CSR view of Jacobian (share buffers)
        self._jacobian_csr = csr_matrix((self._jac_data, self._jac_indices, self._jac_indptr),
                                            shape=(self._n_vars, self._n_vars))
        self._jacobian_sparsity = csr_matrix((np.ones_like(self._jac_data, dtype=bool), self._jac_indices, self._jac_indptr),
                                            shape=(self._n_vars, self._n_vars))
        
        self._prepared = True

        # Warm up numba functions
        print("ReactionSys: Warming up numba JIT functions.")
        tmp_y0 = np.ones(n_cyt * self._n_tri + n_mem * self._n_bor, dtype=np.float64)
        _rhs_impl(tmp_y0, np.empty_like(tmp_y0),
                  self._n_tri, self._n_bor,
                  self._cyt_offset, self._mem_offset,
                  self._cyt_diff_coeff, self._mesh_diffusion, self._tri_neighbors, self._tri_neighbors_mask,
                  self._mem_diff_coeff, self._border_diffusion, self._bor_neighbors, self._bor_neighbors_mask,
                  self._adjacent_tri, self._to_membrane,
                  self._plans_cyt, self._plans_mem)
        self.Jacobian(0.0, tmp_y0)
        print("ReactionSys: Preparation complete.\n")

    def _compile_rate_plans_numba(self):
        """
        Compile reaction rate expressions into numba-friendly plans for runtime evaluation.
        Each plan is a tuple of arrays:
        (term_coeffs, mono_ptr, var_indexes, var_kinds,
         cyt_indexes, cyt_stoich,
         mem_indexes, mem_stoich)
        where:
        - term_coeffs: float64 array of coefficients for each monomial term
        - mono_ptr: int32 array of pointers (CSR style) into var_indexes/var_kinds for each monomial term
        - var_indexes: int32 array of species indices for variables in monomials
        - var_kinds: int8 array of species kinds (0=cyt, 1=mem) for variables in monomials
        - cyt_indexes: int32 array of cytosolic species indices for net stoichiometry
        - cyt_stoich: int32 array of net stoichiometric coefficients for cytosolic species
        - mem_indexes: int32 array of membrane species indices for net stoichiometry
        - mem_stoich: int32 array of net stoichiometric coefficients for membrane species
        """
        # define the numba element type for an individual plan (tuple of 8 1D arrays)
        plan_type = types.Tuple(  # or types.Tuple works too; UniTuple enforces fixed length
            (types.float64[:],  # term_coeffs
             types.int32[:],    # mono_ptr
             types.int32[:],    # var_indexes
             types.int8[:],     # var_kinds
             types.int32[:],    # cyt_indexes
             types.int32[:],    # cyt_stoich
             types.int32[:],    # mem_indexes
             types.int32[:])    # mem_stoich
        )

        plans_cyt = List.empty_list(plan_type)
        plans_mem = List.empty_list(plan_type)

        for rxn in self.reactions:
            rr = rxn.rate_expression
            if rr is None:
                raise ValueError("Reaction has no rate expression.")

            # Parse PolyTerms into numba-friendly arrays
            term_coeffs_py = []     # python side temp lists
            var_indexes_py = []
            var_kinds_py = []
            ptr_py = [0]
            for vars_set, coeff in rr.PolyTerms.items():
                term_coeffs_py.append(float(coeff))
                if vars_set == frozenset([1]):  # constant term has zero variables
                    ptr_py.append(ptr_py[-1])   # keep the same pointer, no vars in this term
                    continue
                term_vars = sorted(str(x) for x in vars_set)
                for var in term_vars:
                    kind, index = self._name_to_kind_index[var]
                    var_indexes_py.append(index)
                    var_kinds_py.append(kind)
                ptr_py.append(ptr_py[-1] + len(term_vars))

            term_coeffs = np.array(term_coeffs_py, dtype=np.float64)
            var_indexes = np.array(var_indexes_py, dtype=np.int32)
            var_kinds = np.array(var_kinds_py, dtype=np.int8)
            mono_ptr = np.array(ptr_py, dtype=np.int32)

            # Calculate Net Stoichiometry = Product - Reactant
            from collections import Counter
            products = Counter([s.name for s in rxn.products])
            reactants = Counter([s.name for s in rxn.reactants])
            net_stoich = {n: products.get(n, 0) - reactants.get(n, 0) for n in set(products) | set(reactants)}

            # Parse net stoichiometry into numba-friendly arrays
            cyt_indexes_py = []     # python side temp lists
            mem_indexes_py = []
            cyt_stoich_py = []
            mem_stoich_py = []

            for var, stoich in net_stoich.items():
                kind, index = self._name_to_kind_index[var]
                if kind == 0:
                    cyt_indexes_py.append(index)
                    cyt_stoich_py.append(int(stoich))
                else:
                    mem_indexes_py.append(index)
                    mem_stoich_py.append(int(stoich))

            cyt_indexes = np.array(cyt_indexes_py, dtype=np.int32)
            mem_indexes = np.array(mem_indexes_py, dtype=np.int32)
            cyt_stoich = np.array(cyt_stoich_py, dtype=np.int32)
            mem_stoich = np.array(mem_stoich_py, dtype=np.int32)

            # Assemble numba type plan tuple
            plan = (term_coeffs, mono_ptr, var_indexes, var_kinds,
                          cyt_indexes, cyt_stoich,
                          mem_indexes, mem_stoich)

            # Classify: membrane-involved if any membrane variable OR any membrane target/reactant in stoichiometry
            mem_involved = (var_kinds.size > 0 and np.any(var_kinds == 1)) or (mem_indexes.size > 0)
            if mem_involved:
                plans_mem.append(plan)
            else:
                plans_cyt.append(plan)
        
        return plans_cyt, plans_mem

    def _build_jac_sparsity(self):
        """
        Build fixed CSR sparsity structure (indptr, indices) for the Jacobian matrix, combining diffusion and reaction contributions:
        - Diffusion couplings: block-diagnonal-like per species (self and neighbors)
        - Reaction couplings: for each target species row, add columns for variables used by its rate at that site.
        """

        rows = [set() for _ in range(self._n_vars)]

        # Diffusion couplings: cytosolic species
        for base in self._cyt_offset:
            for i in range(self._n_tri):
                row = base + i
                rows[row].add(row)  # self
                for n_idx in range(3):
                    if self._tri_neighbors_mask[i, n_idx]:  # valid neighbor
                        neighbor = self._tri_neighbors[i, n_idx]
                        rows[row].add(base + neighbor)

        # Diffusion couplings: membrane species
        for base in self._mem_offset:
            for i in range(self._n_bor):
                row = base + i
                rows[row].add(row)  # self
                for n_idx in range(2):
                    if self._bor_neighbors_mask[i, n_idx]:  # valid neighbor
                        neighbor = self._bor_neighbors[i, n_idx]
                        rows[row].add(base + neighbor)
        
        # Reaction couplings: cytosolic reactions
        for (term_coeffs, mono_ptr, var_indexes, var_kinds,
             cyt_indexes, cyt_stoich,
             mem_indexes, mem_stoich) in self._plans_cyt:   # for each reaction
            for site in range(self._n_tri):                 # for each site
                cols = []
                # columns are cyt variables appearing in monomials at this site
                for t_idx in range(len(term_coeffs)):       # for each monomial term
                    for k in range(mono_ptr[t_idx], mono_ptr[t_idx+1]): # for each var in the monomial term
                        if var_kinds[k] == 0:  # cytosolic double check
                            cols.append(self._cyt_offset[var_indexes[k]] + site)
                        else:
                            raise ValueError("Membrane species found in cytosolic-only reaction plan.")
                
                # add to target species rows, every species affected by this reaction at this site
                for s in cyt_indexes:
                    row = self._cyt_offset[s] + site
                    rows[row].update(cols)
        
        # Reaction couplings: membrane reactions
        for (term_coeffs, mono_ptr, var_indexes, var_kinds,
             cyt_indexes, cyt_stoich,
             mem_indexes, mem_stoich) in self._plans_mem:   # for each reaction
            for site in range(self._n_bor):                 # for each site
                adj_tri = self._adjacent_tri[site]
                cols = []
                # columns are variables (cyt or mem) appearing in monomials at this site
                for t_idx in range(len(term_coeffs)):       # for each monomial term
                    for k in range(mono_ptr[t_idx], mono_ptr[t_idx+1]): # for each var in the monomial term
                        if var_kinds[k] == 0 and adj_tri != -1:       # cytosolic
                            cols.append(self._cyt_offset[var_indexes[k]] + adj_tri)
                        elif var_kinds[k] == 1:     # membrane
                            cols.append(self._mem_offset[var_indexes[k]] + site)
                        else:
                            raise ValueError("Unknown species kind in reaction plan.")
                
                # add to target species rows, every species affected by this reaction at this site
                for s in cyt_indexes:
                    if adj_tri == -1:
                        continue  # skip if no adjacent triangle
                    row = self._cyt_offset[s] + adj_tri
                    rows[row].update(cols)
                for s in mem_indexes:
                    row = self._mem_offset[s] + site
                    rows[row].update(cols)

        # Convert to CSR format (sorted within rows)
        indptr = np.zeros(self._n_vars + 1, dtype=np.int32)
        none_zeros = 0
        for i in range(self._n_vars):
            none_zeros += len(rows[i])
            indptr[i+1] = none_zeros
        
        indices = np.zeros(none_zeros, dtype=np.int32)
        pos = 0
        for i in range(self._n_vars):
            cols = np.array(list(rows[i]), dtype=np.int32)
            cols.sort()
            indices[pos:pos+len(cols)] = cols
            pos += len(cols)
        return indptr, indices

    # --------------- Runtime for solver -----------------

    def RHS(self, t, y):
        """Right-hand side f(t, y) for ODE solver: diffusion + reactions."""
        if not self._prepared:
            raise RuntimeError("ReactionSys not prepared. Call Establish() before simulation.")
        dy = np.empty_like(y, dtype=np.float64)
        _rhs_impl(y, dy,
                  self._n_tri, self._n_bor,
                  self._cyt_offset, self._mem_offset,
                  self._cyt_diff_coeff, self._mesh_diffusion, self._tri_neighbors, self._tri_neighbors_mask,
                  self._mem_diff_coeff, self._border_diffusion, self._bor_neighbors, self._bor_neighbors_mask,
                  self._adjacent_tri, self._to_membrane,
                  self._plans_cyt, self._plans_mem)
        
        if self._progress_bar is not None:
            if t > self._last_time + 0.04:
                self._progress_bar.update(t-self._last_time)
                self._last_time = t

        return dy
        
    def Jacobian(self, t, y):
        """Return csr_matrix view with up-to-date Jacobian values at (t, y)."""
        if not self._prepared:
            raise RuntimeError("ReactionSys not prepared. Call Establish() before simulation.")
        # Start from constant diffusion part
        self._jac_data[:] = self._jac_data_diffusion
        # Add reaction contributions
        _jac_react_fill(y,
                        self._n_tri, self._n_bor,
                        self._cyt_offset, self._mem_offset,
                        self._adjacent_tri, self._to_membrane,
                        self._plans_cyt, self._plans_mem,
                        self._jac_indptr, self._jac_indices, self._jac_data)
        return self._jacobian_csr
    
    @property
    def JacobianSparsity(self):
        """Boolean sparsity pattern for solver's jac_sparsity hint."""
        if not self._prepared:
            raise RuntimeError("ReactionSys not prepared. Call Establish() before simulation.")
        return self._jacobian_sparsity

    @property
    def is_prepared(self):
        """Return whether the system has been prepared (Establish called)."""
        return self._prepared

# --------------- Numba kernels -----------------

@njit(cache=True, fastmath=True, parallel=True)
def _rhs_impl(y, dy,
              n_tri, n_bor,
              cyt_off, mem_off,
              cyt_diff_coeff, mesh_diff, tri_nb, tri_mask,
              mem_diff_coeff, bor_diff, bor_nb, bor_mask,
              adj_tri, to_mem,
              plans_cyt, plans_mem):
    """
    Compute the right-hand side dy = f(t, y) including diffusion and reactions.
    y: input concentration vector
    dy: output rate of change vector
    n_tri: number of triangles (cytosolic sites)
    n_bor: number of borders (membrane sites)
    cyt_off: offsets for cytosolic species in y
    mem_off: offsets for membrane species in y
    cyt_diff_coeff: diffusion coefficients for cytosolic species (n_cyt,)
    mesh_diff: diffusion coefficients for cytosolic species (n_tri, 3)
    tri_nb: triangle neighbors (n_tri, 3)
    tri_mask: triangle neighbor validity mask (n_tri, 3)
    mem_diff_coeff: diffusion coefficients for membrane species (n_mem,)
    bor_diff: diffusion coefficients for membrane species (n_bor, 2)
    bor_nb: border neighbors (n_bor, 2)
    bor_mask: border neighbor validity mask (n_bor, 2)
    adj_tri: adjacent triangle index for each border (n_bor,)
    to_mem: scaling factors turns membrane concentrations into corresponding cytosolic concentrations (n_bor,)
    plans_cyt: compiled reaction rate plans for cytosolic reactions
    plans_mem: compiled reaction rate plans for membrane reactions
    """
    # Zero dy, the output
    for i in prange(dy.shape[0]):
        dy[i] = 0.0

    # Cytosolic diffusion (operate per species)
    for s_index in prange(len(cyt_off)):
        base = cyt_off[s_index]
        for i in range(n_tri):
            accum = 0.0
            for n_idx in range(3):
                if tri_mask[i, n_idx]:  # valid neighbor
                    neighbor = tri_nb[i, n_idx]
                    accum += mesh_diff[i, n_idx] * cyt_diff_coeff[s_index] * (y[base + neighbor] - y[base + i])
            dy[base + i] += accum
    
    # Membrane diffusion (operate per species)
    for s_index in prange(len(mem_off)):
        base = mem_off[s_index]
        for i in range(n_bor):
            accum = 0.0
            for n_idx in range(2):
                if bor_mask[i, n_idx]:  # valid neighbor
                    neighbor = bor_nb[i, n_idx]
                    accum += bor_diff[i, n_idx] * mem_diff_coeff[s_index] * (y[base + neighbor] - y[base + i])
            dy[base + i] += accum
    
    # Cytosolic reactions
    for p_index in range(len(plans_cyt)):
        term_coeffs, mono_ptr, var_indexes, var_kinds, cyt_indexes, cyt_stoich, mem_indexes, mem_stoich = plans_cyt[p_index]
        for site in prange(n_tri):
            # Evaluate rate at this site
            rate = 0.0
            for t_idx in range(len(term_coeffs)):
                term_val = term_coeffs[t_idx]
                for k in range(mono_ptr[t_idx], mono_ptr[t_idx+1]):
                    var_index = var_indexes[k]
                    term_val *= y[cyt_off[var_index] + site]
                rate += term_val
            
            # Update dy for each affected species
            for s_idx in range(len(cyt_indexes)):
                s = cyt_indexes[s_idx]
                stoich = cyt_stoich[s_idx]
                dy[cyt_off[s] + site] += stoich * rate
    
    # Membrane reactions
    for p_index in range(len(plans_mem)):
        term_coeffs, mono_ptr, var_indexes, var_kinds, cyt_indexes, cyt_stoich, mem_indexes, mem_stoich = plans_mem[p_index]
        for site in prange(n_bor):
            adj_triangle_idx = adj_tri[site]
            # Evaluate rate at this site
            rate = 0.0
            for t_idx in range(len(term_coeffs)):
                term_val = term_coeffs[t_idx]
                for k in range(mono_ptr[t_idx], mono_ptr[t_idx+1]):
                    var_index = var_indexes[k]
                    if var_kinds[k] == 0:  # cytosolic
                        term_val *= y[cyt_off[var_index] + adj_triangle_idx]
                    else:  # membrane
                        term_val *= y[mem_off[var_index] + site]
                rate += term_val
            
            # Update dy for each affected species
            # for cytosolic species, a scale factor to_mem is required
            scale_f = to_mem[site]
            for s_idx in range(len(cyt_indexes)):
                s = cyt_indexes[s_idx]
                stoich = cyt_stoich[s_idx]
                dy[cyt_off[s] + adj_triangle_idx] += stoich * rate * scale_f
            for s_idx in range(len(mem_indexes)):
                s = mem_indexes[s_idx]
                stoich = mem_stoich[s_idx]
                dy[mem_off[s] + site] += stoich * rate

@njit(cache=True, fastmath=True)
def _row_bisearch(indices, start, end, col):
    """Binary search for column 'col' in indices[start:end], return position or -1 if not found."""
    l = start; r = end
    while l < r:
        mid = (l + r) // 2
        if indices[mid] < col:
            l = mid + 1
        else:
            r = mid
    if l < end and indices[l] == col:
        return l
    return -1

@njit(cache=True, fastmath=True)
def _jac_data_accum(row, col, val, indptr, indices, data):
    """Accumulate 'val' into the Jacobian data at position (row, col) using binary search."""
    start = indptr[row]; end = indptr[row + 1]
    pos = _row_bisearch(indices, start, end, col)
    if pos != -1:
        data[pos] += val
    # raise error if position not found (should not happen in prebuilt sparsity)

@njit(cache=True, fastmath=True, parallel=True)
def _fill_diffusion_jac_data(n_tri, n_bor,
                             cyt_off, mem_off,
                             cyt_diff_coeff, mesh_diff, tri_nb, tri_mask,
                             mem_diff_coeff, bor_diff, bor_nb, bor_mask,
                             indptr, indices, data):
    """
    Fill in the diffusion contributions to the Jacobian data array.
    n_tri: number of triangles (cytosolic sites)
    n_bor: number of borders (membrane sites)
    cyt_off: offsets for cytosolic species in y
    mem_off: offsets for membrane species in y
    cyt_diff_coeff: diffusion coefficients for cytosolic species (n_cyt,)
    mesh_diff: diffusion coefficients for cytosolic species (n_tri, 3)
    tri_nb: triangle neighbors (n_tri, 3)
    tri_mask: triangle neighbor validity mask (n_tri, 3)
    mem_diff_coeff: diffusion coefficients for membrane species (n_mem,)
    bor_diff: diffusion coefficients for membrane species (n_bor, 2)
    bor_nb: border neighbors (n_bor, 2)
    bor_mask: border neighbor validity mask (n_bor, 2)
    indptr, indices, data: CSR structure and data array to fill
    """
    # Zero data
    for i in prange(data.shape[0]):
        data[i] = 0.0

    # Cytosolic diffusion
    for s_index in prange(len(cyt_off)):
        base = cyt_off[s_index]
        for i in range(n_tri):
            row = base + i
            acc = 0.0
            for n_idx in range(3):
                if tri_mask[i, n_idx]:
                    neighbor = tri_nb[i, n_idx]
                    diff_coeff = mesh_diff[i, n_idx] * cyt_diff_coeff[s_index]
                    _jac_data_accum(row, base + neighbor, diff_coeff, indptr, indices, data)
                    acc -= diff_coeff
            # on-diagonal, the site itself
            _jac_data_accum(row, row, acc, indptr, indices, data)
    
    # Membrane diffusion
    for s_index in prange(len(mem_off)):
        base = mem_off[s_index]
        for i in range(n_bor):
            row = base + i
            acc = 0.0
            for n_idx in range(2):
                if bor_mask[i, n_idx]:
                    neighbor = bor_nb[i, n_idx]
                    diff_coeff = bor_diff[i, n_idx] * mem_diff_coeff[s_index]
                    _jac_data_accum(row, base + neighbor, diff_coeff, indptr, indices, data)
                    acc -= diff_coeff
            # on-diagonal, the site itself
            _jac_data_accum(row, row, acc, indptr, indices, data)

@njit(cache=True, fastmath=True, parallel=True)
def _jac_react_fill(y,
                    n_tri, n_bor,
                    cyt_off, mem_off,
                    adj_tri, to_mem,
                    plans_cyt, plans_mem,
                    indeptr, indices, data):
    """
    Fill in the reaction contributions to the Jacobian data array at (t, y).
    y: input concentration vector
    n_tri: number of triangles (cytosolic sites)
    n_bor: number of borders (membrane sites)
    cyt_off: offsets for cytosolic species in y
    mem_off: offsets for membrane species in y
    adj_tri: adjacent triangle index for each border (n_bor,)
    to_mem: scaling factors turns membrane concentrations into corresponding cytosolic concentrations (n_bor,)
    plans_cyt: compiled reaction rate plans for cytosolic reactions
    plans_mem: compiled reaction rate plans for membrane reactions
    indeptr, indices, data: CSR structure and data array to fill
    """
    
    # Cytosolic reactions
    for p_index in range(len(plans_cyt)):
        term_coeffs, mono_ptr, var_indexes, var_kinds, cyt_indexes, cyt_stoich, mem_indexes, mem_stoich = plans_cyt[p_index]
        Tmp = len(term_coeffs)
        for site in prange(n_tri):
            for mono in range(Tmp):
                coeff = term_coeffs[mono]
                for k1 in range(mono_ptr[mono], mono_ptr[mono+1]):
                    var_index = var_indexes[k1]
                    coeff_prod = coeff
                    for k2 in range(mono_ptr[mono], mono_ptr[mono+1]):
                        v2_index = var_indexes[k2]
                        if k2 != k1:
                            coeff_prod *= y[cyt_off[v2_index] + site]
                    # Update Jacobian entries for each affected species
                    for target_s_idx in range(len(cyt_indexes)):
                        target_s = cyt_indexes[target_s_idx]
                        stoich = cyt_stoich[target_s_idx]
                        row = cyt_off[target_s] + site
                        col = cyt_off[var_index] + site
                        _jac_data_accum(row, col, stoich * coeff_prod, indeptr, indices, data)
    
    # Membrane reactions
    for p_index in range(len(plans_mem)):
        term_coeffs, mono_ptr, var_indexes, var_kinds, cyt_indexes, cyt_stoich, mem_indexes, mem_stoich = plans_mem[p_index]
        Tmp = len(term_coeffs)
        for site in prange(n_bor):
            adj_triangle_idx = adj_tri[site]
            for mono in range(Tmp):
                coeff = term_coeffs[mono]
                for k1 in range(mono_ptr[mono], mono_ptr[mono+1]):
                    var_index = var_indexes[k1]
                    var_kind = var_kinds[k1]
                    coeff_prod = coeff
                    for k2 in range(mono_ptr[mono], mono_ptr[mono+1]):
                        v2_index = var_indexes[k2]
                        v2_kind = var_kinds[k2]
                        if k2 != k1:
                            if v2_kind == 0:  # cytosolic
                                coeff_prod *= y[cyt_off[v2_index] + adj_triangle_idx]
                            else:           # membrane
                                coeff_prod *= y[mem_off[v2_index] + site]
                    # Update Jacobian entries for each affected species
                    # cytosolic targets
                    scale_f = to_mem[site]
                    for target_s_idx in range(len(cyt_indexes)):
                        target_s = cyt_indexes[target_s_idx]
                        stoich = cyt_stoich[target_s_idx]
                        row = cyt_off[target_s] + adj_triangle_idx
                        if var_kind == 0:   # cytosolic
                            col = cyt_off[var_index] + adj_triangle_idx
                        else:       # membrane
                            col = mem_off[var_index] + site
                        _jac_data_accum(row, col, stoich * coeff_prod * scale_f, indeptr, indices, data)
                    # membrane targets
                    for target_s_idx in range(len(mem_indexes)):
                        target_s = mem_indexes[target_s_idx]
                        stoich = mem_stoich[target_s_idx]
                        row = mem_off[target_s] + site
                        if var_kind == 0:
                            col = cyt_off[var_index] + adj_triangle_idx
                        else:
                            col = mem_off[var_index] + site
                        _jac_data_accum(row, col, stoich * coeff_prod, indeptr, indices, data)