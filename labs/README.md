# FPGA-FlyBrain Physical Labs

The Physical Lab track is the real-hardware companion to Lessons 13–18. It is written for learners who may never have used an FPGA board, Vivado, JTAG, UART, or embedded Linux before.

Reference board: **AMD Kria KV260 Vision AI Starter Kit**.

## Current executable batch

| Lab | English | 中文 | Hardware required |
|---|---|---|---|
| LAB-HW-00 | [Vendor toolchain preflight](en/00_vendor_toolchain_preflight.ipynb) | [厂商工具链预检](zh/00_vendor_toolchain_preflight.ipynb) | No |
| LAB-HW-01 | [Board orientation](en/01_board_orientation.ipynb) | [第一次认识 KV260](zh/01_board_orientation.ipynb) | KV260, unpowered |
| LAB-HW-02 | [Power + target detection](en/02_power_target_detection.ipynb) | [供电与目标发现](zh/02_power_target_detection.ipynb) | KV260 + 12 V / 3 A supply + J4 USB data cable |

LAB-HW-03~10 remain specified in `docs/*/PHYSICAL_FPGA_LABS.md` and are implemented only after the preceding physical checkpoint is validated.

## Evidence rule

A hardware lab is not considered passed merely because a tool showed no error. Follow the matching `T-HW-*` oracle in `docs/*/TDD.md` and retain the evidence requested by the notebook.

Cloud CI checks notebook structure and helper scripts only. It **does not** claim that a real KV260 was present or passed.
