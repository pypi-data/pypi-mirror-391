"""
Sparse multivariate polynomial for reaction-rate expressions.

Representation:
- PolyTerms: dict[frozenset[str|int], float]
- Each key is a frozenset of variable names (species) that form a monomial.
- The special key frozenset([1]) denotes the constant term (1).
- Coefficients are real numbers.
Supports + and * with numbers and other ReactionRateExpression instances.
"""

class ReactionRateExpression:
    """A sparse polynomial with set-based monomials to avoid duplicate variable ordering."""
    
    def __init__(self, expression=None):
        """Initialize the polynomial expression."""
        if expression is None:
            self.PolyTerms = {frozenset([1]): 0}  # dict mapping frozenset of variables to coefficient
        elif isinstance(expression, ReactionRateExpression):
            self.PolyTerms = expression.PolyTerms.copy()
        elif isinstance(expression, (int, float)):
            self.PolyTerms = {frozenset([1]): expression}
        elif isinstance(expression, ChemSubs):
            self.PolyTerms = {frozenset([expression.name]): 1}
        else:
            raise TypeError("Unsupported type for ReactionRateExpression initialization.")
    
    def __str__(self):
        """Return a human-readable string representation of the polynomial."""
        terms = []
        for vars_set, coeff in self.PolyTerms.items():
            if vars_set == frozenset([1]):
                terms.append(f"{coeff}")
            else:
                vars_str = '*'.join(sorted(str(v) for v in vars_set))
                terms.append(f"{coeff}*{vars_str}")
        return ' + '.join(terms) if terms else "0"

    def __add__(self, other):
        """
        Add another expression or a scalar.
        
        - Merges identical monomials by summing coefficients.
        - Scalars contribute to the constant term (frozenset([1])).
        """
        if isinstance(other, ReactionRateExpression):
            new_expr = ReactionRateExpression()
            # merge terms with identical variable-sets by summing their coefficients
            combined_terms = self.PolyTerms.copy()
            for vars_set, coeff in other.PolyTerms.items():
                combined_terms[vars_set] = combined_terms.get(vars_set, 0) + coeff
            new_expr.PolyTerms = combined_terms
            return new_expr
        elif isinstance(other, (int, float)):
            new_expr = ReactionRateExpression()
            new_expr.PolyTerms = self.PolyTerms.copy()
            new_expr.PolyTerms[frozenset([1])] = new_expr.PolyTerms.get(frozenset([1]), 0) + other
            return new_expr
        return NotImplemented
    
    def __radd__(self, other):
        """Support scalar + expression."""
        return self.__add__(other)
    
    def __mul__(self, other):
        """
        Multiply by another expression or a scalar.
        
        - Scalar multiplication scales all coefficients.
        - Expression multiplication unions variable sets for monomial products.
        - The constant monomial (frozenset([1])) acts as multiplicative identity for variables.
        """
        if isinstance(other, ReactionRateExpression):
            new_expr = ReactionRateExpression()
            new_terms = {}
            for vars_set1, coeff1 in self.PolyTerms.items():
                for vars_set2, coeff2 in other.PolyTerms.items():
                    new_vars_set = None
                    if vars_set1 == frozenset([1]):
                        new_vars_set = vars_set2
                    elif vars_set2 == frozenset([1]):
                        new_vars_set = vars_set1
                    else:
                        new_vars_set = frozenset(set(vars_set1) | set(vars_set2))
                    new_terms[new_vars_set] = new_terms.get(new_vars_set, 0) + coeff1 * coeff2
            new_expr.PolyTerms = new_terms
            return new_expr
        elif isinstance(other, (int, float)):
            new_expr = ReactionRateExpression()
            new_expr.PolyTerms = {vars_set: coeff * other for vars_set, coeff in self.PolyTerms.items()}
            return new_expr
        return NotImplemented

    def __rmul__(self, other):
        """Support scalar * expression."""
        return self.__mul__(other)

if __name__ == "__main__":
    from .ChemSubs import ChemSubs

    A = ChemSubs("A")
    B = ChemSubs("B")
    C = ChemSubs("C")

    expr1 = C * 2 + 1
    expr2 = A * B + 3

    combined_expr = expr1 * expr2
    print(combined_expr)
    print(ReactionRateExpression(5))
    print(ReactionRateExpression(A) + ReactionRateExpression(B) + 2)