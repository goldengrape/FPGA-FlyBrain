# FPGA-FlyBrain 实体 FPGA 实验

Physical Lab 是第 13–18 课的真实硬件配套路径，面向此前没有用过 FPGA 开发板、Vivado、JTAG、UART 或嵌入式 Linux 的学习者。

参考板卡：**AMD Kria KV260 Vision AI Starter Kit**。

## 当前可执行的第一批实验

| Lab | 中文 | English | 是否需要实体硬件 |
|---|---|---|---|
| LAB-HW-00 | [厂商工具链预检](zh/00_vendor_toolchain_preflight.ipynb) | [Vendor toolchain preflight](en/00_vendor_toolchain_preflight.ipynb) | 否 |
| LAB-HW-01 | [第一次认识 KV260](zh/01_board_orientation.ipynb) | [Board orientation](en/01_board_orientation.ipynb) | KV260，不上电 |
| LAB-HW-02 | [供电与目标发现](zh/02_power_target_detection.ipynb) | [Power + target detection](en/02_power_target_detection.ipynb) | KV260 + 12 V / 3 A 电源 + J4 USB data cable |

LAB-HW-03~10 已在 `docs/*/PHYSICAL_FPGA_LABS.md` 中冻结教学 contract；只有前一 physical checkpoint 实际验证后才继续实现。

## Evidence 规则

“工具没有报错”不等于实验通过。每个实验必须按 `docs/*/TDD.md` 中对应的 `T-HW-*` oracle 保存证据。

云端 CI 只检查 Notebook 结构和辅助脚本，**不会**假装已经连接真实 KV260。
