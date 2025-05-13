"""
Read TreeEvolution_Canonicalize_SymPy.py  
"""

from ExpressionTree import tree_size
from Canonicalization_SymPy import canonicalize_sympy
import math

def fitness_canonicalization_sympy(tree, data_points, target_values, lambda_parsimony=0.01):
    canonical_form = canonicalize_sympy(tree)

    # If the symbolic expression is invalid or problematic
    if canonical_form == "NaN":
        return float('inf'), float('inf')

    mse = 0.0
    for point, target in zip(data_points, target_values):
        try:
            prediction = tree.evaluate(point)
            if math.isnan(prediction) or math.isinf(prediction):
                return float('inf'), float('inf')
        except Exception:
            return float('inf'), float('inf')

        mse += (prediction - target) ** 2

    mse /= len(data_points)
    complexity = tree_size(tree)
    fitness = mse + lambda_parsimony * complexity
    return fitness, mse
