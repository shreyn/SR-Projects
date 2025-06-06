"""
VERY IMPORTANT DISTINCTION:
No simplification here! (since the actual tree is being altered already).
This is different from SymPy, since for that, the tree is not being altered, and simplification is only used in fitness.

"""

from SR_Setup.ExpressionTree import tree_size
from Canonicalization.Canon_Customv1 import simplify

def fitness_canonicalization_customv1(tree, data_points, target_values, lambda_parsimony=0.01):
    mse = 0.0
    for point, target in zip(data_points, target_values):
        try:
            pred = tree.evaluate(point)
        except Exception:
            return float('inf'), float('inf')  # both fitness and mse are infinite

        mse += (pred - target) ** 2
    mse /= len(data_points)

    complexity = tree_size(tree)
    fitness = mse + (lambda_parsimony * complexity)
    return fitness, mse


# Example data points:
# data_points = [{'x': 2, 'y': 3}, {'x': 1, 'y': 4}, {'x': 0, 'y': 5}]
# target_values = [9.0, 7.0, 5.0]  # Whatever the true outputs are

# variables = ['x']
# operators = ['+', '-', '*', '/', 'sin']
# max_depth = 3

# randTree = generate_random_tree(max_depth, variables=variables, operators=operators)
# #print(randTree)
# print("Fitness (MSE):", fitness(randTree, data_points, target_values))
