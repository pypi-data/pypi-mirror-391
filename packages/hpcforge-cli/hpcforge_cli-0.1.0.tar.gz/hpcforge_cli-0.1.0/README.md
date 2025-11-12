# ⚙️ HPC Forge 🔥

**HPC Forge** is a powerful, lightweight CLI toolkit designed to simplify everyday tasks for developers, researchers, and students working in **High-Performance Computing (HPC)** environments.  

It helps you **generate optimized Makefiles**, **create SLURM job scripts**, and **apply pre-configured templates** for clusters like **Deucalion**, **SeARCH**, or your own local HPC setup — all interactively, from the terminal.

---

## 🚀 Features

| Feature | Description |
|----------|-------------|
| 🧱 **Makefile Generator** | Interactive creation of Makefiles with auto-optimized compiler flags for `gcc`, `clang`, and `scorep` |
| 🧩 **SLURM Job Script Generator** | Quickly build `.slurm` job scripts with dynamic runtime estimates |
| 🌌 **Deucalion Mode** | Instantly load tuned parameters for the Deucalion cluster (fully editable) |
| 📂 **Template Viewer** | Browse, preview, or apply built-in templates with syntax highlighting |
| ⚙️ **Interactive Menu System** | Clean, arrow-key-driven interface powered by `questionary` |
| 🧠 **Smart Defaults** | Context-aware recommendations and examples for each field |
| 🧰 **Extensible Design** | Modular architecture for future commands like `doctor`, `deploy`, or `benchmark` |
| 🛠 **Roadmap** | Continuous improvement toward a full HPC automation toolkit |

---

## 🧑‍💻 Installation

### 📦 From PyPI
Once published:
```bash
pip install hpcforge
