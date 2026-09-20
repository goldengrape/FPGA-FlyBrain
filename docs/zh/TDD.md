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
参考板卡为 KV260。先完成 target discovery / programming / physical I/O / host loopback 等 `T-HW-*` checkpoint，再做固定 seed/输入事件 replay；采集输出并与 RTL 仿真和 Python reference 比较。

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

- **T-HW-001 Target discovery**：KV260 正确供电后，development host 能通过课程指定 JTAG 路径稳定枚举目标；记录 board/carrier revision、tool version 与 target identification。
- **T-HW-002 First bitstream program**：批准的最小 design 能完成 implementation/timing、生成 bitstream 并成功 program；保存 artifact hash 与 PL configuration status evidence。
- **T-HW-003 Physical clock/reset/I/O**：真实 clock/reset/一个课程批准的 physical I/O 行为与 contract 一致；错误 constraint 或 held-reset 必须能被实验捕获。
- **T-HW-004 Host↔PL loopback**：runtime host 按固定 sequence 写入 PL state/operation 并读回；self-checking script 能检测错误值/错误顺序。
- **T-HW-005 BRAM neuron-state store**：多个 address 的 state write/read 正确，且 synthesis/resource report 显示预期的 on-chip memory mapping。
- **T-HW-006 Small FlyBrain replay**：固定 network image / seed / input 下，KV260 的 spike/state trace 与 Python fixed-point reference 在冻结 contract 下匹配。
- **T-HW-007 DDR integrity**：已知 payload 写入后读回，byte-for-byte 或批准 checksum 完全一致；任何 integrity failure 都阻断性能结论。
- **T-HW-008 AXI/burst measurement**：在相同 data volume 与明确 measurement window 下，至少两种 access pattern 得到可重复 latency/effective-bandwidth measurement。
- **T-HW-009 Hardware evidence manifest**：每次 physical checkpoint 记录 Git commit、board model/revision、tool version、board/platform version（能确定时）、bitstream/build hash、测试输入、输出摘要和日期。

### 3.1 Physical evidence 最低要求

“tool 没报错”不是通过标准。board test 至少需要一种直接 evidence：

- target/program log；
- physical/readable I/O observation；
- host readback；
- hardware trace；
- resource/timing report；
- differential replay report；
- DDR integrity/bandwidth measurement。

照片可以补充“真实板卡确实发生了可见变化”，但不能替代 machine-readable oracle。

### 3.2 Hardware runner / CI 边界

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
- bilingual ID consistency check：**未实现完整自动化**；作业 Notebook 已有双语结构/code-cell 一致性检查

FPGA full build 不要求每次 CI 都跑，可按 checkpoint/nightly 处理。实体 KV260 的 `T-HW-*` 还必须遵守 3.2 的 physical-evidence 边界。
