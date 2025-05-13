"""
Originally tried SymPy, was way too slow.
Now testing Customv1 (manual rules) vs. no canon (parsimony)
"""
## testing how "good" canon is, for a diverse group of functions

import math
from Evolution.TreeEvolution import Population as PopParsimony
from Evolution.TreeEvolution_Canon_Customv1 import Population as PopCanonical


def test_function_convergence(PopClass, target_fn, mse_threshold=0.01, max_generations=200, runs=20):
    results = []
    for run in range(runs):
        data_points = [{'x': i} for i in range(30)]
        target_values = [target_fn(dp['x']) for dp in data_points]

        pop = PopClass(
            size=200,
            max_depth=10,
            variables=['x'],
            operators=['+', '-', '*', '/', 'sin'],
            data_points=data_points,
            target_values=target_values,
            lambda_parsimony=0.5
        )

        for gen in range(max_generations):
            pop.evolve(generations=1, tournament_size=5, elite_fraction=0.1, mutation_rate=0.1)
            _, _, mse = pop.best_tree()
            if mse <= mse_threshold:
                results.append((True, gen + 1, mse))
                break
        else:
            _, _, final_mse = pop.best_tree()
            results.append((False, max_generations, final_mse))
    return results

def summarize(results):
    success_rate = sum(1 for success, _, _ in results if success) / len(results)
    avg_gen = sum(gen for _, gen, _ in results) / len(results)
    avg_mse = sum(mse for _, _, mse in results) / len(results)
    return success_rate, avg_gen, avg_mse

# function list (only supported ops)
functions_to_test = [
    (lambda x: x, "x"),
    (lambda x: x + 1, "x + 1"),
    (lambda x: x - 3, "x - 3"),
    (lambda x: x * x, "x^2"),
    (lambda x: x + x * x, "x + x^2"),
    (lambda x: x * (x + 1), "x(x+1)"),
    (lambda x: x * (x + 1) / 2, "x(x+1)/2"),
    (lambda x: x / (x + 1), "x/(x+1)"),
    (lambda x: math.sin(x), "sin(x)"),
    (lambda x: x + math.sin(x), "x + sin(x)"),
    (lambda x: x * math.sin(x), "x * sin(x)"),
    (lambda x: x * math.sin(x) + x, "x * sin(x) + x"),
    (lambda x: math.sin(x) + math.sin(2*x), "sin(x) + sin(2x)"),
    (lambda x: x * x + x / 2 - 3, "x^2 + x/2 - 3"),
    (lambda x: x + x + x, "x + x + x"),
    (lambda x: x + (x + (x + x)), "x + (x + (x + x))"),
    (lambda x: x - x + x, "x - x + x")
]

print("\nCanonicalization vs Parsimony")
print("-" * 60)
print(f"{'Function':<28} | {'Success Δ':<10} | {'Gen Δ':<10} | {'MSE Δ':<10}")
print("-" * 60)

for fn, label in functions_to_test:
    print(f"\nTesting: {label}")
    
    parsimony_results = test_function_convergence(PopParsimony, fn)
    canonical_results = test_function_convergence(PopCanonical, fn)

    ps_success, ps_avg_gen, ps_avg_mse = summarize(parsimony_results)
    ca_success, ca_avg_gen, ca_avg_mse = summarize(canonical_results)

    #positive deltas mean canon is better
    delta_success = ca_success - ps_success
    delta_gen = ps_avg_gen - ca_avg_gen
    delta_mse = ps_avg_mse - ca_avg_mse

    print(f"{label:<28} | {delta_success:+.2%}    | {delta_gen:+.1f}     | {delta_mse:+.5f}")
