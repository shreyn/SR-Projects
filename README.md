# SR-Projects

This repository implements a symbolic regression (SR) system using genetic programming and tree-based expression evolution. It includes multiple canonicalization strategies and is designed for experiments on runtime, simplification effects, and model generalization.

---

## 📁 Folder Structure

| Folder             | Description |
|--------------------|-------------|
| `Canonicalization/` | Canonicalization strategies (e.g., custom rule-based, SymPy-based) |
| `Evolution/`        | Core GP algorithms for symbolic regression |
| `SR_Setup/`         | Expression trees and random tree generation |
| `Experiments/`      | Comparison scripts and generalization experiments |

---

## 🚀 How to Run

Make sure you are in the root directory `SR-Projects/`, then use:

```bash
# Custom canonicalization
python -m Evolution.TreeEvolution_Canon_Customv1

# SymPy canonicalization
python -m Evolution.TreeEvolution_Canon_SymPy

# No canonicalization
python -m Evolution.TreeEvolution

# Generalization testing
python -m Experiments.GeneralizationTesting

# Canon strategy comparison (rename file for convenience)
python -m Experiments.canon_comparison
