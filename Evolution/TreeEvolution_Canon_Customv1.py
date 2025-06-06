"""
MUCH FASTER!
However, need to manually add rules

Simplification here! (changing the actual tree itself)
"""


from Canonicalization.FitnessFunction_Canon_Customv1 import fitness_canonicalization_customv1
from SR_Setup.RandomTreeGeneration import generate_random_tree
from SR_Setup.ExpressionTree import ConstantNode, VariableNode, operator_arity, OperatorNode, tree_size
import random
import copy
from Canonicalization.Canon_Customv1 import simplify
import math

def mutate(tree, max_depth, variables, operators, mutation_rate):
    #Structural +local mutation. applies small changes to nodes with probability = mutation_rate.
    #basically, improvement is that mutation is much more granular, instead of just entire nodes to something completely random
    if random.random() < mutation_rate:
        return generate_random_tree(max_depth, variables, operators)

    if isinstance(tree, ConstantNode): #slightly perturb the constant
        if random.random() < mutation_rate:
            delta = random.uniform(-1.0, 1.0)
            return ConstantNode(tree.val + delta)
        return tree

    elif isinstance(tree, VariableNode): #with low prob, swap to a diff variable
        if random.random() < mutation_rate:
            return VariableNode(random.choice(variables))
        return tree

    elif isinstance(tree, OperatorNode): # With low prob, mutate operator to another of same arity
        new_operator = tree.operator
        if random.random() < mutation_rate:
            same_arity_ops = [op for op in operators if operator_arity[op] == operator_arity[tree.operator]]
            if same_arity_ops:
                new_operator = random.choice(same_arity_ops)

        mutated_children = [ #recursively mutate children
            mutate(child, max_depth, variables, operators, mutation_rate)
            for child in tree.children
        ]
        return OperatorNode(new_operator, mutated_children)

    return tree


def tournament_selection(population, fitnesses, tournament_size):
    #standard k tournament selection
    zipped = list(zip(population, fitnesses)) #pair trees and scores
    tournament_group = random.sample(zipped, tournament_size)  #sample k of them
    best_pair = min(tournament_group, key=lambda pair: pair[1]) #best (lowest) fitness
    best_tree = best_pair[0]  #return just the tree
    return best_tree

def collect_all_nodes(tree):
    nodes = [tree]
    if isinstance(tree, OperatorNode): #if node is operator, add its children
        for child in tree.children:
            nodes.extend(collect_all_nodes(child))
    return nodes

def get_random_subtree(tree): 
    return random.choice(collect_all_nodes(tree))

def collect_all_paths(node, path=()):
    """
    Returns a list of all paths from root to every node (including internal nodes and leaves).
    Each path is a tuple of child-indices, e.g. () for the root, (0,2) for root→child0→child2, etc.
    """
    paths = [path]
    if isinstance(node, OperatorNode):
        for idx, child in enumerate(node.children):
            paths.extend(collect_all_paths(child, path + (idx,)))
    return paths

def collect_random_path(tree):
    """
    Chooses *any* node in the tree (root, internal, or leaf) at random.
    """
    all_paths = collect_all_paths(tree)
    return list(random.choice(all_paths))

def replace_subtree(tree, path, new_subtree):
    #walks along the path
    #replaces node found at the end of the path with the new_subtree
    if not path:
        return new_subtree
    node = tree
    for i in path[:-1]:
        node = node.children[i]
    node.children[path[-1]] = new_subtree
    return tree
### Above two functions ####
#like a folder system:
#path (open Desktop, then College, and then you will find the file)
#replace_subtree is like pasting a new folder at that file location

def crossover(tree1, tree2):
    # find a crossover point in tree1 (through path)
    # get a random subtree of tree 2
    # return tree1 with the replaced subtree of 2 at the crossover point
    tree1_copy = copy.deepcopy(tree1)
    tree2_copy = copy.deepcopy(tree2)
    path = collect_random_path(tree1_copy) # where to insert
    new_subtree = get_random_subtree(tree2_copy)# what to insert
    return replace_subtree(tree1_copy, path, copy.deepcopy(new_subtree))

##### Hard constraint for crossover tree depth: 
def get_tree_depth(tree):
    if isinstance(tree, OperatorNode):
        return 1 + max(get_tree_depth(child) for child in tree.children)
    else:
        return 1
def crossover_with_depth_control(parent1, parent2, max_depth, variables, operators):
    for _ in range(5):  # try up to 5 times
        child = crossover(parent1, parent2)
        if get_tree_depth(child) <= max_depth:
            return child
    return generate_random_tree(max_depth, variables, operators)  # fallback


class Population:
    def __init__(self, size, max_depth, variables, operators, data_points, target_values, lambda_parsimony=0.1, immigration_rate=0.05):
        self.size = size
        self.max_depth = max_depth
        self.variables = variables
        self.operators = operators
        self.data_points = data_points
        self.target_values = target_values
        self.trees = [generate_random_tree(max_depth, variables, operators) for _ in range(size)]
        self.fitnessmsepairs = [fitness_canonicalization_customv1(tree, self.data_points, self.target_values) for tree in self.trees] 
        self.scores = [pair[0] for pair in self.fitnessmsepairs] #just fitness for selection
        self.immigration_rate = immigration_rate #added immigration (completely random trees introduced per generation)
        self.mse_history = []  # store true MSEs across generations

    def evaluate(self): #for recalculating fitness scores for trees (updates self.scores using latest self.trees)
        self.fitnessmsepairs = [fitness_canonicalization_customv1(tree, self.data_points, self.target_values) for tree in self.trees]
        self.scores = [pair[0] for pair in self.fitnessmsepairs]

    def best_tree(self): #best tree and its score
        best_idx = self.scores.index(min(self.scores))
        return self.trees[best_idx], *self.fitnessmsepairs[best_idx]

    def evolve(self, generations, tournament_size=5, elite_fraction=0.1, mutation_rate=0.05):
        for gen in range(generations):
            self.evaluate()
            scored = list(zip(self.trees, self.scores))
            scored.sort(key=lambda x: x[1])  # sort by fitness

            # elitism
            elite_count = max(1, int(self.size * elite_fraction))
            new_trees = [copy.deepcopy(tree) for tree, _ in scored[:elite_count]]

            # fill the rest of the population
            while len(new_trees) < self.size:
                # IMMIGRATION: with some chance, insert a new individual
                if random.random() < self.immigration_rate:
                    immigrant = generate_random_tree(self.max_depth, self.variables, self.operators)
                    immigrant = simplify(immigrant)
                    new_trees.append(immigrant)
                    continue

                # Otherwise evolve using crossover + mutation
                parent1 = tournament_selection(self.trees, self.scores, tournament_size)
                parent2 = tournament_selection(self.trees, self.scores, tournament_size)
                child = crossover_with_depth_control(parent1, parent2, self.max_depth, self.variables, self.operators)
                child = mutate(child, self.max_depth, self.variables, self.operators, mutation_rate)
                child = simplify(child)
                new_trees.append(child)

            self.trees = new_trees
            self.evaluate()

            best_tree, best_fitness, best_mse = self.best_tree()
            self.mse_history.append(best_mse)
            print(f"Generation {gen + 1}: Fitness = {best_fitness:.4f}, True MSE = {best_mse:.4f}")




# ## TESTING

# # define target function: f(x) = x(x+1)/2
# def target_fn(x):
#     return (x*(x+1))/2

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

# pop.evolve(generations=200, tournament_size=5, elite_fraction=0.1, mutation_rate=0.1)

# # output best expression
# best_tree, best_fitness, best_mse = pop.best_tree()
# print("\nBest Expression Found:")
# print(best_tree)
# print("Fitness (with penalty):", best_fitness)
# print("True MSE:", best_mse)


# #more complex target function
# # Target function: moderately complex
# def target_fn(x):
#     return math.sin(x) + math.log(x + 1) + math.sqrt(x) + 0.5 * (x ** 2)


# # Generate training data
# data_points = [{'x': x} for x in range(1, 200)]  # avoid x = 0 for log/sqrt
# target_values = [target_fn(dp['x']) for dp in data_points]

# # Define symbolic regression parameters
# variables = ['x']
# operators = ['+', '-', '*', '/', 'sin', 'cos', 'log', 'exp', '^']
# max_depth = 10
# lambda_parsimony = 0.1
# immigration_rate = 0.05  # 5% chance of injecting a new random individual

# # Initialize and run evolution
# pop = Population(
#     size=200,
#     max_depth=max_depth,
#     variables=variables,
#     operators=operators,
#     data_points=data_points,
#     target_values=target_values,
#     lambda_parsimony=lambda_parsimony,
#     immigration_rate=immigration_rate
# )

# pop.evolve(
#     generations=500,
#     tournament_size=5,
#     elite_fraction=0.1,
#     mutation_rate=0.1
# )

# # Output best result
# best_tree, best_fitness, best_mse = pop.best_tree()
# print("\nBest Expression Found:")
# print(best_tree)
# print("Fitness (with parsimony penalty):", best_fitness)
# print("True MSE:", best_mse)
