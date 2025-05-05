from ExpressionTree import ConstantNode, VariableNode, OperatorNode

def canonicalize(tree):
    if isinstance(tree, OperatorNode):
        # First canonicalize all children
        children = [canonicalize(child) for child in tree.children]

        # If op is associative, flatten nested operators of same kind
        if tree.operator in ['+', '*']:
            flat_children = []
            for child in children:
                if isinstance(child, OperatorNode) and child.operator == tree.operator:
                    flat_children.extend(child.children)
                else:
                    flat_children.append(child)
            children = flat_children

        # If op is commutative, sort children by repr (for structural equality)
        if tree.operator in ['+', '*']:
            children.sort(key=lambda x: repr(x))

        return OperatorNode(tree.operator, children)
    else:
        return tree  # Constant or Variable




# Define variables
x = VariableNode('x')
y = VariableNode('y')
z = VariableNode('z')

# Build two equivalent trees with different structure/order
tree1 = OperatorNode('+', [OperatorNode('+', [x, y]), z])        # (x + y) + z
tree2 = OperatorNode('+', [z, OperatorNode('+', [y, x])])        # z + (y + x)

# Canonicalize both
canon1 = canonicalize(tree1)
canon2 = canonicalize(tree2)

# Print both
print("Canonical 1:", canon1)
print("Canonical 2:", canon2)

# Check if canonical forms match
print("Are canonical forms equal?", repr(canon1) == repr(canon2))
