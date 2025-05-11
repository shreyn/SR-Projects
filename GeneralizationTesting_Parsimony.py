import math
from TreeEvolution_Parsimony import Population as PopParsimony
from TreeEvolution_Canonicalize import Population as PopCanonical

def test_function_convergence(PopClass, target_fn, mse_threshold=0.01, max_generations=300, runs=10):
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
            pop.evolve(generations=1, tournament_size=5, elite_fraction=0.1, mutation_rate=0.2)
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

# Target functions to test
functions_to_test = [
    (lambda x: x * (x + 1) / 2, "x(x+1)/2"),
    (lambda x: math.sin(x), "sin(x)"),
    (lambda x: x**2 + 3*x + 2, "x^2 + 3x + 2"),
    (lambda x: math.exp(-x), "exp(-x)"),
    (lambda x: 1 / (1 + math.exp(-x)), "sigmoid(x)"),
    (lambda x: math.log(x + 1), "log(x+1)"),
    (lambda x: abs(x - 5), "|x - 5|")
]

print("\n🧪 Comparing Parsimony vs Canonicalization")
print("-" * 70)
print(f"{'Function':<18} | {'Parsimony Gen':<15} | {'Canon Gen':<12} | ΔGen")
print("-" * 70)

for fn, label in functions_to_test:
    print(f"\n🔍 Testing: {label}")
    
    parsimony_results = test_function_convergence(PopParsimony, fn)
    canonical_results = test_function_convergence(PopCanonical, fn)

    ps_success, ps_avg_gen, ps_avg_mse = summarize(parsimony_results)
    ca_success, ca_avg_gen, ca_avg_mse = summarize(canonical_results)

    delta_gen = ps_avg_gen - ca_avg_gen
    delta_mse = ps_avg_mse - ca_avg_mse
    delta_success = ca_success - ps_success

    print(f"✅ Success Rate:      Parsimony = {ps_success:.1%}, Canonical = {ca_success:.1%}, Δ = {delta_success:.1%}")
    print(f"📉 Avg Generations:   Parsimony = {ps_avg_gen:.1f}, Canonical = {ca_avg_gen:.1f}, Δ = {delta_gen:.1f}")
    print(f"🎯 Avg Final MSE:     Parsimony = {ps_avg_mse:.5f}, Canonical = {ca_avg_mse:.5f}, Δ = {delta_mse:.5f}")
