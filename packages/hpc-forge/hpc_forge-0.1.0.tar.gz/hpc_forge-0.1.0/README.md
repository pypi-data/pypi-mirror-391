# ⚙️ HPCTools

**HPCTools** is a lightweight, multi-purpose CLI designed to make life easier for developers, researchers, and students working with **High-Performance Computing (HPC)** environments.

It helps you quickly generate **Makefiles**, **SLURM job scripts**, and view or apply ready-made **templates** for various HPC tasks.  
Whether you’re running on clusters like **Deucalion**, **SeARCH**, or local Linux HPC setups, HPCTools saves time and reduces repetitive configuration work.

---

## 🚀 Features

| Feature | Description |
|----------|-------------|
| 🧱 **Makefile Generator** | Interactive Makefile creator with intelligent defaults for `gcc`, `clang`, `scorep`, and others |
| 🧩 **SLURM Job Script Generator** | Quickly build `.slurm` job scripts for any cluster configuration |
| 🌌 **Deucalion Mode** | Automatically loads optimized settings for the Deucalion cluster (still editable) |
| 📂 **Template Viewer** | Browse and preview all built-in templates with syntax highlighting |
| ⚙️ **Interactive Menu System** | Navigate everything via arrow-key menus powered by `questionary` |
| 🧠 **Smart Defaults** | Helpful tips, examples, and editable defaults for every prompt |
| 🧰 **Extensible Design** | Add your own templates or future modules like `doctor`, `deploy`, or `benchmark` |
| 🛠 **Roadmap** | Planned features and improvements for upcoming releases |

 

---

## 🧑‍💻 Installation

### 🧱 Local (Development Mode)
If you are cloning from GitHub:

```bash
git clone https://github.com/diogocsilva12/hpctools.git
cd hpctools
pip install -e .


MIT License © 2025 Diogo Silva - diogocsilva12
Contributions welcome — open an issue or pull request on GitHub.
