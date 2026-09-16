# FPGA FlyBrain

[简体中文](README.zh-CN.md)

**From membrane potential to silicon:** a learning and engineering project for life-science students to build an FPGA-based, event-driven spiking neural system constrained by the real Drosophila MaleCNS connectome.

This repository is being developed bilingually in English and Chinese. Stable engineering IDs such as `FR1`, `DP4`, `MOD-007`, `T-010`, `RMD-013A`, and `LSN-004` are shared across both languages so requirements, design, implementation, tests, and lessons remain traceable.

## North-star goal

Start from one understandable LIF neuron and progressively build toward a verifiable FPGA system that can load and run a spiking network derived from the MaleCNS connectome, with the host computer providing sensory input, output decoding, visualization, and experiment control.

This project does **not** claim to reproduce a complete biological fly brain or consciousness. It is a connectome-constrained computational model and a vehicle for learning AI hardware design.

## Method

The project combines:

- neurophysiology → mathematical model → digital hardware translation;
- AI-assisted / vibe coding with human ownership of requirements, models, architecture, and test oracles;
- Axiomatic Design (`FR`/`DP`, coupling analysis, lower-triangular decoupled design);
- a Learning Independence Axiom: one major unfamiliar concept per learning slice;
- layered verification: Python float → Python fixed-point → RTL simulation → FPGA replay;
- Git checkpoints and end-to-end traceability.

## Documentation

### Human-facing guides
| English | 中文 |
|---|---|
| [Project Bible](docs/en/PROJECT_BIBLE.md) | [项目创作圣经](docs/zh/PROJECT_BIBLE.md) |
| [High-level Roadmap](docs/en/ROADMAP.md) | [高层学习路线](docs/zh/ROADMAP.md) |
| [Learning Architecture](docs/en/LEARNING_PATH.md) | [教学路径](docs/zh/LEARNING_PATH.md) |

### Engineering source documents
| English | 中文 |
|---|---|
| [Idea Brief / URD](docs/en/URD.md) | [项目需求 / URD](docs/zh/URD.md) |
| [Axiomatic Design / ADD](docs/en/ADD.md) | [公理设计 / ADD](docs/zh/ADD.md) |
| [Building Blocks / MDD](docs/en/MDD.md) | [模块设计 / MDD](docs/zh/MDD.md) |
| [Check Plan / TDD](docs/en/TDD.md) | [测试验证 / TDD](docs/zh/TDD.md) |
| [Build Path / RMD](docs/en/RMD.md) | [实施路线 / RMD](docs/zh/RMD.md) |
| [Project Map / TRACE](docs/en/TRACE.md) | [追踪矩阵 / TRACE](docs/zh/TRACE.md) |

`URD/ADD/MDD/TDD/RMD/TRACE` are the engineering source of truth. The Project Bible, Roadmap, Learning Architecture, and Notebooks teach and explain the project without replacing those specifications.

## Executable lessons

The Notebook layer combines narrative, runnable experiments, AI tasks, human checks, and an explicit handoff into formal source code.

1. [LSN-001 — From Membrane Potential to LIF](lessons/en/01_membrane_to_lif.ipynb)
2. [LSN-002 — From Floating Point to Finite Width](lessons/en/02_float_to_fixed.ipynb)
3. [LSN-003 — Freeze Neuron Semantics](lessons/en/03_freeze_neuron_semantics.ipynb)
4. [LSN-004 — State and Clock](lessons/en/04_state_and_clock.ipynb)

See the [bilingual lesson index](lessons/README.md).

## Current status

The planning, architecture, and first teaching block are initialized. The first four bilingual executable lessons now map directly to:

1. `RMD-001` — Python LIF float reference
2. `RMD-002` — fixed-point exploration
3. `RMD-003` — freeze v0 neuron semantics
4. `RMD-003A` — Digital Hardware Bridge

The **formal implementation** of RMD-001 has not yet been declared complete. Hardware purchase is intentionally deferred until the early simulation stages are understood and verified.
