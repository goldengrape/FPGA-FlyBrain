# TDD — Check Plan / 测试与验证文档

## 0. 原则
- 先定义 oracle，再写实现。
- 不宣称测试通过，除非具体命令实际成功运行。
- Python float reference 是概念真值；Python fixed-point reference 是 RTL 直接真值。
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
固定 seed/输入事件回放；采集输出；与仿真和 Python reference 比较。

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

## 3. 性能指标
- **P-001** max clock frequency
- **P-002** synaptic events / second
- **P-003** spikes / second
- **P-004** average / 99p event latency
- **P-005** DDR bandwidth utilization
- **P-006** BRAM/URAM/DSP/LUT usage
- **P-007** power estimate / measured board power
- **P-008** real-time factor

## 4. 教学验证
每章结束要求读者能回答：
1. 本章新引入的硬件概念解决了哪个实际问题？
2. 哪个状态被保存在哪里？
3. 哪个模块定义了该行为的真值？
4. 测试失败时，优先回到模型、接口还是实现？
5. 本 slice 是否同时引入了多个尚未掌握的主要概念？如果是，必须回到 ADD/RMD 拆分。

## 5. AI 生成代码的额外规则
- AI 写 RTL 时必须同时给出接口解释和 testbench/测试向量方案。
- 关键 arithmetic 必须有 bit-level reference，不接受“看起来合理”。
- AI 修改公共接口前，先更新 MDD/TRACE。
- AI 修改模型语义前，先更新 URD/ADD/TDD，不得直接改 RTL“修好”。
- AI 声称测试、时序或性能结果时，必须附对应命令、波形、报告或 benchmark 证据。

## 6. 最小 CI（部分已实现）

当前状态：
- Python tests：**已实现**（Python exercise infrastructure）
- RTL compile：**已实现**
- fast RTL unit tests：**已实现**，含教学边界 characterization
- Verilator RTL lint：**已实现**
- Yosys synthesis sanity：**已实现**
- lint/format：**部分实现**，尚无统一 Python format/lint gate
- trace consistency check：**未实现自动化**
- bilingual ID consistency check：**未实现完整自动化**；作业 Notebook 已有双语结构/code-cell 一致性检查

FPGA full build 不要求每次 CI 都跑，可按 checkpoint/nightly 处理。
