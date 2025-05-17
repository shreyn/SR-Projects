import math
import random
from Evolution.TreeEvolution_Canon_Customv1 import Population
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

# 1. Define the target control function (nonlinear PID-style controller)
def true_control_fn(e, e_dot):
    return (
        1.5 * e                             # proportional
        - 0.6 * e_dot                       # derivative
        + 0.2 * math.sin(2 * e)            # nonlinear oscillatory response
        + 0.1 * (e ** 2)                   # quadratic term
        + 0.05 * e * e_dot                 # coupling term (state interaction)
        - 0.03 * e_dot ** 2                # penalize large velocity
    )

# 2. Generate training data (input: e, e_dot; output: control signal)
data_points = []
target_values = []

for _ in range(100): ## noisy data!
    # true input (used to generate the target output)
    e_true = random.uniform(-10, 10)
    e_dot_true = random.uniform(-10, 10)
    
    # add noise to the input values (simulate sensor error)
    e_noisy = e_true + random.gauss(0, 0.5)
    e_dot_noisy = e_dot_true + random.gauss(0, 0.5)
    
    #use true inputs to generate output (want to learn the ideal system)
    u = true_control_fn(e_true, e_dot_true)
    
    #store the noisy input and clean target
    data_points.append({'e': e_noisy, 'e_dot': e_dot_noisy})
    target_values.append(u)


# 3. Define SR parameters
variables = ['e', 'e_dot']
operators = ['+', '-', '*', '/', 'sin', '^']
max_depth = 7
lambda_parsimony = 0.1
immigration_rate = 0.05

# 4. Run symbolic regression
pop = Population(
    size=200,
    max_depth=max_depth,
    variables=variables,
    operators=operators,
    data_points=data_points,
    target_values=target_values,
    lambda_parsimony=lambda_parsimony,
    immigration_rate=immigration_rate
)

pop.evolve(
    generations=500,
    tournament_size=5,
    elite_fraction=0.1,
    mutation_rate=0.1
)

# 5. Output best result
best_tree, best_fitness, best_mse = pop.best_tree()
print("\nBest Expression Found:")
print(best_tree)
print("Fitness (with parsimony penalty):", best_fitness)
print("True MSE:", best_mse)





# 1. Create grid of input values
e_vals = np.linspace(-10, 10, 100)
e_dot_vals = np.linspace(-10, 10, 100)
E, E_DOT = np.meshgrid(e_vals, e_dot_vals)

# 2. Evaluate true control function
Z_true = np.vectorize(lambda e, edot: true_control_fn(e, edot))(E, E_DOT)

# 3. Evaluate SR-evolved function
Z_sr = np.vectorize(lambda e, edot: best_tree.evaluate({'e': e, 'e_dot': edot}))(E, E_DOT)



# 4. Plot both functions on the same 3D surface with solid colors
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(1, 1, 1, projection='3d')

# Plot true function in solid blue
ax.plot_surface(E, E_DOT, Z_true, color='blue', alpha=0.5, shade=False)

# Plot SR-generated function in solid red
ax.plot_surface(E, E_DOT, Z_sr, color='red', alpha=0.5, shade=False)

# Labels and title
ax.set_title("True vs SR Control Function")
ax.set_xlabel('e')
ax.set_ylabel('e_dot')
ax.set_zlabel('u')


legend_elements = [
    Line2D([0], [0], color='blue', lw=4, label='True Function'),
    Line2D([0], [0], color='red', lw=4, label='SR Approximation')
]
ax.legend(handles=legend_elements)

plt.tight_layout()
plt.show()



plt.figure()
plt.plot(pop.mse_history, color='green')
plt.title("MSE Over Generations")
plt.xlabel("Generation")
plt.ylabel("True MSE")
plt.grid(True)
plt.tight_layout()
plt.show()