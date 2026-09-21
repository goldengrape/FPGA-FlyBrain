# HDL Toolchain Setup and Jupyter Launch

This guide supports the SystemVerilog/RTL labs in Lessons 6–8 and the Yosys synthesis dry run in Lesson 13. **It is not the KV260 physical-board toolchain guide.**

The physical track now freezes the **AMD Kria KV260 Vision AI Starter Kit** as the reference board. Before `LAB-HW-*`, read:
- [KV260 Reference Hardware Platform](KV260_REFERENCE_PLATFORM.md)
- [Physical FPGA Lab Teaching Standard](PHYSICAL_FPGA_LABS.md)

The Python environment remains managed by `uv`. Icarus Verilog, Verilator, Yosys, and other HDL tools are separate system tools.

## Recommended path: OSS CAD Suite

For beginners, this project recommends YosysHQ's **OSS CAD Suite**. It bundles common open-source digital-design tools such as Yosys, Icarus Verilog, and Verilator, avoiding separate installs and version combinations.

Official sources:

- https://github.com/YosysHQ/oss-cad-suite-build
- https://github.com/YosysHQ/oss-cad-suite-build/releases

Download the archive that matches your operating system and extract it.

## Linux / macOS

Assume the extracted directory is:

```text
/path/to/oss-cad-suite/
```

In the terminal you will use for the course, run:

```bash
source /path/to/oss-cad-suite/environment
```

Alternatively, add only the tool directory to `PATH`:

```bash
export PATH="/path/to/oss-cad-suite/bin:$PATH"
```

Verify the tools:

```bash
yosys -V
iverilog -V
vvp -V
verilator --version
```

All four commands should be discoverable. `iverilog` compiles the SystemVerilog simulation while `vvp` actually executes the compiled simulation, so both must be available.

### If macOS blocks downloaded executables

The official OSS CAD Suite instructions provide an `./activate` / quarantine-handling path. Follow the official installation instructions rather than disabling system security features.

## Windows

YosysHQ recommends **WSL with the linux-x64 OSS CAD Suite** for the best Windows experience.

Inside WSL, follow the Linux steps:

```bash
source /path/to/oss-cad-suite/environment
```

OSS CAD Suite also provides a native PowerShell environment script. If you choose native Windows PowerShell, run the corresponding script from the extracted suite:

```powershell
. C:\path\to\oss-cad-suite\environment.ps1
```

Then continue the course from the **same PowerShell window**.

## The easy-to-miss step: launch JupyterLab from the same activated terminal

The environment script affects only the current shell and child processes.

Use this order:

```bash
cd FPGA-FlyBrain
source /path/to/oss-cad-suite/environment

uv sync
uv run jupyter lab
```

If JupyterLab was started from a desktop launcher or another terminal where OSS CAD Suite was not activated, then inside the Notebook:

```python
shutil.which("yosys")
```

may still return `None`.

## Quick check before Lesson 13

From the repository root:

```bash
yosys -V
iverilog -V
vvp -V
verilator --version
uv run python -c "import shutil; print(shutil.which('yosys'))"
```

The second command should print a real path to `yosys`, not `None`.

### One known OSS Icarus diagnostic

With newer OSS CAD Suite / Icarus 14, the LAB-HW-08 replay engine may print a message similar to:

`constant selects in always_* processes are not fully supported`

This means Icarus is using a conservative sensitivity treatment for a function argument inside `always_comb`; it can cause extra combinational reevaluation but does not change the current fixed-replay result. The course still uses the self-checking testbench `PASS` / `$fatal` outcome as the behavioral oracle. Other compile/runtime errors must not be dismissed as this known diagnostic.

If you have already completed Lessons 6–8, you can also run the full teaching RTL check:

```bash
./scripts/check_rtl_learning.sh
```

## The Notebook still says “Yosys was not found”

Check these in order:

1. Does `yosys -V` work in the current terminal?
2. Does `uv run python -c "import shutil; print(shutil.which('yosys'))"` print a path?
3. Was JupyterLab actually launched from this terminal?
4. After changing the environment, did you stop the old Jupyter server and restart it?
5. Is the Notebook using the project's **FPGA FlyBrain** kernel?

Lesson 13 does not require a full FPGA-vendor board toolchain. Its goal is an open-source generic synthesis dry run.

## KV260 Physical Labs use a second tool layer

Starting with `LAB-HW-00~10`, the course enters the **AMD KV260 physical platform**:

- reference board: AMD Kria KV260 Vision AI Starter Kit;
- board-specific build/program uses AMD's supported **Vivado Board Flow**;
- the development host uses the KV260 JTAG/UART path for target discovery/programming;
- later runtime-host/PS and microSD/Linux steps belong to the Physical Labs rather than OSS CAD Suite.

Keep the two tool layers distinct:

```text
Lessons 6–13
  OSS CAD Suite
  → generic RTL compile/sim/lint/synthesis

LAB-HW-00~10
  AMD KV260 + Vivado/platform tools
  → target-specific implementation/timing/bitstream/program/runtime
```

LAB-HW-00 may name an **authoring candidate** Vivado version so the prose and helper scripts remain reproducible. That candidate is **not yet the tested support baseline**. Promotion to supported/tested status requires a complete real-KV260 dry run with retained physical evidence; do not infer compatibility from third-party tutorials.
