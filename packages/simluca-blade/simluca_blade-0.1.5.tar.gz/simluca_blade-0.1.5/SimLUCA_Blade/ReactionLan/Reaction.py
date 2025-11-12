"""Reaction container tying reactant and product groups together with minimal formatting utilities."""
from .ReactionRateExpression import ReactionRateExpression

class Reaction:
    """A reaction with ordered reactants and products (lists of ChemSubs)."""
    def __init__(self, reactants, products):
        """Initialize from SubsGroup instances."""
        self.reactants = reactants.SubsList  # List of ChemSubs instances
        self.products = products.SubsList    # List of ChemSubs instances
        self.rate_expression = None

    def __str__(self):
        """Return a human-readable 'A + B -> C + D' string."""
        reactants_str = '∅' # Empty set symbol for no reactants
        if len(self.reactants) != 0:
            reactants_str = ' + '.join(str(r.name) for r in self.reactants)
        products_str = '∅' # Empty set symbol for no products
        if len(self.products) != 0:
            products_str = ' + '.join(str(p.name) for p in self.products)
        rate_str = f" ; Rate: {self.rate_expression}" if self.rate_expression is not None else ""
        return f"{reactants_str} -> {products_str}{rate_str}"

    def SetRate(self, rate_expression: ReactionRateExpression):
        """Set the rate expression for this reaction."""
        self.rate_expression = ReactionRateExpression(rate_expression)
    
    def AllSpecies(self):
        """Return a set of all species (ChemSubs) involved in this reaction."""
        return set(self.reactants + self.products)

if __name__ == "__main__":
    from .ChemSubs import ChemSubs

    # Example usage: build A + B -> C + D using @ to group and >> to form a Reaction.
    A = ChemSubs("A")
    B = ChemSubs("B")
    C = ChemSubs("C")
    D = ChemSubs("D")

    reaction = A @ B >> C @ D
    reaction.SetRate(2 * A * B + 3)
    
    print(reaction)