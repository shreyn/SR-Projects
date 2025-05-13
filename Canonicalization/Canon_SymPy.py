"""
Read TreeEvolution_Canonicalize_SymPy.py  
"""

import sympy as sp
from SR_Setup.ExpressionTree import ConstantNode, VariableNode, OperatorNode

def tree_to_sympy(tree):
    if isinstance(tree, ConstantNode):
        return sp.Float(tree.val)

    elif isinstance(tree, VariableNode):
        return sp.Symbol(tree.name)

    elif isinstance(tree, OperatorNode):
        #convert children first
        args = [tree_to_sympy(child) for child in tree.children]
        op = tree.operator

        #check for constant denominator = 0
        if op == '/' and isinstance(tree.children[1], ConstantNode):
            if tree.children[1].val == 0:
                raise ZeroDivisionError("Division by constant zero detected")

        # standard operator mappings
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
        raise TypeError(f"Unknown node type: {type(tree)}")


def canonicalize_sympy(tree):
    try:
        expr = tree_to_sympy(tree)
        expr = sp.expand(expr)
        expr = sp.powsimp(expr, deep=True)
        expr = sp.cancel(expr)
        return expr

    except Exception:
        return "NaN"
