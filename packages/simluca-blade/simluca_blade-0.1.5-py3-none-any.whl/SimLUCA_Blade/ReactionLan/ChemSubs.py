"""
Chemical substituents (species) and grouping utilities.

Provides:
- ChemSubs: a species with operator overloads to build reactions and rate expressions.
- SubsGroup: a lightweight container to group species.
Operators:
- @ groups species (concatenation into SubsGroup)
- >> forms a Reaction from reactants to products
- +, * interoperate with ReactionRateExpression to build polynomial kinetics
"""

from .Reaction import Reaction
from .ReactionRateExpression import ReactionRateExpression

class ChemSubs:
    """Represents a chemical substituent (species) participating in reactions and rate expressions."""
    def __init__(self, name):
        """Initialize a species with a unique name (string identifier)."""
        self.name = name
        self.index = None  # to be set later for vectorized state ordering
        self.init_distribution = None  # function to initialize concentration distribution
        self.init_scope = None  # function to define geometric scope for initial distribution

    def __matmul__(self, other):
        """Use A @ B to build a SubsGroup by concatenating species/groups."""
        if isinstance(other, ChemSubs):
            return SubsGroup([self, other])
        elif isinstance(other, SubsGroup):
            return SubsGroup([self] + other.SubsList)
        return NotImplemented

    def __rshift__(self, other):
        """Use A >> B to create a Reaction from reactants to products."""
        if isinstance(other, ChemSubs):
            return Reaction(SubsGroup([self]), SubsGroup([other]))
        elif isinstance(other, SubsGroup):
            return Reaction(SubsGroup([self]), other)
        return NotImplemented
    
    # to set an index for the chemical substituent
    def IndexChem(self, index: int):
        """Assign an integer index to this species (e.g., for vectorized state ordering)."""
        self.index = index

    def SetInitDistribution(self, init_func: callable, *args, **kwargs):
        """
        Set the initial concentration distribution function for this species.
        
        The function should accept mesh parameters and return an array of initial concentrations.
        Additional args/kwargs are passed to the init_func when called.
        """
        def wrapped_init():
            return init_func(*args, **kwargs)
        self.init_distribution = wrapped_init

    def SetInitScope(self, init_scope: callable):
        """
        Set the geometric scope where the previously defined init_distribution applies.
        The function should accept geometric coordinates (x, r) and return a boolean value indicating if the scope is valid.
        e.g., init_scope = lambda x, r: x < 1000
        """
        self.init_scope = init_scope


    # --------------------------------- overloading operators for reaction rate calculation ---------------------------------
    def __eq__(self, other):
        """Species equality is name-based so they can be hashed and compared."""
        if isinstance(other, ChemSubs):
            return self.name == other.name
        return NotImplemented
    def __hash__(self):
        """Hash by name to allow use in sets/dicts."""
        return hash(self.name)
    def __str__(self):
        """Return the species name as its string representation."""
        return self.name
    
    def __add__(self, other):
        """
        Build a ReactionRateExpression representing sum with another species/constant/expression.
        
        Representation:
        - PolyTerms maps frozenset of variable names to coefficient.
        - frozenset([1]) denotes the constant (1) monomial.
        """
        if isinstance(other, ChemSubs):
            new_expr = ReactionRateExpression()
            new_expr.PolyTerms = {frozenset([self.name]): 1,
                                  frozenset([other.name]): 1}
            return new_expr
        elif isinstance(other, (int, float)):
            new_expr = ReactionRateExpression()
            new_expr.PolyTerms = {frozenset([self.name]): 1,
                                  frozenset([1]): other}
            return new_expr
        elif isinstance(other, ReactionRateExpression):
            new_expr = ReactionRateExpression()
            new_expr.PolyTerms = other.PolyTerms.copy()
            new_expr.PolyTerms[frozenset([self.name])] = new_expr.PolyTerms.get(frozenset([self.name]), 0) + 1
            return new_expr
        return NotImplemented
    def __radd__(self, other):
        """Support commutative addition with numbers/expressions."""
        return self.__add__(other)
    
    def __mul__(self, other):
        """
        Build a ReactionRateExpression representing product with species/constant/expression.
        
        Multiplication combines variable sets (union for monomials) and multiplies coefficients.
        """
        if isinstance(other, ChemSubs):
            new_expr = ReactionRateExpression()
            new_expr.PolyTerms = {frozenset([self.name, other.name]): 1}
            return new_expr
        elif isinstance(other, (int, float)):
            new_expr = ReactionRateExpression()
            new_expr.PolyTerms = {frozenset([self.name]): other}
            return new_expr
        elif isinstance(other, ReactionRateExpression):
            new_expr = ReactionRateExpression()
            new_terms = {}
            for vars_set, coeff in other.PolyTerms.items():
                new_vars_set = None
                if vars_set == frozenset([1]):
                    new_vars_set = frozenset([self.name])
                else:
                    new_vars_set = frozenset(set(vars_set) | {self.name})
                new_terms[new_vars_set] = coeff
            new_expr.PolyTerms = new_terms
            return new_expr
        return NotImplemented
    def __rmul__(self, other):
        """Support commutative multiplication with numbers/expressions."""
        return self.__mul__(other)

class SubsGroup:
    """A simple ordered collection of ChemSubs used to form Reaction reactants/products."""
    def __init__(self, SubsList: list[ChemSubs]):
        """Initialize with a list of ChemSubs instances."""
        self.SubsList = SubsList

    def __matmul__(self, other):
        """Concatenate two groups or append a species using @."""
        if isinstance(other, SubsGroup):
            return SubsGroup(self.SubsList + other.SubsList)
        elif isinstance(other, ChemSubs):
            return SubsGroup(self.SubsList + [other])
        return NotImplemented

    def __rshift__(self, other):
        """Create a Reaction using this group as reactants and the right operand as products."""
        if isinstance(other, SubsGroup):
            return Reaction(self, other)
        elif isinstance(other, ChemSubs):
            return Reaction(self, SubsGroup([other]))
        return NotImplemented

class CytSubs(ChemSubs):
    """A chemical substituent localized in the cytoplasm."""
    def __init__(self, name: str, diffusion_coeff=1e7):
        """
        name: string identifier for the species
        diffusion_coeff: 3D diffusion coefficient in nm^2/s
        """
        super().__init__(name)
        self.diffusion_coeff = diffusion_coeff

class MemSubs(ChemSubs):
    """A chemical substituent localized on the membrane."""
    def __init__(self, name: str, diffusion_coeff=1e4):
        """
        name: string identifier for the species
        diffusion_coeff: 2D diffusion coefficient in nm^2/s
        """
        super().__init__(name)
        self.diffusion_coeff = diffusion_coeff

def Void():
    """
    An empty SubsGroup representing no chemical species,
    used to form reactants/products in zero-order source/sink reactions.
    Usage:
        rs.AddReaction(Void() >> A, k_prod)  # zero-order production of A
        rs.AddReaction(B >> Void(), k_deg)   # zero-order degradation of B
    """
    return SubsGroup([])