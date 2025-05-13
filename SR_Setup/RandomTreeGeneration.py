import random
from SR_Setup.ExpressionTree import Node, ConstantNode, VariableNode, OperatorNode

def generate_random_tree(max_depth, variables, operators, current_depth=0):
    p_leaf = p_leaf_at_depth(current_depth, max_depth)
    
    if (current_depth >= max_depth or random.random() < p_leaf): #leaf node
        if random.random() < 0.3:  # 10% chance anywhere to insert a constant node
            value = random.randrange(-5, 5)
            return ConstantNode(value)
        else:
            variable = random.choice(variables)
            return VariableNode(variable)
    else: #operator node
        oper = random.choice(operators)
        if oper in ['sin']: #unary
            children = [generate_random_tree(max_depth, variables, operators, current_depth + 1)]
        else: #binary
            children = [
                generate_random_tree(max_depth, variables, operators, current_depth + 1),
                generate_random_tree(max_depth, variables, operators, current_depth + 1)
            ]
        return OperatorNode(oper, children)

def p_leaf_at_depth(depth, max_depth): #prob. of leaf is low initially, then goes up, till curr depth > max_depth (will be a leaf)
    return 1.0 if depth >= max_depth else 0.5+0.5*(depth/max_depth)

# variables = ['x', 'y']
# operators = ['+', '-', '*', '/', 'sin']
# max_depth = 5
# variable_vals = {'x': 2, 'y': 3}
# randTree = generate_random_tree(max_depth, variables, operators)
# print(randTree)
# print(randTree.evaluate(variable_vals))
