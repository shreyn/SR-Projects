"""
THIS IS INSANELY SLOW. (stopped updating)
Why?:
sp.simplify() is very expensive (tries many different algebraic methods (factoring, trigsimp, cancel, etc))
simplify() is called on every child after mutation (so is called hundreds of times per generation)
these expressions are not cached.

FIX:
Instead of simplifying every tree, simplify only the elite trees.
Why? Since elite trees for sure will carry over to next gen, we dont waste time simplifying bad trees
.... STILL QUITE SLOW!
New Fix: 
Only use certain SymPy methods (not simplify(), which does them all)

IMPORTANT CHANGE:
No simplification of the actual tree in evolve(). 
Only simplify in the fitness function. 
Why? since if we were to simplify the actual tree, then the simplify() method needs to return a tree, but it is in SymPy notation, not tree notation. 
If we wanted simplify to return a tree, we would have to convert from tree to SymPy, run simplify, and then convert back to tree.
Instead, we only use simplify in fitness, since this will ensure that equivalent expressions have similar fitnesses, which makes sense.

"""

from Canonicalization.FitnessFunction_Canon_SymPy import fitness_canonicalization_sympy
from SR_Setup.RandomTreeGeneration import generate_random_tree
from SR_Setup.ExpressionTree import OperatorNode, tree_size
import random
import copy


def mutate(tree, max_depth, variables, operators, mutation_rate):
    if random.random() < mutation_rate:
        return generate_random_tree(max_depth, variables, operators)
    if isinstance(tree, OperatorNode): 
        mutated_children = [
            mutate(child, max_depth, variables, operators, mutation_rate)
            for child in tree.children
        ]
        return OperatorNode(tree.operator, mutated_children)
    elif random.random() < mutation_rate:
        return generate_random_tree(max_depth, variables, operators)
    return tree

def tournament_selection(population, fitnesses, tournament_size):
    zipped = list(zip(population, fitnesses))
    tournament_group = random.sample(zipped, tournament_size)
    return min(tournament_group, key=lambda pair: pair[1])[0]

def collect_all_nodes(tree):
    nodes = [tree]
    if isinstance(tree, OperatorNode):
        for child in tree.children:
            nodes.extend(collect_all_nodes(child))
    return nodes

def get_random_subtree(tree): 
    return random.choice(collect_all_nodes(tree))

def collect_random_path(tree):
    path = []
    while isinstance(tree, OperatorNode) and tree.children:
        idx = random.randint(0, len(tree.children) - 1)
        path.append(idx)
        tree = tree.children[idx]
    return path

def replace_subtree(tree, path, new_subtree):
    if not path:
        return new_subtree
    node = tree
    for i in path[:-1]:
        node = node.children[i]
    node.children[path[-1]] = new_subtree
    return tree

def crossover(tree1, tree2):
    tree1_copy = copy.deepcopy(tree1)
    tree2_copy = copy.deepcopy(tree2)
    path = collect_random_path(tree1_copy)
    new_subtree = get_random_subtree(tree2_copy)
    return replace_subtree(tree1_copy, path, copy.deepcopy(new_subtree))

def get_tree_depth(tree):
    if isinstance(tree, OperatorNode):
        return 1 + max(get_tree_depth(child) for child in tree.children)
    else:
        return 1

def crossover_with_depth_control(parent1, parent2, max_depth, variables, operators):
    for _ in range(5):
        child = crossover(parent1, parent2)
        if get_tree_depth(child) <= max_depth:
            return child
    return generate_random_tree(max_depth, variables, operators)

class Population:
    def __init__(self, size, max_depth, variables, operators, data_points, target_values, lambda_parsimony=0.1):
        self.size = size
        self.max_depth = max_depth
        self.variables = variables
        self.operators = operators
        self.data_points = data_points
        self.target_values = target_values
        self.trees = [generate_random_tree(max_depth, variables, operators) for _ in range(size)]
        self.fitnessmsepairs = [
            fitness_canonicalization_sympy(tree, self.data_points, self.target_values)
            for tree in self.trees
        ]
        self.scores = [pair[0] for pair in self.fitnessmsepairs]

    def evaluate(self):
        self.fitnessmsepairs = [
            fitness_canonicalization_sympy(tree, self.data_points, self.target_values)
            for tree in self.trees
        ]
        self.scores = [pair[0] for pair in self.fitnessmsepairs]

    def best_tree(self):
        best_idx = self.scores.index(min(self.scores))
        return self.trees[best_idx], *self.fitnessmsepairs[best_idx]

    def evolve(self, generations, tournament_size=5, elite_fraction=0.1, mutation_rate=0.05):
        for gen in range(generations):
            self.evaluate()
            scored = list(zip(self.trees, self.scores))
            scored.sort(key=lambda x: x[1])

            elite_count = max(1, int(self.size * elite_fraction))
            new_trees = [copy.deepcopy(tree) for tree, _ in scored[:elite_count]]

            while len(new_trees) < self.size:
                parent1 = tournament_selection(self.trees, self.scores, tournament_size)
                parent2 = tournament_selection(self.trees, self.scores, tournament_size)
                child = crossover_with_depth_control(
                    parent1, parent2, self.max_depth, self.variables, self.operators
                )
                child = mutate(child, self.max_depth, self.variables, self.operators, mutation_rate)
                new_trees.append(child)

            self.trees = new_trees
            self.evaluate()

            best_tree, best_fitness, best_mse = self.best_tree()
            # print(f"Generation {gen + 1}: Fitness = {best_fitness:.4f}, True MSE = {best_mse:.4f}")



# # TESTING

# # define target function: f(x) = x(x+1)/2
# def target_fn(x):
#     return (x*(x+1)/2)

# # generate training data
# data_points = [{'x': i} for i in range(20)]  # Inputs: x = 0 to 19
# target_values = [target_fn(dp['x']) for dp in data_points]

# # define problem parameters
# variables = ['x']
# operators = ['+', '-', '*', '/', 'sin']
# max_depth = 10
# lambda_parsimony = 0.5

# # initialize and evolve population
# pop = Population(
#     size=200,
#     max_depth=max_depth,
#     variables=variables,
#     operators=operators,
#     data_points=data_points,
#     target_values=target_values,
#     lambda_parsimony=lambda_parsimony
# )

# pop.evolve(generations=200, tournament_size=5, elite_fraction=0.1, mutation_rate=0.2)

# # output best expression
# best_tree, best_fitness, best_mse = pop.best_tree()
# print("\nBest Expression Found:")
# print(best_tree)
# print("Fitness (with penalty):", best_fitness)
# print("True MSE:", best_mse)

