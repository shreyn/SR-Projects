from ExpressionTree import ConstantNode, VariableNode, OperatorNode

def canonicalize(tree):
    if isinstance(tree, OperatorNode):
        # First canonicalize children
        children = [canonicalize(child) for child in tree.children]

        # Flatten associative children
        if tree.operator in ['+', '*']:
            flat_children = []
            for child in children:
                if isinstance(child, OperatorNode) and child.operator == tree.operator:
                    flat_children.extend(child.children)
                else:
                    flat_children.append(child)
            children = flat_children

        # Constant folding
        if tree.operator in ['+', '*']:
            constant_value = 0 if tree.operator == '+' else 1
            new_children = []

            for child in children:
                if isinstance(child, ConstantNode):
                    if tree.operator == '+':
                        constant_value += child.val
                    else:  # '*'
                        constant_value *= child.val
                else:
                    new_children.append(child)

            # Identity simplification
            if tree.operator == '+' and constant_value != 0:
                new_children.append(ConstantNode(constant_value))
            elif tree.operator == '*' and constant_value != 1:
                new_children.append(ConstantNode(constant_value))

            # Special case: if one child and no others, return it directly
            if not new_children:
                return ConstantNode(constant_value)
            elif len(new_children) == 1:
                return new_children[0]
            else:
                children = new_children

        # Sort children for commutativity
        if tree.operator in ['+', '*']:
            children.sort(key=lambda x: repr(x))

        return OperatorNode(tree.operator, children)
    else:
        return tree  # Constant or Variable




# x = VariableNode('x')
# y = VariableNode('y')

# # Tree: ((x + 3) + (5 + y)) → should become (x + y + 8)
# tree = OperatorNode('+', [
#     OperatorNode('+', [x, ConstantNode(3)]),
#     OperatorNode('+', [ConstantNode(5), y])
# ])

# canon = canonicalize(tree)
# print("Canonical:", canon)