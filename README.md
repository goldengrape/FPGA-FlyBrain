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

This project requires **Python 3.11 or newer** and uses [uv](https://github.com/astral-sh/uv) to manage Python dependencies, the virtual environment, and the Jupyter workflow. After cloning the repository, there is no need to manually configure Conda or run individual `pip install` commands.

### 1. Synchronize Dependencies

```bash
git clone https://github.com/goldengrape/FPGA-FlyBrain
cd FPGA-FlyBrain
uv sync
```

This command automatically provisions `.venv` with all runtime libraries (`numpy`, `matplotlib`) and development/lab tooling (`jupyterlab`, `ipykernel`, `pytest`) according to `uv.lock`.

### 2. Create a personal exercise copy

Do not write answers directly into the Git-tracked official templates under `exercises/en/`. Create a personal copy first:

```bash
uv run python scripts/start_exercise.py 01 --lang en
```

This creates:

```text
exercises/work/en/01_membrane_to_lif.ipynb
```

`exercises/work/` is ignored by Git, so student answers do not appear in normal `git status` / commits and do not conflict with later template updates. Existing work copies are never overwritten.

For Chinese exercises:

```bash
uv run python scripts/start_exercise.py 01
```

To create all currently available exercises:

```bash
uv run python scripts/start_exercise.py all --lang en
```

See the [exercise README](exercises/README.md) for the complete workflow.

### 3. Launch JupyterLab

```bash
uv run jupyter lab
```

When doing exercises, open your personal copy under `exercises/work/en/`; `exercises/en/` contains the official course starters.

### 4. Register the Dedicated Kernel (Required)

Exercise Notebooks, Physical Labs, and Lessons 13–23 declare the `fpga-flybrain` kernel spec. Register it before entering those materials. Earlier Lessons 1–12 still use the standard `python3` kernelspec; both kernel families should be launched from the same `uv` project environment. For notebooks that declare `fpga-flybrain`, headless execution such as `nbconvert --execute` fails with `NoSuchKernel` if the named kernel is missing.

Register the named kernel with:

```bash
uv run ipython kernel install --user --name fpga-flybrain --display-name "FPGA FlyBrain"
```

Once registered, select **FPGA FlyBrain** as the notebook kernel in JupyterLab.

### 5. Dependency Hygiene

- **No in-notebook installations**: Do not run `%pip install` or `!pip install` inside Notebook cells.
- **Declarative changes**: Add runtime packages via `uv add <package>` and dev tools via `uv add --dev <package>`. All changes are pinned in `pyproject.toml` and `uv.lock`.

### 6. HDL Toolchain for Lessons 6–8 and Lesson 13

For first-time setup, follow [HDL Toolchain Setup and Jupyter Launch](docs/en/HDL_TOOLCHAIN_SETUP.md). In particular, after activating OSS CAD Suite, launch JupyterLab from the **same terminal**.

Lessons 6–8 use **SystemVerilog-2012** for RTL and simulation, and Lesson 13 directly invokes Yosys for a real synthesis dry run. Python dependencies are managed by `uv`; HDL simulators and synthesis tools are separate system tools.

The project CI installs Icarus Verilog, Verilator, and Yosys from the GitHub Actions Ubuntu runner and prints their exact versions on every run. The baseline that has been verified end-to-end is:

- Icarus Verilog 12.0
- Verilator 5.020
- Yosys 0.33

The development VM has also been checked with the OSS CAD Suite 2026-09-18 bundle (Icarus 14.0, Verilator 5.053, Yosys 0.69).

Older Icarus 10.x installations are **not** a supported baseline for these lessons. Do not rewrite `always_ff` / `always_comb` into legacy Verilog solely to accommodate an old simulator; use a current SystemVerilog-capable toolchain instead.

To run the complete teaching RTL checks locally:

```bash
./scripts/check_rtl_learning.sh
```

This runs Icarus self-checking simulation, Verilator lint, Yosys synthesis sanity checks, and verifies that the Lesson 8 VCD waveform was actually generated. The Lesson 13 Notebook also calls Yosys directly on `rtl/learning/clocked_accumulator.sv` so learners can inspect a real synthesis report.

### 7. Physical FPGA reference board: AMD Kria KV260

The physical teaching path now freezes the **AMD Kria KV260 Vision AI Starter Kit** as the first complete reference board. Concept lessons remain board-neutral where practical, while the zero-experience Physical Lab track will give explicit KV260 steps for vendor-toolchain preflight, power, JTAG/UART, target discovery, first bitstream, constraints/I/O, PS/Linux first boot, host↔PL, BRAM, DDR, and AXI/burst measurement.

The documentation-first design is now being implemented. **LAB-HW-00~10** have bilingual student Notebooks and board-support/runtime artifacts under `boards/kv260/`; LAB-HW-10 adds the first PL→DDR AXI CDMA teaching path, deterministic contiguous-vs-small/scattered workload, integrity gate, and two-batch reproducibility oracle. Real-KV260 T-HW evidence and a real Vivado LAB-HW-10 full build remain pending.

Read:

- [KV260 Reference Hardware Platform](docs/en/KV260_REFERENCE_PLATFORM.md)
- [Physical FPGA Lab Teaching Standard](docs/en/PHYSICAL_FPGA_LABS.md)
- [Physical Lab Notebooks](labs/README.md)

The OSS CAD Suite used by Lessons 6–13 and the later AMD Vivado/platform toolchain for KV260 are intentionally separate tool layers.

## Start learning

The current executable lessons are in [`lessons/`](lessons/README.md):

1. [From membrane potential to a minimal computational neuron](lessons/en/01_membrane_to_lif.ipynb)
2. [How does digital hardware store 0.22?](lessons/en/02_float_to_fixed.ipynb)
3. [Why is “we both use LIF” not enough?](lessons/en/03_freeze_neuron_semantics.ipynb)
4. [How can a circuit remember the previous membrane potential?](lessons/en/04_state_and_clock.ipynb)
5. [What are the basic logical building blocks of a digital circuit?](lessons/en/05_logic_building_blocks.ipynb)
6. [What is RTL?](lessons/en/06_what_is_rtl.ipynb)
7. [The first RTL neuron](lessons/en/07_first_rtl_neuron.ipynb)
8. [How do we know the hardware is correct?](lessons/en/08_testbench_waveform_simulation.ipynb)
9. [How can one compute unit serve many neurons?](lessons/en/09_time_multiplex_many_neurons.ipynb)
10. [Why do spikes need a queue?](lessons/en/10_spike_fifo_backpressure.ipynb)
11. [Why not scan every synapse after every spike?](lessons/en/11_sparse_synapse_lookup.ipynb)
12. [The complete journey of one spike](lessons/en/12_one_spike_journey.ipynb)
13. [Simulation is not a chip](lessons/en/13_simulation_is_not_chip.ipynb)
14. [What is an FPGA board?](lessons/en/14_what_is_fpga_board.ipynb)
15. [How does the computer talk to the FPGA?](lessons/en/15_host_talks_to_fpga.ipynb)
16. [Why can moving data be harder than adding?](lessons/en/16_data_movement_cost.ipynb)
17. [What is external memory?](lessons/en/17_external_memory_ddr.ipynb)
18. [Learn only the AXI we need](lessons/en/18_axi_subset.ipynb)
19. [What is a connectome?](lessons/en/19_what_is_connectome.ipynb)
20. [Before loading a real MaleCNS subset: verify the network image](lessons/en/20_load_malecns_subset.ipynb)
21. [What changes when the network becomes larger?](lessons/en/21_scaling_bottlenecks.ipynb)
22. [Give the fly a world: close the loop](lessons/en/22_closed_loop_world.ipynb)
23. [Three machines, one experiment](lessons/en/23_cpu_gpu_fpga_benchmark.ipynb)

The corresponding standalone exercise workbooks are under [`exercises/`](exercises/README.md). Python exercises use Jupyter Notebooks with external graders; grading asserts and concrete test vectors are not displayed directly in the workbook.

### Public NotebookLM course companion

If you prefer learning through narrated explanations, Q&A, and quick review, the project also has a public NotebookLM companion:

[Open FPGA FlyBrain in NotebookLM](https://notebook.google.com/notebook/ad55b316-1d40-40e6-b2fa-2beef29a5b56)

It can generate lesson audio overviews and other study materials from the course sources, and you can ask questions about the course content directly. The GitHub repository remains the primary source for notebooks, code, exercises, tests, and engineering documents; NotebookLM is a complementary learning and discussion interface.

## References and further reading

These are the foundational sources currently used or repeatedly referenced by the project. This is not intended to be a complete bibliography; more specific papers and resources will be added to the corresponding notebooks as the course grows.

### Drosophila connectomics

- [Male CNS Connectome Project](https://male-cns.janelia.org/) — the primary portal for the complete adult male Drosophila central nervous system connectome, including cell-type browsing, connectivity queries, and data downloads.
- [Berg et al., *Cell* (2026): *Sexual dimorphism in the complete Drosophila male central nervous system connectome*](https://doi.org/10.1016/j.cell.2026.08.015) — the formal publication describing the MaleCNS dataset and analyses.
- [Schlegel et al., *Nature* (2024): *Whole-brain annotation and multi-connectome cell typing of Drosophila*](https://www.nature.com/articles/s41586-024-07686-5) — important background on FlyWire whole-brain annotations, cell types, and cross-connectome comparisons.

### Neuron models and computational neuroscience

- [Gerstner, Kistler, Naud & Paninski, *Neuronal Dynamics*](https://neuronaldynamics.epfl.ch/online/) — an open online text spanning single-neuron dynamics through network models; its [Integrate-and-Fire Models](https://neuronaldynamics.epfl.ch/online/Ch1.S3.html) chapter directly supports Lesson 1.

### FPGA and digital design

- [AMD FPGA Overview](https://www.amd.com/en/products/adaptive-socs-and-fpgas/fpga.html) — an entry point for FPGA architecture, devices, and terminology.
- [AMD FPGA Architecture](https://docs.amd.com/r/en-US/ug1291-viv/FPGA-Architecture) — background on programmable logic, routing, I/O, clocking, and on-chip FPGA resources.

### Design methodology

- [MIT Axiomatic Design Introduction](https://web.mit.edu/axiom/www/introduction.shtml) — background for `FR`/`DP`, the Independence Axiom, coupling analysis, and uncoupled / decoupled designs.

### Course toolchain

- [JupyterLab Documentation](https://jupyterlab.readthedocs.io/en/stable/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [pytest Documentation](https://docs.pytest.org/en/stable/)

## Documentation

### Human-facing guides
| English | 中文 |
|---|---|
| [Project Bible](docs/en/PROJECT_BIBLE.md) | [项目创作圣经](docs/zh/PROJECT_BIBLE.md) |
| [High-level Roadmap](docs/en/ROADMAP.md) | [高层学习路线](docs/zh/ROADMAP.md) |
| [Learning Architecture](docs/en/LEARNING_PATH.md) | [教学路径](docs/zh/LEARNING_PATH.md) |
| [Beginner Glossary](docs/en/GLOSSARY.md) | [初学者术语表](docs/zh/GLOSSARY.md) |
| [Exercise Notebook Design](docs/en/EXERCISE_DESIGN.md) | [作业 Notebook 设计](docs/zh/EXERCISE_DESIGN.md) |
| [HDL Toolchain Setup and Jupyter Launch](docs/en/HDL_TOOLCHAIN_SETUP.md) | [HDL 工具链安装与 Jupyter 启动](docs/zh/HDL_TOOLCHAIN_SETUP.md) |
| [KV260 Reference Hardware Platform](docs/en/KV260_REFERENCE_PLATFORM.md) | [KV260 参考硬件平台](docs/zh/KV260_REFERENCE_PLATFORM.md) |
| [Physical FPGA Lab Teaching Standard](docs/en/PHYSICAL_FPGA_LABS.md) | [实体 FPGA 实验教学规范](docs/zh/PHYSICAL_FPGA_LABS.md) |

### Engineering source documents
| English | 中文 |
|---|---|
| [Documentation-First Governance](docs/en/DOCUMENT_AUTHORITY.md) | [文档优先与规范治理](docs/zh/DOCUMENT_AUTHORITY.md) |
| [Idea Brief / URD](docs/en/URD.md) | [项目需求 / URD](docs/zh/URD.md) |
| [Axiomatic Design / ADD](docs/en/ADD.md) | [公理设计 / ADD](docs/zh/ADD.md) |
| [Building Blocks / MDD](docs/en/MDD.md) | [模块设计 / MDD](docs/zh/MDD.md) |
| [Check Plan / TDD](docs/en/TDD.md) | [测试验证 / TDD](docs/zh/TDD.md) |
| [Build Path / RMD](docs/en/RMD.md) | [实施路线 / RMD](docs/zh/RMD.md) |
| [Project Map / TRACE](docs/en/TRACE.md) | [追踪矩阵 / TRACE](docs/zh/TRACE.md) |

`docs/` is the priority source for project facts and design decisions. See [Documentation-First Governance](docs/en/DOCUMENT_AUTHORITY.md): specification changes update documentation first, then test oracles / TRACE, and only then code or RTL. Existing implementation does not become specification merely because it already runs.

`URD/ADD/MDD/TDD/RMD/TRACE` are the engineering source documents. The Project Bible, Roadmap, Learning Architecture, Glossary, and Notebooks explain and teach the project without silently replacing formal engineering contracts.

## Current status

The teaching layer now covers **LSN-001~023, their Exercise paths, and LAB-HW-00~10**. The KV260 reference board, Physical-Lab boundaries, board-support/runtime helpers, and CI contracts are all present in the repository. This means the learner path and executable teaching materials are established, but it **does not mean every formal MOD/RMD product implementation is complete, and it does not mean real-board acceptance has passed**.

Current verification state:

- Python Exercise/lesson paths are protected by automated student-flow and grader tests;
- the generic RTL path for Lessons 6–8 / 13 is checked with Icarus, Verilator, and Yosys and has been exercised in both Ubuntu CI and OSS CAD Suite environments;
- LAB-HW-00~10 notebook/helper/RTL/runtime contracts are checked by Physical Lab CI;
- real-KV260 T-HW evidence, promotion of Vivado 2026.1 to a tested/supported baseline, a controlled LAB-HW-05 image SHA-256, and the real LAB-HW-10 u-dma-buf/HP0 DDR/AXI CDMA path remain pending physical dry runs.

RMD-001~003 remain semantic/numeric prerequisites for the **formal product implementation**. The teaching track has already progressed within explicitly marked teaching-artifact boundaries, so the early instruction to defer the FPGA toolchain/hardware no longer describes the current repository. The next high-priority step is a complete real-KV260 instructor dry run, with physical results written back into TDD/TRACE and the reference-platform documentation.

## License

Unless a file or third-party dependency states otherwise, repository-authored documentation, notebooks, Python, SystemVerilog, testbenches, scripts, and other original content are licensed under the [MIT License](LICENSE).
