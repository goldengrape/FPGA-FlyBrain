# HDL 工具链安装与 Jupyter 启动

这份说明服务于第 6–8 课的 SystemVerilog/RTL 实验，以及第 13 课的 Yosys synthesis dry run。**它不是 KV260 实体上板工具链说明。**

实体板课程已经冻结参考板卡为 **AMD Kria KV260 Vision AI Starter Kit**。进入 `LAB-HW-*` 前先阅读：
- [KV260 参考硬件平台](KV260_REFERENCE_PLATFORM.md)
- [实体 FPGA 实验教学规范](PHYSICAL_FPGA_LABS.md)

Python 环境仍由 `uv` 管理；Icarus Verilog、Verilator、Yosys 等 HDL 工具是独立的系统工具。

## 推荐路径：OSS CAD Suite

本项目推荐初学者使用 YosysHQ 的 **OSS CAD Suite**。它把 Yosys、Icarus Verilog、Verilator 等常用开源数字设计工具打包在一起，避免学生分别安装并处理版本组合。

官方入口：

- https://github.com/YosysHQ/oss-cad-suite-build
- https://github.com/YosysHQ/oss-cad-suite-build/releases

下载与你的操作系统匹配的压缩包并解压。

## Linux / macOS

假设解压后目录为：

```text
/path/to/oss-cad-suite/
```

在准备运行课程的终端中执行：

```bash
source /path/to/oss-cad-suite/environment
```

或者只把工具目录加入 `PATH`：

```bash
export PATH="/path/to/oss-cad-suite/bin:$PATH"
```

然后验证：

```bash
yosys -V
iverilog -V
verilator --version
```

至少应当能找到这三个命令。

### macOS 下载文件不能执行时

OSS CAD Suite 官方说明提供了 `./activate` / quarantine 处理方式。遇到 macOS 阻止执行时，按官方安装说明处理，不要关闭系统安全功能。

## Windows

YosysHQ 对 Windows 的推荐体验是使用 **WSL + linux-x64 OSS CAD Suite**。

在 WSL 中按 Linux 步骤执行：

```bash
source /path/to/oss-cad-suite/environment
```

OSS CAD Suite 也提供原生 PowerShell 环境脚本。若选择原生 Windows PowerShell，可在解压目录对应位置执行：

```powershell
. C:\path\to\oss-cad-suite\environment.ps1
```

然后在**同一个 PowerShell 窗口**中继续启动课程。

## 最容易漏掉的一步：从同一个终端启动 JupyterLab

环境脚本只影响当前 shell 及其子进程。

因此正确顺序是：

```bash
cd FPGA-FlyBrain
source /path/to/oss-cad-suite/environment

uv sync
uv run jupyter lab
```

如果先从桌面图标或另一个没有激活 OSS CAD Suite 的终端启动 JupyterLab，那么 Notebook 中：

```python
shutil.which("yosys")
```

仍然可能得到 `None`。

## 第 13 课之前的快速自检

从仓库根目录执行：

```bash
yosys -V
uv run python -c "import shutil; print(shutil.which('yosys'))"
```

第二条命令应打印一个实际的 `yosys` 路径，而不是 `None`。

如果已经学完第 6–8 课，也可以运行完整 RTL 教学检查：

```bash
./scripts/check_rtl_learning.sh
```

## Notebook 仍然显示 “没有找到 Yosys”

依次检查：

1. 当前终端直接运行 `yosys -V` 是否成功；
2. 当前终端运行 `uv run python -c "import shutil; print(shutil.which('yosys'))"` 是否得到路径；
3. JupyterLab 是否确实从这个终端启动；
4. 修改环境后，是否关闭旧的 Jupyter server 并重新启动；
5. Notebook 是否选择了项目的 **FPGA FlyBrain** kernel。

Lesson 13 不要求安装 FPGA 厂商的完整板卡工具链。它的目标只是做一次开源 generic synthesis dry run。

## KV260 Physical Lab 使用另一套工具层

从 `LAB-HW-00~08` 开始，课程进入 **AMD KV260 实体平台**：

- reference board：AMD Kria KV260 Vision AI Starter Kit；
- board-specific build/program 使用 AMD 官方支持的 **Vivado Board Flow**；
- development host 通过 KV260 的 JTAG/UART 路径进行 target discovery / programming；
- 后续 runtime host/PS 路径与 microSD/Linux 属于 Physical Lab，而不是 OSS CAD Suite 的职责。

这两套工具不要混淆：

```text
Lessons 6–13
  OSS CAD Suite
  → generic RTL compile/sim/lint/synthesis

LAB-HW-00~08
  AMD KV260 + Vivado/platform tools
  → target-specific implementation/timing/bitstream/program/runtime
```

本次 documentation-first 修订**尚未冻结具体 Vivado 版本**。具体支持版本要在写 LAB-HW-01/02 prose 时，用真实 KV260 完整 dry run 后再写入课程；在此之前不要根据网络教程猜测版本兼容性。
