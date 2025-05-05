from FitnessFunction_Canonicalization import fitness_canonicalization
from RandomTreeGeneration import generate_random_tree
from ExpressionTree import OperatorNode, tree_size
import random
import copy
from Canonicalization import canonicalize 
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

def collect_random_path(tree):
    #we can't just say "node 7"
    #we need a way to find that node starting from the root (directions to the crossover point)
    #this function gives you [0, 1, 0], which says start at root, go to child 0, then child 1, then child 0
    path = []
    while isinstance(tree, OperatorNode) and tree.children:
        idx = random.randint(0, len(tree.children) - 1)
        path.append(idx)
        tree = tree.children[idx]
    return path
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
        self.trees = [canonicalize(generate_random_tree(max_depth, variables, operators)) for _ in range(size)] ## with canonicalization!
        self.fitnessmsepairs = [fitness_canonicalization(tree, self.data_points, self.target_values) for tree in self.trees] 
        self.scores = [pair[0] for pair in self.fitnessmsepairs] #just fitness for selection

    def evaluate(self): #for recalculating fitness scores for trees (updates self.scores using latest self.trees)
        self.fitnessmsepairs = [fitness_canonicalization(tree, self.data_points, self.target_values) for tree in self.trees]
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
                child = canonicalize(child) #simplify child
                child = mutate(child, self.max_depth, self.variables, self.operators, mutation_rate)
                child = canonicalize(child) #simplify child
                new_trees.append(child) #add final child to next pop.

            self.trees = new_trees #replace old pop. with new pop.
            self.evaluate()
            
            best_tree, best_fitness, best_mse = self.best_tree()
            #print(f"Generation {gen + 1}: Fitness = {best_fitness:.4f}, True MSE = {best_mse:.4f}")
            





# # Define target function: f(x) = x(x+1)/2
# def target_fn(x):
#     return (x*(x+1)/2)

# # Generate training data
# data_points = [{'x': i} for i in range(50)]  # Inputs: x = 0 to 19
# target_values = [target_fn(dp['x']) for dp in data_points]

# # Define problem parameters
# variables = ['x']
# operators = ['+', '-', '*', '/', 'sin']
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

# pop.evolve(generations=500, tournament_size=5, elite_fraction=0.1, mutation_rate=0.2)

# # Output best expression
# best_tree, best_fitness, best_mse = pop.best_tree()
# print("\nBest Expression Found:")
# print(best_tree)
# print("Fitness (with penalty):", best_fitness)
# print("True MSE:", best_mse)

