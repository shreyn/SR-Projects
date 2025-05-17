from SR_Setup.FitnessFunction_Parsimony import fitness_parsimony
from SR_Setup.RandomTreeGeneration import generate_random_tree
from SR_Setup.ExpressionTree import OperatorNode, tree_size
import random
import copy
import math

def mutate(tree, max_depth, variables, operators,  mutation_rate):
    #At root: mutation_rate chance of replacing entire tree.
    #Else: walk through tree recursively, each OperatorNode has same operator but different subtrees, each leaf can be replaced
    #Else: return same tree
    if random.random() < mutation_rate:
        return generate_random_tree(max_depth, variables, operators)
    if isinstance(tree, OperatorNode): 
        mutated_children = []
        for child in tree.children:
            mutated_child = mutate(child, max_depth, variables, operators, mutation_rate)
            mutated_children.append(mutated_child)
        return OperatorNode(tree.operator, mutated_children) #same operator, mutated children
    elif random.random() < mutation_rate: #if leaf, small chance of new tree
        return generate_random_tree(max_depth, variables, operators)
    return tree #else, return unchanged

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
    path = collect_random_path(tree1_copy) # Where to insert
    new_subtree = get_random_subtree(tree2_copy)# What to insert
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
    def __init__(self, size, max_depth, variables, operators, data_points, target_values, lambda_parsimony=0.1):
        self.size = size
        self.max_depth = max_depth
        self.variables = variables
        self.operators = operators
        self.data_points = data_points
        self.target_values = target_values
        self.trees = [generate_random_tree(max_depth, variables, operators) for _ in range(size)] #initial pop.
        self.fitnessmsepairs = [fitness_parsimony(tree, self.data_points, self.target_values) for tree in self.trees] 
        self.scores = [pair[0] for pair in self.fitnessmsepairs] #just fitness for selection

    def evaluate(self): #for recalculating fitness scores for trees (updates self.scores using latest self.trees)
        self.fitnessmsepairs = [fitness_parsimony(tree, self.data_points, self.target_values) for tree in self.trees]
        self.scores = [pair[0] for pair in self.fitnessmsepairs]

    def best_tree(self): #best tree and its score
        best_idx = self.scores.index(min(self.scores))
        return self.trees[best_idx], *self.fitnessmsepairs[best_idx]

    def evolve(self, generations, tournament_size=5, elite_fraction=0.1, mutation_rate=0.05):
        for gen in range(generations):
            self.evaluate()
            scored = list(zip(self.trees, self.scores))
            scored.sort(key=lambda x: x[1]) #pairs tree with fitness, sorts by best first

            elite_count = max(1, int(self.size * elite_fraction)) #some fraction * pop size
            new_trees = [copy.deepcopy(tree) for tree, _ in scored[:elite_count]] #add the best elite_count from curr pop. to next pop.

            while len(new_trees) < self.size: #keep creating offspring until population is full again
                parent1 = tournament_selection(self.trees, self.scores, tournament_size)
                parent2 = tournament_selection(self.trees, self.scores, tournament_size)
                child = crossover_with_depth_control(parent1, parent2, self.max_depth, self.variables, self.operators)
                child = mutate(child, self.max_depth, self.variables, self.operators, mutation_rate)
                new_trees.append(child) #add final child to next pop.

            self.trees = new_trees #replace old pop. with new pop.
            self.evaluate()
            
            best_tree, best_fitness, best_mse = self.best_tree()
            # print(f"Generation {gen + 1}: Fitness = {best_fitness:.4f}, True MSE = {best_mse:.4f}")
            



# #more complex target function
# def target_fn(x):
#     return math.sin(x) + math.log(x + 1) + math.sqrt(x) + 0.5 * (x ** 2)

# data_points = [{'x': x} for x in range(1, 50)]  # Avoid x = 0 for log/sqrt
# target_values = [target_fn(dp['x']) for dp in data_points]

# # Define problem parameters
# variables = ['x']
# operators = ['+', '-', '*', '/', 'sin', 'cos', 'log', 'exp', '^']
# max_depth = 10
# lambda_parsimony = 0.5

# # Initialize and evolve population
# pop = Population(
#     size=200,
#     max_depth=max_depth,
#     variables=variables,
#     operators=operators,
#     data_points=data_points,
#     target_values=target_values,
#     lambda_parsimony=lambda_parsimony
# )

# pop.evolve(generations=500, tournament_size=5, elite_fraction=0.1, mutation_rate=0.1)

# # Output best expression
# best_tree, best_fitness, best_mse = pop.best_tree()
# print("\nBest Expression Found:")
# print(best_tree)
# print("Fitness (with parsimony penalty):", best_fitness)
# print("True MSE:", best_mse)

