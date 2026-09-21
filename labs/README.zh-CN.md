# FPGA-FlyBrain 实体 FPGA 实验

Physical Lab 是第 13–18 课的真实硬件配套路径，面向此前没有用过 FPGA 开发板、Vivado、JTAG、UART 或嵌入式 Linux 的学习者。

参考板卡：**AMD Kria KV260 Vision AI Starter Kit**。

## 从空白机器开始

如果这是第一次使用本仓库，不要直接跳到某个 Lab 中间。按下面顺序建立环境：

1. 按仓库根目录 `README.zh-CN.md` 安装 Git/uv、clone 仓库并执行 `uv sync`；需要用 Notebook 时注册 `fpga-flybrain` kernel。
2. LAB-HW-00 按 `zh/00_vendor_toolchain_preflight.ipynb` 安装 **Vivado 2026.1 + cable driver + KV260 board definitions**。Vivado 是上板工具，不能用 Yosys 替代。
3. LAB-HW-07/08 第一次出现 `iverilog` 前，按 `../docs/zh/HDL_TOOLCHAIN_SETUP.md` 安装/激活 OSS CAD Suite，并确认 `iverilog -V`、`vvp -V` 可运行。
4. 实体阶段至少准备 KV260、12 V / 3 A 电源、J4 USB data cable、16 GB+ microSD；HW-06 之后若使用 `scp`，再准备 J10 Ethernet 到可用网络。
5. HW-05 的 image expected SHA-256 尚未冻结时，可以在真实 boot/login/OS evidence 完整的前提下满足**学习进度 gate**继续 HW-06；这不等于正式 T-HW-005 acceptance PASS。
6. HW-09 通过后、进入 HW-10 前，必须单独完成 `../docs/zh/KV260_UDMABUF_SETUP.md` 并保存真实 u-dma-buf preflight `STATUS=PASS`。

development host（运行 Vivado/clone 仓库的电脑）与 runtime host（KV260 PS 上运行的 Ubuntu）是两台逻辑主机。课程会反复标明命令在哪一侧执行。

## 当前可执行的第一批实验

| Lab | 中文 | English | 是否需要实体硬件 |
|---|---|---|---|
| LAB-HW-00 | [厂商工具链预检](zh/00_vendor_toolchain_preflight.ipynb) | [Vendor toolchain preflight](en/00_vendor_toolchain_preflight.ipynb) | 否 |
| LAB-HW-01 | [第一次认识 KV260](zh/01_board_orientation.ipynb) | [Board orientation](en/01_board_orientation.ipynb) | KV260，不上电 |
| LAB-HW-02 | [供电与目标发现](zh/02_power_target_detection.ipynb) | [Power + target detection](en/02_power_target_detection.ipynb) | KV260 + 12 V / 3 A 电源 + J4 USB data cable |
| LAB-HW-03 | [第一次生成并配置 bitstream](zh/03_first_bitstream.ipynb) | [First bitstream](en/03_first_bitstream.ipynb) | KV260 + LAB-HW-02 connection |
| LAB-HW-04 | [Clock、reset 与 physical I/O](zh/04_clock_reset_io.ipynb) | [Clock, reset, and physical I/O](en/04_clock_reset_io.ipynb) | KV260 + LAB-HW-03 passed |
| LAB-HW-05 | [第一次启动 PS/Linux + UART Console](zh/05_ps_linux_first_boot.ipynb) | [First PS/Linux boot + UART console](en/05_ps_linux_first_boot.ipynb) | KV260 + 16 GB+ microSD + J4 USB data cable + 12 V / 3 A 电源 |
| LAB-HW-06 | [真实 PS/Linux ↔ PL loopback](zh/06_host_pl_loopback.ipynb) | [Real PS/Linux ↔ PL loopback](en/06_host_pl_loopback.ipynb) | KV260 + LAB-HW-05 operational progression gate + Vivado/JTAG connection |
| LAB-HW-07 | [BRAM neuron state / 第一次使用真实片上 RAM](zh/07_bram_neuron_state.ipynb) | [BRAM neuron state](en/07_bram_neuron_state.ipynb) | KV260 + LAB-HW-06 passed + Icarus available on development host |
| LAB-HW-08 | [Small FlyBrain replay / 小网络第一次跑在真实 FPGA](zh/08_small_flybrain_replay.ipynb) | [Small FlyBrain replay](en/08_small_flybrain_replay.ipynb) | KV260 + LAB-HW-07 passed |
| LAB-HW-09 | [DDR integrity / 第一次真实读写外部内存](zh/09_ddr_integrity.ipynb) | [DDR integrity](en/09_ddr_integrity.ipynb) | KV260 PS/Linux + LAB-HW-05 operational path；课程顺序在 LAB-HW-08 之后 |
| LAB-HW-10 | [AXI / burst measurement / 真实 PL→DDR 测量](zh/10_axi_burst_measurement.ipynb) | [AXI / burst measurement](en/10_axi_burst_measurement.ipynb) | KV260 + LAB-HW-09 integrity PASS + [Ubuntu/u-dma-buf prerequisite](../docs/zh/KV260_UDMABUF_SETUP.md) PASS |

**LAB-HW-00~10 的教材与 CI contract 已实现。** LAB-HW-10 加入第一套 PL→DDR AXI CDMA workload comparison，并带 integrity 与 reproducibility gate；真实 PASS 仍必须来自实体板 T-HW evidence。

## Evidence 规则

“工具没有报错”不等于实验通过。每个实验必须按 `docs/*/TDD.md` 中对应的 `T-HW-*` oracle 保存证据。

云端 CI 只检查 Notebook 结构和辅助脚本，**不会**假装已经连接真实 KV260。
