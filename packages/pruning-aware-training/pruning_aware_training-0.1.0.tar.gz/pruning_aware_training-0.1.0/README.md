# Pruning Aware Training

[![Build Status](https://img.shields.io/github/actions/workflow/status/<your-username>/<your-repo-name>/tests.yml?branch=main&label=build)](https://github.com/<your-username>/<your-repo-name>/actions)
[![PyPI](https://img.shields.io/pypi/v/pruning-aware-training?color=blue)](https://pypi.org/project/pruning-aware-training/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://<your-docs-link>)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.xxxxx.svg)](https://doi.org/10.5281/zenodo.xxxxx)

---

**Pruning Aware Training (PAT)** is an open-source, easy-to-integrate framework for **structured (channel) pruning** in PyTorch.  
It enables researchers and practitioners to accelerate deep neural networks by removing redundant channels with minimal loss in task performance.

---

## 🌟 Key Features

- **Structured Channel Pruning:**  
  Removes whole channels (filters) for real acceleration and model compression.

- **Config-Driven Workflows:**  
  Define pruning behaviour entirely through JSON/YAML configuration files — reproducible and shareable.

- **Pruning-Aware Regularization:**  
  Apply channel regularization during training to promote sparsity before pruning.

- **MAC-Aware Scheduling:**  
  Automatically track and prune toward a target compute budget (e.g., 70% MAC reduction).

- **Plug-and-Play Integration:**  
  Works directly with standard PyTorch training loops and models — no need to modify architectures.

---

## 🎯 Objectives

- **Reduce Model Size:**  
  Identify and prune redundant parameters while maintaining accuracy.

- **Accelerate Inference:**  
  Lower computational cost for efficient deployment on edge devices, servers, or mobile platforms.

- **Ensure Reproducibility:**  
  Every pruning run is configuration-driven and fully logged for transparent experiments.

---

## 🧩 Repository Structure

```

PruningAwareTraining/
│
├── torch_pruning             # Core code
├────── pruning_utils.py      # Core orchestration module for initialization, regularization, and pruning
├────── pruner/               # Importance metrics and pruning algorithms (Taylor, magnitude, Hessian)
├────── load_pruned_model.py  # Allowing fluent save and load masked and pruned models
├── tests/                    # Unit and integration tests for correctness and stability
├── examples/                 # Ready-to-run scripts for different model architectures
└── reproduce/                # Documantation, Reference experiments and configuration files

````

Full documentation and examples are in  
[`Documentation/README.md`](Documentation/README.md).

---

## ⚙️ Installation

### Option 1 — Pip (recommended)
```bash
pip install git+https://github.com/AvrahamRaviv/PruningAwareTraining.git
````

### Option 2 — Local Development

```bash
git clone https://github.com/AvrahamRaviv/PruningAwareTraining.git
cd <your-repo-name>
pip install -e .
```

---

## 🚀 Quick Start

```python
from torch_pruning.pruning_utils import Pruning

# 1. Initialize the pruner
pruner = Pruning(model, output_dir="checkpoints", device=device)

# 2. Apply pruning-aware regularization after each backward pass
loss.backward()
pruner.channel_regularize(model)

# 3. Prune at scheduled epochs
for epoch in range(num_epochs):
    pruner.prune(model, epoch)
```

---

## 🧪 Example Config (JSON)

```json
{
  "start_epoch": 5,
  "end_epoch": 50,
  "interval": 5,
  "global_sparsity": 0.5,
  "mac_target": 0.7,
  "layers_to_prune": ["conv1", "layer2", "layer3"]
}
```

---
## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Please open a pull request or report issues via the [GitHub Issues](../../issues) page.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🧭 Acknowledgements

Built upon [Torch-Pruning](https://github.com/VainF/Torch-Pruning) and inspired by its DepGraph architecture.
Special thanks to collaborators and the research community for shaping this work.

---

