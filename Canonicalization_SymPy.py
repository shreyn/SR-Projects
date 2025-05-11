
"""
THIS IS INSANELY SLOW. 
Why?:
sp.simplify() is very expensive (tries many different algebraic methods (factoring, trigsimp, cancel, etc))
simplify() is called on every child after mutation (so is called hundreds of times per generation)
these expressions are not cached.
"""

import sympy as sp
from ExpressionTree import ConstantNode, VariableNode, OperatorNode

def tree_to_sympy(tree):
    if isinstance(tree, ConstantNode):
        return sp.Float(tree.val)
    elif isinstance(tree, VariableNode):
        return sp.Symbol(tree.name)
    elif isinstance(tree, OperatorNode):
        args = [tree_to_sympy(child) for child in tree.children]
        op = tree.operator
        try:
            if op == '+':
                return args[0] + args[1]
            elif op == '-':
                return args[0] - args[1]
            elif op == '*':
                return args[0] * args[1]
            elif op == '/':
                return args[0] / args[1] if args[1] != 0 else sp.oo  # avoid div by zero
            elif op == 'sin':
                return sp.sin(args[0])
        except Exception:
            raise ValueError("Invalid tree structure (e.g., division by zero)")
    else:
        raise TypeError("Unknown node type")


def canonicalize_sympy(tree):
    try:
        sympy_expr = tree_to_sympy(tree)
        return sp.simplify(sympy_expr)
    except Exception:
        return tree  # fallback to original if simplification failed
