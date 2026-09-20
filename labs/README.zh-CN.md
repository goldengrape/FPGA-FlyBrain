# FPGA-FlyBrain 实体 FPGA 实验

Physical Lab 是第 13–18 课的真实硬件配套路径，面向此前没有用过 FPGA 开发板、Vivado、JTAG、UART 或嵌入式 Linux 的学习者。

参考板卡：**AMD Kria KV260 Vision AI Starter Kit**。

## 当前可执行的第一批实验

| Lab | 中文 | English | 是否需要实体硬件 |
|---|---|---|---|
| LAB-HW-00 | [厂商工具链预检](zh/00_vendor_toolchain_preflight.ipynb) | [Vendor toolchain preflight](en/00_vendor_toolchain_preflight.ipynb) | 否 |
| LAB-HW-01 | [第一次认识 KV260](zh/01_board_orientation.ipynb) | [Board orientation](en/01_board_orientation.ipynb) | KV260，不上电 |
| LAB-HW-02 | [供电与目标发现](zh/02_power_target_detection.ipynb) | [Power + target detection](en/02_power_target_detection.ipynb) | KV260 + 12 V / 3 A 电源 + J4 USB data cable |
| LAB-HW-03 | [第一次生成并配置 bitstream](zh/03_first_bitstream.ipynb) | [First bitstream](en/03_first_bitstream.ipynb) | KV260 + LAB-HW-02 connection |
| LAB-HW-04 | [Clock、reset 与 physical I/O](zh/04_clock_reset_io.ipynb) | [Clock, reset, and physical I/O](en/04_clock_reset_io.ipynb) | KV260 + LAB-HW-03 passed |
| LAB-HW-05 | [第一次启动 PS/Linux + UART Console](zh/05_ps_linux_first_boot.ipynb) | [First PS/Linux boot + UART console](en/05_ps_linux_first_boot.ipynb) | KV260 + 16 GB+ microSD + J4 USB data cable + 12 V / 3 A 电源 |
| LAB-HW-06 | [真实 PS/Linux ↔ PL loopback](zh/06_host_pl_loopback.ipynb) | [Real PS/Linux ↔ PL loopback](en/06_host_pl_loopback.ipynb) | KV260 + LAB-HW-05 passed + Vivado/JTAG connection |

**LAB-HW-00~06 的教材与 CI contract 已实现。** LAB-HW-06 加入第一条 PS↔PL MMIO loopback 教学路径与 self-checking checker。LAB-HW-07~10 仍按 `docs/*/PHYSICAL_FPGA_LABS.md` 的 documentation-first contract 逐步实现；真实板卡 PASS 仍必须由对应 T-HW evidence 给出。

## Evidence 规则

“工具没有报错”不等于实验通过。每个实验必须按 `docs/*/TDD.md` 中对应的 `T-HW-*` oracle 保存证据。

云端 CI 只检查 Notebook 结构和辅助脚本，**不会**假装已经连接真实 KV260。
