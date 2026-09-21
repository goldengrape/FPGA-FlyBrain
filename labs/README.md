# FPGA-FlyBrain Physical Labs

The Physical Lab track is the real-hardware companion to Lessons 13–18. It is written for learners who may never have used an FPGA board, Vivado, JTAG, UART, or embedded Linux before.

Reference board: **AMD Kria KV260 Vision AI Starter Kit**.

## Current executable batch

| Lab | English | 中文 | Hardware required |
|---|---|---|---|
| LAB-HW-00 | [Vendor toolchain preflight](en/00_vendor_toolchain_preflight.ipynb) | [厂商工具链预检](zh/00_vendor_toolchain_preflight.ipynb) | No |
| LAB-HW-01 | [Board orientation](en/01_board_orientation.ipynb) | [第一次认识 KV260](zh/01_board_orientation.ipynb) | KV260, unpowered |
| LAB-HW-02 | [Power + target detection](en/02_power_target_detection.ipynb) | [供电与目标发现](zh/02_power_target_detection.ipynb) | KV260 + 12 V / 3 A supply + J4 USB data cable |
| LAB-HW-03 | [First bitstream](en/03_first_bitstream.ipynb) | [第一次生成并配置 bitstream](zh/03_first_bitstream.ipynb) | KV260 + LAB-HW-02 connection |
| LAB-HW-04 | [Clock, reset, and physical I/O](en/04_clock_reset_io.ipynb) | [Clock、reset 与 physical I/O](zh/04_clock_reset_io.ipynb) | KV260 + LAB-HW-03 passed |
| LAB-HW-05 | [First PS/Linux boot + UART console](en/05_ps_linux_first_boot.ipynb) | [第一次启动 PS/Linux + UART Console](zh/05_ps_linux_first_boot.ipynb) | KV260 + 16 GB+ microSD + J4 USB data cable + 12 V / 3 A supply |
| LAB-HW-06 | [Real PS/Linux ↔ PL loopback](en/06_host_pl_loopback.ipynb) | [真实 PS/Linux ↔ PL loopback](zh/06_host_pl_loopback.ipynb) | KV260 + LAB-HW-05 passed + Vivado/JTAG connection |
| LAB-HW-07 | [BRAM neuron state](en/07_bram_neuron_state.ipynb) | [BRAM neuron state / 第一次使用真实片上 RAM](zh/07_bram_neuron_state.ipynb) | KV260 + LAB-HW-06 passed |
| LAB-HW-08 | [Small FlyBrain replay](en/08_small_flybrain_replay.ipynb) | [Small FlyBrain replay / 小网络第一次跑在真实 FPGA](zh/08_small_flybrain_replay.ipynb) | KV260 + LAB-HW-07 passed |
| LAB-HW-09 | [DDR integrity](en/09_ddr_integrity.ipynb) | [DDR integrity / 第一次真实读写外部内存](zh/09_ddr_integrity.ipynb) | KV260 PS/Linux + LAB-HW-05 operational path; course sequence after LAB-HW-08 |
| LAB-HW-10 | [AXI / burst measurement](en/10_axi_burst_measurement.ipynb) | [AXI / burst measurement / 真实 PL→DDR 测量](zh/10_axi_burst_measurement.ipynb) | KV260 + LAB-HW-09 integrity PASS + DMA-safe buffer prerequisite |

**LAB-HW-00~10 now have implemented prose and CI contracts.** LAB-HW-10 adds the first PL→DDR AXI CDMA workload comparison with integrity and reproducibility gates. Physical PASS still requires real-board T-HW evidence. A physical PASS still requires the corresponding T-HW evidence from a real board.

## Evidence rule

A hardware lab is not considered passed merely because a tool showed no error. Follow the matching `T-HW-*` oracle in `docs/*/TDD.md` and retain the evidence requested by the notebook.

Cloud CI checks notebook structure and helper scripts only. It **does not** claim that a real KV260 was present or passed.
