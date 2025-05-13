# SR-Projects

This repository implements a symbolic regression (SR) system using genetic programming and tree-based expression evolution. It formalizes multiple canonicalization strategies and compares runtime, convergence, and generalization performance.

---

## Folder Structure

| Folder             | Description |
|--------------------|-------------|
| `Canonicalization/` | Canonicalization strategies |
| `Evolution/`        | Core GP algorithms |
| `SR_Setup/`         | Expression trees and random tree generation |
| `Experiments/`      | Comparison scripts |

---

## How to Run

Make sure you are in the root directory `SR-Projects/`, then use:

```bash
# Final Canonicalization strategy comparison (across many functions)
python -m Experiments.OverallCanonTesting

# Custom canonicalization evolution 
python -m Evolution.TreeEvolution_Canon_Customv1

# SymPy canonicalization evolution
python -m Evolution.TreeEvolution_Canon_SymPy

# No canonicalization
python -m Evolution.TreeEvolution
