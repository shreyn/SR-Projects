import sympy as sp
from ExpressionTree import ConstantNode, VariableNode, OperatorNode

# Step 1: Convert your tree to a SymPy expression
def tree_to_sympy(tree):
    if isinstance(tree, ConstantNode):
        return sp.Float(tree.val)
    elif isinstance(tree, VariableNode):
        return sp.Symbol(tree.name)
    elif isinstance(tree, OperatorNode):
        args = [tree_to_sympy(child) for child in tree.children]
        op = tree.operator
        if op == '+':
            return args[0] + args[1]
        elif op == '-':
            return args[0] - args[1]
        elif op == '*':
            return args[0] * args[1]
        elif op == '/':
            return args[0] / args[1]
        elif op == 'sin':
            return sp.sin(args[0])
        else:
            raise ValueError(f"Unsupported operator: {op}")
    else:
        raise TypeError("Unknown node type")

# Step 2: Apply SymPy simplification
def canonicalize_sympy(tree):
    sympy_expr = tree_to_sympy(tree)
    simplified_expr = sp.simplify(sympy_expr)  # You can try sp.expand, sp.factor, etc.
    return simplified_expr
