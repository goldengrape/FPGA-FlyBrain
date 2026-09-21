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

- **T-HW-001 Vendor toolchain preflight**：development host 上 LAB-HW-00 指定的 Vivado authoring candidate、JTAG cable driver 与 KV260 board files/board flow 通过 preflight；保存 OS、tool version、board-file/platform version 与自检输出。只有真实 KV260 dry run 通过后，candidate 才能升级为 tested/supported course baseline。
- **T-HW-002 Target discovery**：KV260 正确供电后，development host 能通过课程指定 JTAG 路径稳定枚举目标；记录 board/carrier revision 与 target identification。
- **T-HW-003 First bitstream program**：课程冻结的 clockless `kv260_marker_top` 在 `xck26-sfvc784-2LV-c` 上完成 synthesis/implementation/DRC、生成 bitstream 并通过 Vivado/JTAG 成功 program；`bank45_gpio[4:0]` 逻辑值为 `5'b10101`，使用课程冻结的 Bank 45 XDC。因为这个 proof 没有 clocked timing path，build 必须明确输出 `TIMING_CHECK=NOT_APPLICABLE_CLOCKLESS`，不能假装已经证明 timing closure。保存 timing summary、bitstream SHA-256、`xck26*` target identification、program log 与真实可见 marker observation。DS34 不作为 direct-JTAG 主 oracle。
- **T-HW-004 Physical clock/reset/I/O**：`pl_clk0`（nominal 100 MHz）驱动 `kv260_blink_core`，PS `pl_resetn0` 经 `proc_sys_reset` 生成 `peripheral_aresetn` 作为 design-local active-low reset。implemented design 必须真正存在 clock，并且存在 setup 与 hold timing path；worst setup/hold slack 都必须非负，否则 build FAIL。Bank 45 XDC 的 logical-port→package-pin mapping 必须与课程表一致，`bank45_gpio[0]` 出现周期变化且其余 marker bits 保持稳定。错误 constraint、held reset、缺失 clock、缺失 setup/hold timing path 或 negative setup/hold slack 都必须阻断 PASS。SW2 只证明 SOM-level hard reset，不自动等价于 module reset。
- **T-HW-005 PS/Linux first boot**：课程冻结的 starter Linux image 经 checksum/version 验证后写入 microSD；KV260 能通过课程指定 UART console 启动、输出 boot log 并进入 shell；development host 与 runtime host/PS 的角色可区分。撰写阶段可以记录实际下载文件的本地 SHA-256；只要 expected checksum 尚未冻结，该状态只能是 `RECORDED_UNVERIFIED`，不能满足实体 T-HW-005 PASS。为避免 authoring 阶段把学习路径逻辑卡死，若真实 boot transcript、shell、board/OS/kernel identity 与 clean shutdown evidence 已完整，可满足 LAB-HW-05 **learning progression gate** 继续 LAB-HW-06；这不改变 T-HW-005 formal acceptance 仍 blocked 的事实。
- **T-HW-006 Host↔PL loopback**：在 LAB-HW-05 learning progression gate 已满足的前提下（authoring 阶段 T-HW-005 formal acceptance 可以因 expected image hash 未冻结而继续 blocked），冻结的教学路径为 PS/Linux Python → fixed `/dev/mem` MMIO → PS `M_AXI_HPM0_FPD` → SmartConnect → `0xA0010000` dual-channel AXI GPIO。Channel 1 `GPIO_DATA`（`+0x0`）保存 32-bit host write；`kv260_loopback_transform` 计算 `(write + 1) mod 2^32`；Channel 2 `GPIO2_DATA`（`+0x8`）暴露结果。self-checker 对冻结 vectors 连续运行两轮，保存每组 write/expected/read，并必须以 `STATUS=PASS` 结束。device missing、未使用 root、OS policy/mmap failure、PL value mismatch 必须分成不同 failure class；policy failure 不得通过降低系统安全设置绕过。
- **T-HW-007 BRAM neuron-state store**：在 T-HW-006 之后，教学 state store 暴露 1024 × 32-bit word，对 PS 是 `0xA0000000` 开始的 4 KiB window。PS path 为 `M_AXI_HPM0_FPD` → SmartConnect → AXI BRAM Controller → `kv260_neuron_state_store`。native RTL read 为 synchronous read，同周期读写同一地址时教学 store 使用 read-first behavior。host self-check 向低/中/最后地址写入不同值，全部读回，再改写部分 word，并验证未改写 word 保持原值；任何 address alias 或 data mismatch 都 FAIL。Vivado synthesis/implementation evidence 必须显示至少一个 RAMB18/RAMB36 primitive；如果全部落成 LUT storage，不满足该 oracle。transport/policy failure 必须与 memory-behavior failure 分开报告。
- **T-HW-008 Small FlyBrain replay**：在 KV260 replay versioned Lesson-12 四神经元 teaching fixture。fixture 冻结 source index `[(0,2),(2,1),(3,1),(4,0)]`、records `[(1,+2),(2,+1),(3,+2),(3,+1)]`、thresholds `[99,2,1,3]`、initial accumulator `[0,0,0,0]` 与 input queue `[0]`。deterministic Python replay oracle 必须得到 spike order `[0,1,2,3]`、4 条 weighted-event record 与 final state `[0,0,0,0]`。PL readback 必须逐项匹配每个 spike、每个 encoded weighted event、event/spike count 与 final state。4 KiB state/trace window 保持 `0xA0000000`；AXI GPIO control/status 保持 `0xA0010000`。host 只允许在 `busy=0` 时访问 BRAM；concurrent host/engine arbitration 不属于本 Lab。fixture/oracle mismatch、PL differential mismatch、transport failure、engine timeout/error 必须分开。这个 oracle 验证的是 Lesson-12 teaching event machine 的 L5 replay，不宣称正式 fixed-point LIF 或 MOD-004~009 已完成。
- **T-HW-009 DDR integrity**：在真实 KV260 PS/Linux 上分配 OS-managed 64 MiB anonymous mapping，先 prefault，再按冻结 LAB-HW-09 payload algorithm 写入 deterministic contiguous 1 MiB chunk。readback 时重新生成每个 expected chunk，要求 byte-for-byte 全部一致，并且 expected/observed SHA-256 相同。CI/dry-run 必须支持 deliberate one-byte corruption，并在该情况下以 `DDR_INTEGRITY_MISMATCH` FAIL、输出 `PERFORMANCE_BLOCKED=1`，且不得给出可接受 bandwidth 结果。只有 integrity PASS 后，helper 才能报告 write/read elapsed time 与 effective bandwidth，并明确标记为包含 PS/Linux/userspace path 的 host-path observation，而不是 peak DDR 或 PL/AXI bandwidth。physical evidence 记录 board model、kernel/OS identity、MemTotal/MemAvailable/swap snapshot、access-pattern label、payload/chunk geometry、helper hash、integrity hash、timer boundary、raw elapsed time、Git commit/date。本 Lab 不需要 bitstream，也不使用 raw physical DDR address。
- **T-HW-010 AXI/burst measurement**：在真实 KV260 上使用同一个 LAB-HW-10 bitstream，其中 AMD AXI CDMA 工作于 Simple DMA mode。control interface 通过 PS `M_AXI_HPM0_FPD` 固定在 `0xA0020000`；CDMA 128-bit master、maximum burst length 64，通过 non-coherent `S_AXI_HP0_FPD` 访问 DDR。physical run 要求先通过独立 `KV260_UDMABUF_SETUP.md` prerequisite；course-approved u-dma-buf device 至少 2 MiB、以 `O_SYNC` 打开、`sync_mode` 只能为 1 或 2。helper 记录 physical base/size/sync mode，并拒绝不在 mapped `HP0_DDR_LOW` aperture 的 buffer。两种 workload 在相同 source/destination region 之间搬运同一个 deterministic 256 KiB payload：contiguous = 1 次 256 KiB request；small/scattered = frozen permutation `block=(257*i+17) mod 1024` 下的 1024 × 256-byte request。每种 pattern 都必须通过 byte-for-byte precheck 与每批之后的 post-integrity。两批 measurement 中，每批先 5 次 warm-up，再 20 次 measured repetition；timer 包含 software register programming/polling 与 DMA completion。保存所有 raw sample、median、min/max。每种 pattern 的两批 median relative difference 都必须 ≤10%；否则返回 `MEASUREMENT_UNSTABLE` 并禁止 performance conclusion。只有 integrity 与 stability 全部通过后，helper 才允许报告 contiguous/scattered median ratio。CI dry-run 只能验证 workload/statistics/failure gate，不能宣称 physical T-HW-010 PASS，也不能宣称 peak DDR/AXI bandwidth。
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
- bilingual ID consistency check：**部分自动化**；作业 Notebook 与 LAB-HW-00~10 已检查双语 cell structure/ID 一致性
- KV260 Physical Lab contract checks：**LAB-HW-00~10 已实现**；CI 检查双语 Notebook structure、冻结的 XDC/board-helper contract、LAB-HW-03/04/06/07/08 open-source RTL behavior、无需 Vivado 即可检查的 Tcl helper contract、LAB-HW-05 image/boot helper、LAB-HW-06 loopback dry-run、LAB-HW-07 BRAM-state checker、LAB-HW-08 fixture/reference/differential checker、LAB-HW-09 DDR integrity dry-run/corruption gate，以及 LAB-HW-10 u-dma-buf prerequisite dry-run、deterministic AXI-CDMA workload dry-run、integrity failure gate 与 measurement-instability gate；CI 不宣称真实 Vivado LAB-HW-08/10 build，也不宣称真实 KV260 T-HW-007~010 physical PASS

FPGA full build 不要求每次 CI 都跑，可按 checkpoint/nightly 处理。实体 KV260 的 `T-HW-*` 还必须遵守 3.2 的 physical-evidence 边界。
