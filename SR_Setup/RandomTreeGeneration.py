import random
from SR_Setup.ExpressionTree import operator_arity, Node, ConstantNode, VariableNode, OperatorNode
import math

def generate_constant_node():
    if random.random() < 0.5:
        #fixed set of useful constants
        value = random.choice([-1, 0, 0.5, 1, 2, math.e, math.pi, 10])
    else:
        #wider uniform range with control
        value = round(random.uniform(-20, 20), 2)
    return ConstantNode(value)


def generate_random_tree(max_depth, variables, operators, current_depth=0):
    p_leaf = p_leaf_at_depth(current_depth, max_depth)
    
    if (current_depth >= max_depth or random.random() < p_leaf):  # leaf node
        if random.random() < 0.3: #constant
            return generate_constant_node()    
        else: #var
            variable = random.choice(variables)
            return VariableNode(variable)
    else:  # operator node
        oper = random.choice(operators)
        arity = operator_arity[oper]
        children = [generate_random_tree(max_depth, variables, operators, current_depth + 1)
                    for _ in range(arity)]
        return OperatorNode(oper, children)

def p_leaf_at_depth(depth, max_depth): #prob. of leaf is low initially, then goes up, till curr depth > max_depth (will be a leaf)
    return 1.0 if depth >= max_depth else 0.2+0.5*(depth/max_depth)

# variables = ['x', 'y']
# operators = ['+', '-', '*', '/', 'sin', 'cos', 'log', 'exp', 'abs', 'sqrt', '^', 'max', 'min']
# max_depth = 5
# variable_vals = {'x': 2, 'y': 3}
# randTree = generate_random_tree(max_depth, variables, operators)
# print(randTree)
# print(randTree.evaluate(variable_vals))
