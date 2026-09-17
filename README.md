# FPGA FlyBrain

[简体中文](README.zh-CN.md)

**From membrane potential to silicon:** a learning and engineering project for life-science students to build an FPGA-based, event-driven spiking neural system constrained by the real Drosophila MaleCNS connectome.

This repository is being developed bilingually in English and Chinese. Stable engineering IDs such as `FR1`, `DP4`, `MOD-007`, `T-010`, and `RMD-013A` are shared across both languages so requirements, design, implementation, teaching, and tests remain traceable.

## North-star goal

Start from one understandable neuron model and progressively build toward a verifiable FPGA system that can load and run a spiking network derived from the MaleCNS connectome, with the host computer providing sensory input, output decoding, visualization, and experiment control.

This project does **not** claim to reproduce a complete biological fly brain or consciousness. It is a connectome-constrained computational model and a vehicle for learning AI hardware design.

## Teaching philosophy

The course is written for learners who may know basic neurophysiology but **do not already know what FPGA, LIF, RTL, FIFO, DDR, or AXI mean**.

The learning rule is:

> explain why → build intuition → define the term → run an experiment → observe → explain again

Jupyter Notebooks are treated as real textbook chapters, not thin wrappers around code. Abbreviations are expanded on first use, project traceability IDs are moved to the end of lessons, and one lesson introduces only one primary unfamiliar concept.

## Method

The project combines:

- neurophysiology → mathematical model → digital hardware translation;
- AI-assisted / vibe coding with human ownership of requirements, models, architecture, and test oracles;
- Axiomatic Design (`FR`/`DP`, coupling analysis, lower-triangular decoupled design);
- a **Learning Independence Axiom** for curriculum design;
- layered verification: Python float → Python fixed-point → RTL simulation → FPGA replay;
- Git checkpoints and end-to-end traceability.

## Quickstart / Local Setup

This project uses [uv](https://github.com/astral-sh/uv) to manage Python dependencies, the virtual environment, and the Jupyter workflow. After cloning the repository, there is no need to manually configure Conda or run individual `pip install` commands.

### 1. Synchronize Dependencies

```bash
git clone https://github.com/goldengrape/FPGA-FlyBrain
cd FPGA-FlyBrain
uv sync
```

This command automatically provisions `.venv` with all runtime libraries (`numpy`, `matplotlib`) and development/lab tooling (`jupyterlab`, `ipykernel`, `pytest`) according to `uv.lock`.

### 2. Launch JupyterLab

```bash
uv run jupyter lab
```

### 3. Register the Dedicated Kernel (Recommended)

To avoid kernel confusion inside Jupyter, install a named kernel spec:

```bash
uv run ipython kernel install --user --name fpga-flybrain --display-name "FPGA FlyBrain"
```

Once registered, select **FPGA FlyBrain** as the notebook kernel in JupyterLab.

### 4. Dependency Hygiene

- **No in-notebook installations**: Do not run `%pip install` or `!pip install` inside Notebook cells.
- **Declarative changes**: Add runtime packages via `uv add <package>` and dev tools via `uv add --dev <package>`. All changes are pinned in `pyproject.toml` and `uv.lock`.

## Start learning

The first executable lessons are in [`lessons/`](lessons/README.md):

1. [From membrane potential to a minimal computational neuron](lessons/en/01_membrane_to_lif.ipynb)
2. [How does digital hardware store 0.22?](lessons/en/02_float_to_fixed.ipynb)
3. [Why is “we both use LIF” not enough?](lessons/en/03_freeze_neuron_semantics.ipynb)
4. [How can a circuit remember the previous membrane potential?](lessons/en/04_state_and_clock.ipynb)

### Public NotebookLM course companion

If you prefer learning through narrated explanations, Q&A, and quick review, the project also has a public NotebookLM companion:

[Open FPGA FlyBrain in NotebookLM](https://notebook.google.com/notebook/ad55b316-1d40-40e6-b2fa-2beef29a5b56)

It can generate lesson audio overviews and other study materials from the course sources, and you can ask questions about the course content directly. The GitHub repository remains the primary source for notebooks, code, exercises, tests, and engineering documents; NotebookLM is a complementary learning and discussion interface.

## Documentation

### Human-facing guides
| English | 中文 |
|---|---|
| [Project Bible](docs/en/PROJECT_BIBLE.md) | [项目创作圣经](docs/zh/PROJECT_BIBLE.md) |
| [High-level Roadmap](docs/en/ROADMAP.md) | [高层学习路线](docs/zh/ROADMAP.md) |
| [Learning Architecture](docs/en/LEARNING_PATH.md) | [教学路径](docs/zh/LEARNING_PATH.md) |
| [Beginner Glossary](docs/en/GLOSSARY.md) | [初学者术语表](docs/zh/GLOSSARY.md) |

### Engineering source documents
| English | 中文 |
|---|---|
| [Idea Brief / URD](docs/en/URD.md) | [项目需求 / URD](docs/zh/URD.md) |
| [Axiomatic Design / ADD](docs/en/ADD.md) | [公理设计 / ADD](docs/zh/ADD.md) |
| [Building Blocks / MDD](docs/en/MDD.md) | [模块设计 / MDD](docs/zh/MDD.md) |
| [Check Plan / TDD](docs/en/TDD.md) | [测试验证 / TDD](docs/zh/TDD.md) |
| [Build Path / RMD](docs/en/RMD.md) | [实施路线 / RMD](docs/zh/RMD.md) |
| [Project Map / TRACE](docs/en/TRACE.md) | [追踪矩阵 / TRACE](docs/zh/TRACE.md) |

`URD/ADD/MDD/TDD/RMD/TRACE` are the engineering source of truth. The Project Bible, Roadmap, Learning Architecture, Glossary, and Notebooks explain and teach the project without replacing those specifications.

## Current status

Planning, system architecture, and the first curriculum audit are complete. The first formal implementation slice has not yet been declared complete.

Current build sequence:

1. `RMD-001` — Python LIF float reference
2. `RMD-002` — fixed-point exploration
3. `RMD-003` — freeze v0 neuron semantics
4. `RMD-003A` — Digital Hardware Bridge

Hardware purchase is intentionally deferred until the early simulation stages are understood and verified.
