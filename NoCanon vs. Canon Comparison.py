import time
import matplotlib.pyplot as plt
from TreeEvolution_Parsimony import Population as PopParsimony
from TreeEvolution_Canonicalize import Population as PopCanon

def run_convergence_experiment(PopClass, label, runs=50, mse_threshold=0.01, max_generations=350):
    generations_to_converge = []

    for run in range(runs):
        print(f"[{label}] Run {run + 1}/{runs}")

        def target_fn(x): return x * (x + 1) / 2
        data_points = [{'x': i} for i in range(30)]
        target_values = [target_fn(dp['x']) for dp in data_points]

        pop = PopClass(
            size=200,
            max_depth=15,
            variables=['x'],
            operators=['+', '-', '*', '/', 'sin'],
            data_points=data_points,
            target_values=target_values,
            lambda_parsimony=0.5
        )

        for gen in range(max_generations):
            pop.evolve(generations=1, tournament_size=5, elite_fraction=0.1, mutation_rate=0.2)
            _, _, mse = pop.best_tree()
            if mse <= mse_threshold:
                generations_to_converge.append(gen + 1)
                break
        else:
            generations_to_converge.append(max_generations)  # didn't converge

    return generations_to_converge


gens_parsimony = run_convergence_experiment(PopParsimony, "Parsimony Only")
gens_canonical = run_convergence_experiment(PopCanon, "Canonicalization")


plt.boxplot([gens_parsimony, gens_canonical], labels=["Parsimony", "Canonicalization"])
plt.ylabel("Generations to Reach MSE ≤ 0.01")
plt.title("Convergence Comparison (20 Runs)")
plt.grid(True)
plt.show()
