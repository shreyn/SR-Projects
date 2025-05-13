import time
import math
import matplotlib.pyplot as plt

from TreeEvolution_Parsimony import Population as PopParsimony
from TreeEvolution_Canonicalize_Customv1 import Population as PopCanonCustom
from TreeEvolution_Canonicalize_SymPy import Population as PopCanonSymPy 

test_functions = {
    "x": lambda x: x,
    "x + x^2": lambda x: x + x * x,
    "x(x+1)/2": lambda x: x * (x + 1) / 2,
    "x / (x + 1)": lambda x: x / (x + 1),
    "sin(x)": lambda x: math.sin(x),
    "x * sin(x)": lambda x: x * math.sin(x),
    "x * sin(x) + x": lambda x: x * math.sin(x) + x,
    "sin(x) + sin(2x)": lambda x: math.sin(x) + math.sin(2 * x),
    "x^2 + x/2 - 3": lambda x: x * x + x / 2 - 3,
}

# canon types to test
strategies = {
    "Parsimony": PopParsimony,
    "SymPy": PopCanonSymPy,
    "Custom": PopCanonCustom
}

def run_convergence_experiment(PopClass, strat_label, fn_label, target_fn, runs=10, mse_threshold=0.001, max_generations=200):
    generations_to_converge = []
    times_to_converge = []
    print(f"\n--- Starting: Function = '{fn_label}' | Strategy = '{strat_label}' ---\n")

    for run in range(runs):
        print(f"[{strat_label}][{fn_label}] Run {run + 1}/{runs}...")

        data_points = [{'x': i} for i in range(30)]
        target_values = [target_fn(dp['x']) for dp in data_points]

        pop = PopClass(
            size=100,
            max_depth=7,
            variables=['x'],
            operators=['+', '-', '*', '/', 'sin'],
            data_points=data_points,
            target_values=target_values,
            lambda_parsimony=0.5
        )

        start_time = time.time()

        for gen in range(max_generations):
            pop.evolve(generations=1, tournament_size=5, elite_fraction=0.1, mutation_rate=0.1)
            _, _, mse = pop.best_tree()
            if mse <= mse_threshold:
                end_time = time.time()
                elapsed = end_time - start_time
                generations_to_converge.append(gen + 1)
                times_to_converge.append(elapsed)
                print(f"[{strat_label}][{fn_label}] Converged in {gen + 1} generations. Time Taken: {elapsed:.2f}s (Run {run + 1})")
                break
        else:
            end_time = time.time()
            elapsed = end_time - start_time
            generations_to_converge.append(max_generations)
            times_to_converge.append(elapsed)
            print(f"[{strat_label}][{fn_label}] Did not converge. Time Taken: {elapsed:.2f}s (Run {run + 1})")

    return generations_to_converge, times_to_converge


results = {}  # {function_label: {strategy_label: {'generations': [...], 'times': [...]}}}

for fn_label, fn in test_functions.items():
    results[fn_label] = {}
    for strat_label, PopClass in strategies.items():
        gens, times = run_convergence_experiment(PopClass, strat_label, fn_label, fn)
        results[fn_label][strat_label] = {
            "generations": gens,
            "times": times
        }

#plotting
for fn_label in test_functions.keys():
    print(f"\n📊 Plotting results for function: {fn_label}")

    labels = list(strategies.keys())

    # gens to converge
    gen_data = [results[fn_label][strat]["generations"] for strat in labels]
    plt.figure()
    plt.boxplot(gen_data, labels=labels)
    plt.title(f"Convergence Comparison (Generations) – {fn_label}")
    plt.ylabel("Generations to Reach MSE ≤ 0.001")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # time to converge
    time_data = [results[fn_label][strat]["times"] for strat in labels]
    plt.figure()
    plt.boxplot(time_data, labels=labels)
    plt.title(f"Convergence Comparison (Time) – {fn_label}")
    plt.ylabel("Time to Converge (seconds)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
