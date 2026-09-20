# TDD — Check Plan / 测试与验证文档

## 0. 原则
- 遵守 [文档优先与规范治理](DOCUMENT_AUTHORITY.md)：先有批准的需求/语义/接口 contract，再把它翻译成 oracle，最后写实现。
- 先定义 oracle，再写实现。
- 不宣称测试通过，除非具体命令实际成功运行。
- 在对应模型语义已经冻结的前提下，Python float reference 是概念 oracle；Python fixed-point reference 是 RTL 直接 oracle。reference model 本身也必须追随已批准的文档 contract。
- 单元测试、集成测试、性能测试分开。

## 1. 验证层级
### L0 数学/生理 sanity checks
验证：无输入时衰减、持续输入时积累、过阈值 spike、reset/refractory 行为。

### L1 Python float reference
确定性输入下验证状态轨迹和 spike timestamp。

### L2 Python fixed-point reference
测试：
- quantization error
- overflow/saturation
- 不同 Q-format 对 spike timing 的影响

通过标准：选定 Q-format 后，在预设测试集上误差可接受，且无未定义 overflow。

### L3 RTL unit simulation
模块：`lif_neuron_engine`、FIFO、`synapse_reader`、`synapse_engine`、accumulator。  
Oracle：Python fixed-point vectors 或直接构造 expected values。

### L4 RTL integration simulation
场景：10–1000 neurons 小网络。  
比较：逐 step/event 的 spike sequence；必要时比较 neuron-state checksum。

### L5 FPGA board verification
参考板卡为 KV260。先完成 vendor toolchain preflight / target discovery / programming / physical I/O / PS/Linux boot / host loopback 等 `T-HW-*` checkpoint，再做固定 seed/输入事件 replay；采集输出并与 RTL 仿真和 Python reference 比较。

### L6 Connectome subset verification
选择约 1K 真实神经元子图；同一 binary image 同时供软件和 FPGA 使用。

### L7 Full-scale performance / correctness
- 166.7K 级神经元目标
- 全连接表装载
- 长时间运行稳定性
- output statistics 与 software baseline 对比

## 2. 关键 test oracle
- **T-001** LIF no-input decay
- **T-002** threshold crossing
- **T-003** reset after spike
- **T-004** refractory behavior
- **T-005** signed excitatory/inhibitory weight
- **T-006** fixed-point saturation
- **T-007** FIFO ordering
- **T-008** FIFO backpressure
- **T-009** source index → exact synapse range
- **T-010** synapse stream ordering/last marker
- **T-011** target accumulation correctness
- **T-012** small network known spike sequence
- **T-013** random seeded network differential test
- **T-014** DDR image checksum + manifest match
- **T-015** real subset differential test
- **T-016** full-system replay determinism；如模型含噪声则固定 PRNG seed

## 3. KV260 实体板 checkpoint

这些 `T-HW-*` 是 physical-lab oracle，不替代 T-001~T-016 的模型/算法正确性测试。普通云 CI 没有实体 KV260 时，不得把它们标成通过。

- **T-HW-001 Vendor toolchain preflight**：development host 上课程冻结的 Vivado、JTAG cable driver 与 KV260 board files/board flow 可用；保存 OS、tool version、board-file/platform version 与自检输出。
- **T-HW-002 Target discovery**：KV260 正确供电后，development host 能通过课程指定 JTAG 路径稳定枚举目标；记录 board/carrier revision 与 target identification。
- **T-HW-003 First bitstream program**：课程冻结的 clockless `kv260_marker_top` 在 `xck26-sfvc784-2LV-c` 上完成 synthesis/implementation/DRC、生成 bitstream 并通过 Vivado/JTAG 成功 program；`bank45_gpio[4:0]` 逻辑值为 `5'b10101`，使用课程冻结的 Bank 45 XDC。因为这个 proof 没有 clocked timing path，build 必须明确输出 `TIMING_CHECK=NOT_APPLICABLE_CLOCKLESS`，不能假装已经证明 timing closure。保存 timing summary、bitstream SHA-256、`xck26*` target identification、program log 与真实可见 marker observation。DS34 不作为 direct-JTAG 主 oracle。
- **T-HW-004 Physical clock/reset/I/O**：`pl_clk0`（nominal 100 MHz）驱动 `kv260_blink_core`，PS `pl_resetn0` 经 `proc_sys_reset` 生成 `peripheral_aresetn` 作为 design-local active-low reset。implemented design 必须真正存在 clock 和至少一条 setup timing path；worst setup slack 必须非负，否则 build FAIL。Bank 45 XDC 的 logical-port→package-pin mapping 必须与课程表一致，`bank45_gpio[0]` 出现周期变化且其余 marker bits 保持稳定。错误 constraint、held reset、缺失 clock、没有 setup timing path 或 negative setup slack 都必须阻断 PASS。SW2 只证明 SOM-level hard reset，不自动等价于 module reset。
- **T-HW-005 PS/Linux first boot**：课程冻结的 starter Linux image 经 checksum/version 验证后写入 microSD；KV260 能通过课程指定 UART console 启动、输出 boot log 并进入 shell；development host 与 runtime host/PS 的角色可区分。
- **T-HW-006 Host↔PL loopback**：在 T-HW-005 已通过的前提下，runtime host 按固定 sequence 写入 PL state/operation 并读回；self-checking script 能检测错误值/错误顺序，并区分 Linux/transport failure 与 core-behavior failure。
- **T-HW-007 BRAM neuron-state store**：多个 address 的 state write/read 正确，且 synthesis/resource report 显示预期的 on-chip memory mapping。
- **T-HW-008 Small FlyBrain replay**：固定 network image / seed / input 下，KV260 的 spike/state trace 与 Python fixed-point reference 在冻结 contract 下匹配。
- **T-HW-009 DDR integrity**：已知 payload 写入后读回，byte-for-byte 或批准 checksum 完全一致；任何 integrity failure 都阻断性能结论。
- **T-HW-010 AXI/burst measurement**：在相同 bitstream、data volume、payload 与 measurement boundary 下，每种 access pattern 先做 5 次 warm-up，再至少做 20 次 measured repetitions；主结果取 median，并保存全部 raw samples 与 min/max。同一 session 的第二批 measurement 与第一批 median 相对差异应 ≤10%；否则标记为 `measurement unstable`，不得下性能结论。
- **T-HW-011 Hardware evidence manifest**：每次 physical checkpoint 显式记录 Git commit、board model/revision、development-host OS、tool version、board/platform version（能确定时）、Linux image/version（涉及 PS boot 时）、适用时的 bitstream SHA-256 和/或 build hash、测试输入、输出摘要、保留 artifact path 与日期；这些必须是 manifest 的明确字段，不能只藏在 free-form notes 中。

### 3.1 Physical evidence 最低要求

“tool 没报错”不是通过标准。board test 至少需要一种直接 evidence：

- toolchain/version preflight log；
- target/program log；
- UART boot log；
- physical/readable I/O observation；
- host readback；
- hardware trace；
- resource/timing report；
- differential replay report；
- DDR integrity/bandwidth raw samples + summary。

照片可以补充“真实板卡确实发生了可见变化”，但不能替代 machine-readable oracle。

### 3.2 Performance measurement 默认协议

除非某个 Lab 用真实数据证明需要更严格协议，否则板上性能比较默认：

1. 先通过 correctness / integrity oracle；
2. 固定 bitstream、data volume、payload 和计时边界；
3. 5 次 warm-up 不入统计；
4. 每种 pattern 至少 20 次测量；
5. 报告 median 为主值，同时保存原始样本和 min/max；
6. 同一 session 重复一批 measurement；两批 median 的相对差异 ≤10% 才可称“可重复”；
7. 明确说明计时是否包含 host/software overhead。

若第 6 条不满足，结果只能报告为不稳定 observation，不能支持“更快/更慢”的工程结论。

### 3.3 Hardware runner / CI 边界

- 不要求每个普通 CI commit 都跑完整 Vivado + 实体板。
- 可自动化的 HDL、report parser、host self-check script 进入普通 CI。
- 真正需要 KV260 的 `T-HW-*` 由人工 physical checkpoint 或受控 hardware runner 执行。
- PR/文档不得使用“board verified”字样，除非对应 physical evidence 实际存在并指向具体 commit/artifact。

## 4. 性能指标
- **P-001** max clock frequency
- **P-002** synaptic events / second
- **P-003** spikes / second
- **P-004** average / 99p event latency
- **P-005** DDR bandwidth utilization
- **P-006** BRAM/URAM/DSP/LUT usage
- **P-007** power estimate / measured board power
- **P-008** real-time factor

## 5. 教学验证
每章结束要求读者能回答：
1. 本章新引入的硬件概念解决了哪个实际问题？
2. 哪个状态被保存在哪里？
3. 哪个模块定义了该行为的真值？
4. 测试失败时，优先回到模型、接口还是实现？
5. 本 slice 是否同时引入了多个尚未掌握的主要概念？如果是，必须回到 ADD/RMD 拆分。

## 6. AI 生成代码的额外规则
- AI 写 RTL 时必须同时给出接口解释和 testbench/测试向量方案。
- 关键 arithmetic 必须有 bit-level reference，不接受“看起来合理”。
- AI 修改公共接口前，先更新 MDD/TRACE。
- AI 修改模型语义前，先更新 URD/ADD/TDD，不得直接改 RTL“修好”。
- AI 声称测试、时序或性能结果时，必须附对应命令、波形、报告或 benchmark 证据。

## 7. 最小 CI（部分已实现）

当前状态：
- Python tests：**已实现**（Python exercise infrastructure）
- RTL compile：**已实现**
- fast RTL unit tests：**已实现**，含教学边界 characterization
- Verilator RTL lint：**已实现**
- Yosys synthesis sanity：**已实现**
- lint/format：**部分实现**，尚无统一 Python format/lint gate
- trace consistency check：**未实现自动化**
- bilingual ID consistency check：**部分自动化**；作业 Notebook 与 LAB-HW-00~04 已检查双语 cell structure/ID 一致性
- KV260 Physical Lab contract checks：**LAB-HW-00~04 已实现**；CI 检查双语 Notebook structure、冻结的 XDC/board-helper contract、LAB-HW-03/04 open-source RTL behavior，以及无需 Vivado 即可执行的 Tcl helper path；不宣称真实板卡验证或真实 Vivado full build 已通过

FPGA full build 不要求每次 CI 都跑，可按 checkpoint/nightly 处理。实体 KV260 的 `T-HW-*` 还必须遵守 3.2 的 physical-evidence 边界。
