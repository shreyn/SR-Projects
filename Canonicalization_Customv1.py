"""
MUCH FASTER!
However, need to manually add rules
"""

from ExpressionTree import ConstantNode, VariableNode, OperatorNode
import math

def simplify(tree):
    if isinstance(tree, OperatorNode):
        # First canonicalize children
        children = [simplify(child) for child in tree.children]

        # Flatten associative children
        if tree.operator in ['+', '*']:
            flat_children = []
            for child in children:
                if isinstance(child, OperatorNode) and child.operator == tree.operator:
                    flat_children.extend(child.children)
                else:
                    flat_children.append(child)
            children = flat_children

        # General constant folding (any op, if all children are constants)
        if all(isinstance(c, ConstantNode) for c in children):
            try:
                values = [c.val for c in children]
                if tree.operator == '+':
                    return ConstantNode(sum(values))
                elif tree.operator == '*':
                    result = 1
                    for v in values:
                        result *= v
                    return ConstantNode(result)
                elif tree.operator == '-':
                    return ConstantNode(values[0] - values[1])
                elif tree.operator == '/':
                    if values[1] == 0:
                        return ConstantNode(float('inf'))
                    return ConstantNode(values[0] / values[1])
                elif tree.operator == 'sin':
                    return ConstantNode(math.sin(values[0]))
            except:
                pass  # fallback to structural

        # Redundancy elimination: x - x = 0, x / x = 1
        if len(children) == 2 and repr(children[0]) == repr(children[1]):
            if tree.operator == '-':
                return ConstantNode(0)
            elif tree.operator == '/':
                return ConstantNode(1)

        # Constant folding (accumulate constants in +/*)
        if tree.operator in ['+', '*']:
            constant_value = 0 if tree.operator == '+' else 1
            new_children = []

            for child in children:
                if isinstance(child, ConstantNode):
                    if tree.operator == '+':
                        constant_value += child.val
                    else:
                        constant_value *= child.val
                else:
                    new_children.append(child)

            # Identity simplification
            if tree.operator == '+' and constant_value != 0:
                new_children.append(ConstantNode(constant_value))
            elif tree.operator == '*' and constant_value != 1:
                new_children.append(ConstantNode(constant_value))

            if not new_children:
                return ConstantNode(constant_value)
            elif len(new_children) == 1:
                return new_children[0]
            else:
                children = new_children

        # Sort commutative children
        if tree.operator in ['+', '*']:
            children.sort(key=lambda x: repr(x))

        return OperatorNode(tree.operator, children)

    else:
        return tree  # Constant or Variable
