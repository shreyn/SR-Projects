from BasicSRTrees.RandomTreeGeneration import generate_random_tree, p_leaf_at_depth
import math

def fitness(tree, data_points, target_values):
    """
    tree: the root node of your expression tree
    data_points: list of dictionaries like [{'x': 2, 'y': 3}, ...]
    target_values: list of target outputs like [5.0, 7.3, ...]
    """
    errors = []
    for inputs, true_output in zip(data_points, target_values):
        try:
            prediction = tree.evaluate(inputs)
            if math.isinf(prediction) or math.isnan(prediction):
                prediction = 1e6  # Big penalty for invalid outputs
        except Exception:
            prediction = 1e6  # Big penalty if the tree evaluation fails
        
        error = (prediction - true_output) ** 2  # Squared error
        errors.append(error)
    
    mse = sum(errors) / len(errors)
    return mse  # Lower fitness = better


# Example data points:
# data_points = [{'x': 2, 'y': 3}, {'x': 1, 'y': 4}, {'x': 0, 'y': 5}]
# target_values = [9.0, 7.0, 5.0]  # Whatever the true outputs are

# variables = ['x']
# operators = ['+', '-', '*', '/', 'sin']
# max_depth = 3

# randTree = generate_random_tree(max_depth, variables=variables, operators=operators)
# #print(randTree)
# print("Fitness (MSE):", fitness(randTree, data_points, target_values))
