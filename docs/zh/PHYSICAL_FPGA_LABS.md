# PHYSICAL_FPGA_LABS — 实体 FPGA 实验教学规范

## 0. 目标

Concept Lesson 回答“为什么需要这个硬件概念、它是什么”；Physical Lab 回答“学生怎样在真实 KV260 上完成它，并留下可审查证据”。

Physical Lab 面向 **从未接触过 FPGA、嵌入式 Linux 或厂商 FPGA 工具链的学习者**。不能把 Vivado、cable driver、board file、线缆、供电、JTAG、UART、microSD、Linux boot、programming、constraint 等操作假设成常识。

参考平台见 [KV260_REFERENCE_PLATFORM.md](KV260_REFERENCE_PLATFORM.md)。

## 1. Lesson 与 Lab 的关系

```text
Concept Lesson
    ↓ 建立模型、术语、预期
Physical Lab
    ↓ 真实 setup / connection / build / program / boot / run / observe
Evidence
    ↓ report / readback / serial log / photo / hash / measurement
Human Check
    ↓ 学生解释发生了什么
Engineering Handoff
```

Physical Lab **不是**把现有 Lesson 复制一遍加上截图；它承担真实设备操作、故障定位和证据采集。

## 2. 每个 Lab 的固定结构

每份 Physical Lab 至少包含：

1. **今天桌上应该有什么**：板卡、电源、线缆、SD 卡/外围器件；
2. **开始前检查**：断电/供电、接口、电压、安全边界、所需软件版本；
3. **今天只学习一个主要新操作**；
4. **Connection Map**：使用 inline SVG + 官方接口名称标明这次真正要接的路径；
5. **Build / Program / Boot / Run**：按本 Lab 实际涉及的阶段明确分开；
6. **Expected Evidence**：成功时应该看到什么，而不是只写“无报错”；
7. **If it does not work**：按层级提供 troubleshooting tree；
8. **Human Check**：要求解释当前证据能证明什么、不能证明什么；
9. **Save Evidence**：记录 board rev、tool version、Git commit、artifact hash 与实验输出。

截图可以辅助定位 UI，但不能成为唯一规范。关键按钮/命令、输入、输出与通过标准必须有可搜索的文字版本。

## 3. 故障分层

实体实验默认按下面顺序定位，不让学生一上来改 RTL：

```text
vendor toolchain / driver / board files
  ↓
power
  ↓
physical connection / cable
  ↓
target enumeration / JTAG
  ↓
synthesis / implementation
  ↓
constraints / timing
  ↓
programming
  ↓
PS boot / UART / Linux
  ↓
runtime I/O / host transport
  ↓
FlyBrain core behavior
```

一个证据只能证明其所在层及明确关联的 contract。例如“Vivado 显示 program succeeded”不能证明 neuron algorithm 正确；“Linux 启动成功”也不能证明 PS↔PL transport 正确。

## 4. Reset 层级必须分清

KV260 上存在不同层级的 reset。课程必须明确区分：

- **SW2 / SOM reset**：board/SOM 级 hard reset；用于复位整个 SOM，不自动等于某个 SystemVerilog module 的 `rst_n`；
- **PS/platform reset**：由平台基础设施产生或分发的 reset；
- **FlyBrain design-local reset**：某个 RTL block 的逻辑 reset contract。

在 LAB-HW-04 真正冻结 design-local reset source 之前，教材不得写成“按 SW2 就等于给 neuron RTL 拉低 `rst_n`”。如果某次实验使用 SW2，只能说明它执行 SOM-level reset；若要控制局部 PL design reset，必须明确说明实际来源与极性。

## 5. KV260 Physical Lab 路径

### LAB-HW-00 — Vendor toolchain preflight / 先把开发环境准备正确

**主要新操作：** 在不上电、不写 RTL 的情况下确认厂商工具链本身可用。

学生只处理 development host：

- 使用本 Lab 指定的当前 AMD Vivado **authoring candidate** 版本；
- 安装/验证 JTAG cable driver；
- 安装/验证与该版本匹配的 KV260 board files / board flow；
- 记录 OS、Vivado version、board-file/platform version；
- 运行课程给出的版本与 board-definition 自检命令。

本 Lab 不连接板卡、不生成 bitstream、不学习 AXI。

**通过证据：** tool/version/board-definition preflight 全部通过，并保存文本输出。authoring 阶段可以先指定 candidate version，防止教材/脚本静默漂移；但只有真实 KV260 dry run 留下 evidence 后，才能把它升级为**已测试的课程支持 baseline**。

### LAB-HW-01 — Board orientation / 第一次认识 KV260

**主要新操作：** 在不上电、不写 RTL 的情况下识别实体接口。

学生必须能指出：

- K26 SOM 与 carrier card；
- J12 12 V power input；
- J4 FTDI USB UART/JTAG；
- J11 microSD；
- J10 Ethernet；
- SW2 SOM-level reset；
- 至少一种后续可用 I/O/expansion path；
- carrier revision 标识位置（以实际板卡/官方图为准）。

**通过证据：** 一张按课程模板完成的 board inventory，记录实际 carrier revision，并能说明 SW2 是 SOM reset、不是默认的 FlyBrain local RTL reset。

### LAB-HW-02 — Power + target detection / 让开发电脑看见板子

**主要新操作：** 正确供电并让已通过 LAB-HW-00 的开发工具枚举真实 target。

本 Lab 不修改 FlyBrain RTL，不学习 AXI。

学生区分：

- 12 V board power；
- J4 USB data/JTAG/UART；
- development host；
- target device。

**通过证据：** 工具能够稳定枚举目标；记录 target identification。若板未被识别，按 power → cable/JTAG → driver/tool 的路径排查，而不是改 RTL。

### LAB-HW-03 — First bitstream / 第一次配置 PL

**主要新操作：** 从一个极小、没有 clock/reset/AXI/Linux 依赖的 RTL，完整经历 synthesis → implementation → bitstream → JTAG program。

第一版教学实现现在冻结为 **Bank 45 GPIO marker**：

- top module：`kv260_marker_top`；
- logical output：`bank45_gpio[4:0]`；
- 固定逻辑 pattern：`5'b10101`；
- target part：`xck26-sfvc784-2LV-c`；
- physical mapping 使用课程提供的 `boards/kv260/constraints/bank45_gpio.xdc`；
- XDC 来源于 AMD/Xilinx Board Store 中 KV260 carrier `bank45_gpio` 的 5-bit LED-class interface，以及 K26 SOM `part0_pins.xml` 对应的 package pin mapping。

冻结的 package pins 为：

| logical bit | K26 SOM signal | package pin | I/O standard |
|---|---|---|---|
| `bank45_gpio[0]` | SOM240 D18 | J11 | LVCMOS33 |
| `bank45_gpio[1]` | SOM240 B17 | J10 | LVCMOS33 |
| `bank45_gpio[2]` | SOM240 B18 | K13 | LVCMOS33 |
| `bank45_gpio[3]` | SOM240 A15 | F11 | LVCMOS33 |
| `bank45_gpio[4]` | SOM240 C24 | A12 | LVCMOS33 |

本 Lab **不要求学生理解这些 constraint**；把 XDC 当成课程提供的 board adapter。为什么 RTL port 还需要 XDC、为什么是这些 pin，在 LAB-HW-04 再拆开讲。

build helper 输出固定目录下的 bitstream、utilization report、timing summary；program helper 只接受已经生成的 bitstream，并在 JTAG chain 中明确找到 `xck26*` device 后才 program。

**通过证据至少包括：**

- synthesis/implementation/DRC 完成；因为这个 marker 故意是 clockless，build 必须明确报告 `TIMING_CHECK=NOT_APPLICABLE_CLOCKLESS` 并保存 timing summary，而不是宣称 timing closure；
- bitstream SHA-256；
- Vivado/JTAG programming success；
- `xck26*` target identification；
- Bank 45 LED-class output 上出现稳定、可重复的 marker 状态，并记录照片/观察结果；
- 当前 Git commit 与 carrier revision。

**物理显示极性边界：** Board Store 能证明这 5 个信号属于 `bank45_gpio` LED-class output，并给出 pin mapping；在真实 KV260 dry run 之前，课程不伪造某个具体丝印 LED 的亮灭极性。学生必须记录实际可见状态；完成真实 dry run 后再把物理 designator/polarity 升级为 tested fact。

**DS34 不是通用 JTAG programming oracle。** AMD 对 DS34 的定义是 PS 成功加载 PL design 时点亮。LAB-HW-03 采用 Vivado/JTAG direct programming，因此主要证据是 Vivado/device programming status + 本设计自己的 Bank 45 observable output。

### LAB-HW-04 — Constraints + clock/reset/I/O / 逻辑 port 连接到真实世界

**主要新操作：** 在已经会生成/program bitstream 的前提下，理解 logical RTL port 怎样通过 clock/reset/platform glue 与 physical board resource 连接。

第一版教学实现冻结为 **PS clock/reset 驱动的 PL blink proof**：

- PS 只承担 platform infrastructure，不引入 Linux/AXI；
- Zynq UltraScale+ MPSoC `pl_clk0` 作为 PL clock，教学口径为 nominal 100 MHz；
- PS `pl_resetn0` 进入 `proc_sys_reset`；
- `proc_sys_reset/peripheral_aresetn` 是本设计冻结的 **design-local active-low reset**；
- `kv260_blink_core` 用 counter 分频，在 `bank45_gpio[0]` 产生肉眼可见的周期变化，其余 bits 保持 marker；
- physical output 继续复用 LAB-HW-03 的 `bank45_gpio.xdc`，这样本 Lab 只新增 clock/reset/constraint interpretation，而不是再换一套外围设备。

这里必须明确三层 reset：

1. **SW2**：SOM-level hard reset，作用于整块 SOM；
2. **PS `pl_resetn0`**：platform reset source；
3. **`peripheral_aresetn`**：经过 reset controller 同步后送入 `kv260_blink_core.resetn` 的 design-local reset。

因此可以说“SW2 会在更上游触发系统级 reset sequence”，但**不能说 SW2 就是 RTL 的 `resetn`**。

本 Lab 只教当前需要的 constraint 概念：

- logical port 没有天然 package pin；
- `PACKAGE_PIN` 把 port 连接到 K26 package；
- `IOSTANDARD LVCMOS33` 对应 Board Store 对这些 Bank 45 carrier signals 的 3.3 V 约束；
- clock 来自 PS→PL 内部 clock path，所以不为 `bank45_gpio` 伪造外部 clock constraint。

**通过证据：**

- synthesis/implementation 完成，implemented design 中真实存在 clock 与 setup/hold timing path，且 worst setup/hold slack 都非负；
- blink bitstream hash 与 program log；
- `bank45_gpio[0]` 出现周期变化、其他 marker bits 保持稳定；
- 学生能指出 XDC 中至少一个 logical bit → package pin 的 mapping；
- 学生能解释 `pl_resetn0`、`peripheral_aresetn` 与 SW2 的层级差异；
- resource/timing report、Git commit、board/carrier revision 被写入 T-HW-011 evidence manifest。



### LAB-HW-05 — PS/Linux first boot + UART console / 第一次启动 runtime host

**前置：** LAB-HW-00~04。

**主要新操作：** 让 KV260 的 PS/runtime host 独立启动起来，不同时第一次学习 PS↔PL transport。

第二阶段 authoring image 冻结为当前 AMD/Canonical 面向 Kria K26 的 Ubuntu Server image：

- distribution：**Ubuntu Server 24.04 LTS**；
- image archive：`iot-limerick-kria-classic-server-2404-classic-24.04-x07-20250423.img.xz`；
- 来源：Canonical **Install Ubuntu on AMD** / Kria K26；
- target：KV260/KR260/KD240 unified Kria image；
- microSD：16 GB UHS-1 或更大；
- 初学者写卡工具：**Raspberry Pi Imager**，与当前 AMD Kria guide 一致。

下载身份写入 `boards/kv260/runtime/ubuntu24_image.json`。仓库现在冻结 image filename/source，但**不会伪造** Canonical 可见下载目录没有发布的 upstream SHA-256。学生使用课程 helper 对实际下载的 archive 计算 SHA-256 并记录。在课程完成一次受控下载、把 expected SHA-256 升级写入 manifest 之前，可以执行 T-HW-005，但不能把 image-hash gate 宣称为 fully frozen PASS。

实体 boot path：

- microSD 插 J11；
- J4 FTDI USB 作为 UART console；
- J12 12 V / 3 A power；
- UART：**115200 baud、8 data bits、no parity、1 stop bit、no flow control**；
- Ubuntu 初始登录：`ubuntu` / `ubuntu`，首次登录按系统要求修改密码。

从上电开始保存完整 UART transcript，进入 shell 后记录：

```bash
uname -a
cat /etc/os-release
cat /proc/device-tree/model; echo
sudo xmutil boardid
sudo xmutil bootfw_status
```

Linux 成功启动不等于 custom PL 已加载；反过来，Vivado/JTAG 成功 program PL 也不等于 Linux 已启动。两条路径必须分开理解。

boot firmware 在主流程中**先观察，不把“更新固件”混成第一次 Linux boot 的必做动作**。如果当前 firmware 阻止受支持 Ubuntu image 启动，再按 AMD boot-firmware update/recovery guide 走 troubleshooting branch，并保留证据。

断电前执行：

```bash
sudo shutdown -h now
```

**通过证据：** exact image filename、实际下载 archive 的 SHA-256、写卡方法、UART settings/port、UART boot log、kernel/OS/model 输出、boot-firmware status、当前 Git commit、board/carrier revision 与 clean shutdown record。只要 course expected SHA-256 仍为 null，就不能宣称 formal image-hash PASS。

### LAB-HW-06 — Real host↔PL loopback / 真正的软件到硬件往返

**前置：** LSN-015、LAB-HW-05。

**主要新操作：** 在已经会启动 PS/Linux 的前提下，让 KV260 runtime host 控制真实 PL register path，但不把第一次 roundtrip 变成完整 AXI 课程。

LAB-HW-06 的教学 transport 冻结为最小、可检查的路径：

```text
Ubuntu/Python on PS
  → /dev/mem MMIO
  → PS M_AXI_HPM0_FPD
  → AXI SmartConnect
  → dual-channel AXI GPIO @ 0xA0010000
  → kv260_loopback_transform
```

AXI GPIO 只作为 teaching adapter，不要求学生第一次 loopback 就手写 AXI slave。本 Lab 只需要 AMD PG144 的两个 register-map 事实：

- Channel 1 `GPIO_DATA`：base + `0x0000`，配置为 32-bit output；
- Channel 2 `GPIO2_DATA`：base + `0x0008`，配置为 32-bit input。

冻结的 PL behavior：

```text
write_value = host 写 GPIO_DATA
read_value  = (write_value + 1) mod 2^32
host 从 GPIO2_DATA 读回
```

Vivado address 冻结为 **0xA0010000**；AMD/Xilinx K26 starter-kit `base_gpio_bram` reference 也把 AXI GPIO 放在这一 address region。完整 AXI channel/ordering 细节继续推迟到 Lesson 18 / LAB-HW-10。

第二阶段 deployment sequence 刻意让两个执行域保持可见：

1. PS/Linux 已通过 LAB-HW-05 启动；
2. runtime host 上如果已有 Kria application firmware active，执行 `sudo xmutil unloadapp`；
3. development host 上 build 并通过 direct JTAG program 专用 LAB-HW-06 bitstream；
4. **不要 power-cycle**，回到 PS/Linux，以 root 身份运行 `boards/kv260/runtime/loopback_mmio.py`；
5. self-checking script 对固定 vector 逐个 write/read，任何 mismatch 都 FAIL。

runtime access 使用 Python `mmap` 访问固定的 `/dev/mem` MMIO region，因为它让 software side 最小并直接暴露 MMIO boundary。这条 fixed-address path 冻结为 **LAB-HW-06 的教学 transport**，不代表后续 MOD-010 一定继续使用 `/dev/mem`；helper 不开放任意 base address。如果受支持 image 的系统策略阻止这条 MMIO path，应保存 transport failure、保持 T-HW-006 阻塞并在后续仓库修订 transport；**不能为了强行 PASS 去降低系统安全策略**。

**通过证据：** LAB-HW-06 bitstream SHA-256、build/timing reports、JTAG program log、固定 base address/register offsets、runtime script version/hash、每个 write/expected/read triple、最终 `STATUS=PASS`、Git commit、OS/image identity、board/carrier revision。第一次 MMIO read 之前的失败必须与“PL 算错了”分开分类。



### LAB-HW-07 — BRAM neuron state / 第一次使用真实片上 RAM resource

**前置：** LSN-009、LAB-HW-06，以及 LAB-HW-06 已建立的 PS/Linux runtime path。

**本 Lab 只新增一个主要操作：** 把 Lesson 9 的抽象 `state[address]` 变成 KV260 上真实、可寻址的片上 Block RAM（BRAM）state store。

先冻结教学 memory contract，再谈网络：

- state word：**32 bits**；
- depth：**1024 words**；
- logical capacity：**4096 bytes（4 KiB）**；
- word index：`0..1023`；
- PS-visible base：**`0xA0000000`**；
- state word `i` 的 byte offset：`4 * i`；
- physical path：PS `M_AXI_HPM0_FPD` → SmartConnect → AXI BRAM Controller → `kv260_neuron_state_store`；
- native memory behavior：**synchronous read**；教学 RTL 在同周期读写同一地址时采用 read-first semantics；
- implementation intent：`(* ram_style = "block" *)`，Vivado resource oracle 要求至少出现一个 RAMB18/RAMB36 primitive。

base address 沿用 AMD/Xilinx K26 `base_gpio_bram` reference 的 BRAM region：`0xA0000000`。runtime helper 继续复用 LAB-HW-06 的 fixed `/dev/mem` 教学 transport，但只映射这 4 KiB state window。

这里必须把两类 proof 分开：

1. **cycle-level proof：** SystemVerilog testbench 证明 native BRAM 是同步读；先给 address，再经过 clocked memory operation 才得到对应 read data。
2. **board-level proof：** PS/Linux 向多个 word index 写入不同 32-bit state，再通过 AXI BRAM Controller 读回。它证明“真实片上 memory 可寻址”，**不**把 Python/MMIO 的软件延迟冒充成“一个 clock cycle”。

实体 self-check 会覆盖低地址、中间地址和最后地址，再改写部分位置，并确认未改写的 neighbor state 没有被破坏。address alias、错误数据与 transport failure 必须分开分类。

本 Lab **不**加入 LAB-HW-08 的 network/spike replay，不教 DDR/performance measurement、ECC、复杂 dual-port arbitration，也不要求学生手工实例化 BRAM primitive。

**通过证据：** LAB-HW-07 bitstream SHA-256；Vivado build/program log；DRC/timing report；显示 block-RAM primitive 非零的 resource report；冻结的 base/window/word geometry；runtime helper hash；每个 address/write/read triple；rewrite + neighbor-preservation trace；最终 `STATUS=PASS`；Git commit；OS/image identity；board/carrier revision。Cloud simulation/resource-contract check 不能替代真实 T-HW-007 board evidence。

### LAB-HW-08 — Small FlyBrain replay / 小网络第一次跑在真实 FPGA

**前置：** LSN-012、LAB-HW-06、LAB-HW-07，以及 Lesson 12 已冻结的 Platform-3 teaching-event semantics。

**主要新操作：** 在 PL 中执行已经学过的四神经元 event-driven network，并把完整 trace 与 deterministic Python replay oracle 对比；不重新发明教学算法。

本 Lab 原样复用 Lesson 12 的 network：

- 4 个 neuron；
- source index：`[(0,2), (2,1), (3,1), (4,0)]`；
- synapse records：`[(1,+2), (2,+1), (3,+2), (3,+1)]`；
- thresholds：`[99, 2, 1, 3]`；
- initial accumulator state：`[0,0,0,0]`；
- initial input queue：`[0]`；
- 达到 threshold 时 target 入队，并把 teaching accumulator reset 为 0；
- expected spike order：`[0,1,2,3]`；
- expected final state：`[0,0,0,0]`。

它是 Lesson 12 的 **teaching event machine**，不是正式 LIF numeric model。因此 LAB-HW-08 不得把简单 integer-threshold semantics 冒充 `MOD-003` 或最终 `MOD-004~009`。这里的 L5 是**冻结教学网络的 board-level replay**。

冻结 replay artifact：

- versioned fixture：`boards/kv260/fixtures/lab08_four_neuron_replay_v1.json`；
- Python oracle：`boards/kv260/runtime/lab08_replay_reference.py`；
- PL engine：`kv260_small_replay_engine`；
- 共享的 4 KiB state/trace BRAM window：`0xA0000000`；
- 固定 AXI GPIO control/status：`0xA0010000`；
- host 只能在 engine 报告 `busy=0` 时访问共享 BRAM；本章不教 concurrent host/engine arbitration。

PL replay 在 BRAM 写入 machine-readable evidence：

- word `0..3`：accumulator state；
- word `16..19`：emitted spike order；
- word `20`：spike count；
- word `32..35`：weighted-event trace；
- word `36`：weighted-event count。

每个 event-trace word 编码 source、target、signed 8-bit weight、reset 前的 accumulator-after-add，以及 target 是否 spike。host checker 先从 fixture 计算 oracle，再启动 PL engine，读回 spike/state/event trace，逐字段比较。

该 fixture 完全 deterministic，不使用 PRNG。只有未来 replay contract 真正含 stochastic behavior 时 seed 才是必需项；不能为了“看起来完整”而伪造无意义 seed。

本章**不**引入 DDR、performance claim、真实 MaleCNS image、最终 LIF numerics、concurrent BRAM arbitration 或通用 programmable network loader。

**通过证据：** fixture SHA-256、Python-oracle SHA-256、bitstream SHA-256、build/program log、DRC/timing/resource report、control/status contract、完整 Python expected trace、完整 PL readback trace、differential `STATUS=PASS`、Git commit、OS/image identity、board/carrier revision。普通 CI 可以证明 oracle/RTL/host-checker 一致，但不能宣称真实 T-HW-008 PASS。

### LAB-HW-09 — DDR integrity / 第一次真实读写外部内存

**课程顺序：** LAB-HW-08 之后。  
**实际操作前置：** LSN-016、LSN-017，以及 LAB-HW-05 已工作的 PS/Linux boot path。

**主要新操作：** 在引入 PL AXI master、DMA engine 或 burst benchmark 之前，先证明 deterministic payload 能稳定经过 K26 system-memory write/read roundtrip。

KV260/K26 提供 4 GB DDR4 system memory。本 Lab 刻意使用 **PS/Linux 管理的 anonymous memory mapping**，而不是用 `/dev/mem` 猜一个物理 DDR 地址。这样 Linux 继续拥有 memory ownership，本章只新增一个大概念：external-memory integrity。

冻结 physical sanity contract：

- test allocation：**64 MiB**；
- chunk size：**1 MiB**；
- access pattern：只做 contiguous sequential chunk；
- payload：由固定 LAB-HW-09 seed string + chunk index 生成 deterministic bytes；
- timed payload write 前先 prefault pages；
- 每个 read chunk 都与重新生成的 expected chunk 做 byte-for-byte compare；
- expected / observed SHA-256 必须一致；
- 任意 mismatch 立即输出 `PERFORMANCE_BLOCKED=1`，不能接受任何 bandwidth 结论；
- physical mode 必须在 PS/Linux 上运行，并记录 board model、kernel、OS identity、`MemTotal`、`MemAvailable` 与 swap 信息；
- 不需要 root，也不需要固定 physical DDR address。

integrity 成功以后，脚本只记录两个 **host-path observation**：

- timed payload-copy write elapsed time / effective write bandwidth；
- timed contiguous read elapsed time / effective read bandwidth。

这些数字包含 PS/Linux/userspace memory path，**不是** peak DDR bandwidth、PL bandwidth、AXI burst efficiency 或 hardware-only latency。可重复 multi-pattern benchmark 留给 LAB-HW-10。

顺序强制为：

```text
verify runtime environment
→ allocate + prefault OS-managed memory
→ deterministic payload write
→ byte-for-byte readback
→ SHA-256 compare
→ integrity PASS
→ only then report host-path timing observations
```

corruption injection 只用于 CI/dry-run，证明哪怕只改一个 byte，也必须阻断 performance conclusion。

本章**不**加入 PL AXI master、AXI CDMA、DMA driver、reserved physical DDR region、random/scattered comparison、burst tuning、cache/coherency claim、DDR PHY training 或 synapse-store migration；这些属于 HW-10/RMD-015 之后。

**通过证据：** `ddr_integrity.py` SHA-256；固定 64 MiB/1 MiB geometry；payload seed/algorithm identifier；board model；kernel/OS identity；memory snapshot；expected/observed SHA-256；byte-compare result；integrity `STATUS=PASS`；write/read timer boundary 与 elapsed time；observed host-path effective bandwidth；access-pattern label；Git commit/date。本 Lab 不需要 bitstream。普通 CI dry-run 不能宣称 physical T-HW-009 PASS。

### LAB-HW-10 — AXI/burst measurement / 协议概念变成真实数据移动

**前置：** LSN-018、LAB-HW-09 integrity PASS，以及之前已经工作的 PS/Linux + JTAG programming path。

**主要新操作：** 第一次让 programmable logic 中的真实 AXI master 访问 K26 DDR，然后在同一 bitstream、同一 payload、同一 byte count、同一 buffer 与同一 timer boundary 下比较两种 transaction granularity。

本 Lab 使用 AMD AXI Central Direct Memory Access（AXI CDMA）的 **Simple DMA mode**。学生会真实使用 AXI4 master，但不要求从零手写完整 AXI master state machine。

冻结 hardware teaching path：

```text
PS/Linux
  ├─ /dev/mem control MMIO
  │    ↓
  │  PS M_AXI_HPM0_FPD
  │    ↓
  │  AXI CDMA S_AXI_LITE @ 0xA0020000
  │
  └─ DMA-safe source/destination buffer in DDR
             ↑
             │ AXI CDMA M_AXI, 128 bit, max burst 64
             │
       PS S_AXI_HP0_FPD
             │
             ↓
           DDR4
```

这里选择的 `S_AXI_HP0_FPD` 是 **non-coherent** path。因此本 Lab 不把普通 cached Python allocation 直接拿来当 DMA buffer。physical checker 要求一个 course-approved **u-dma-buf** device（`/dev/udmabuf0`，至少 2 MiB），并使用 `O_SYNC` 打开；physical address 从 driver sysfs 读取。如果选定 Ubuntu/kernel 无法提供这个 buffer/cache contract，T-HW-010 保持 blocked。不能猜 physical address，也不能为了 PASS 去降低 kernel security。

本章不教授 kernel-driver 实现。u-dma-buf 只是 buffer-provider prerequisite，角色类似 vendor toolchain：学生使用并记录它的 identity，但不修改其源代码。

冻结 AXI CDMA build contract：

- target：KV260/K26，part `xck26-sfvc784-2LV-c`；
- control path：PS `M_AXI_HPM0_FPD` → SmartConnect → AXI CDMA `S_AXI_LITE`；
- control base：**`0xA0020000`**；
- data path：AXI CDMA `M_AXI` → PS **`S_AXI_HP0_FPD`** → DDR；
- AXI CDMA：Simple DMA only，关闭 Scatter/Gather；
- data width：**128 bits**；
- maximum burst length：**64 beats**；
- address width：**64 bits**；
- DRE 关闭；课程冻结的 source/destination address 与 length 都自然对齐；
- 第一版只映射 `HP0_DDR_LOW`；physical helper 如果发现 DMA buffer 不在该 aperture，会明确 FAIL，不偷偷依赖另一套 address map；
- routed implementation 在生成 bitstream 前必须通过 DRC、setup 与 hold timing。

冻结 workload：

- DMA buffer provider：至少 **2 MiB**；
- source region offset：**0 MiB**；
- destination region offset：**1 MiB**；
- 每次 repetition payload：**256 KiB**；
- deterministic payload：SHAKE256-derived bytes；
- **contiguous pattern：** 1 次 256 KiB CDMA request；
- **small/scattered pattern：** 1024 × 256-byte CDMA request，以 deterministic permutation `block = (257*i + 17) mod 1024` 覆盖同一 256 KiB；
- performance measurement 前，以及每个 measured batch 后，destination 都必须 byte-for-byte 等于 source。

这是 **end-to-end software-controlled DMA workload comparison**。timer 包含 Python register programming/polling，以及 AXI/CDMA/DDR transfer。因此结果不是纯 bus-efficiency measurement，不能推广成 peak-DDR claim。

两种 pattern 都固定执行：

1. same bitstream、DMA buffer、payload、总 256 KiB、timer boundary；
2. pattern integrity precheck；
3. **5 次 warm-up**，不进统计；
4. **20 次 measured repetition**，保存所有 raw elapsed time；
5. **median** 作为主结果，同时保留 min/max；
6. 同一 session 再跑第二批完全相同的 5 + 20；
7. 每批结束后验证 destination integrity；
8. 分别计算两批 median 的 relative difference；
9. 两种 pattern 都必须 **≤10%** 才能称 benchmark reproducible；
10. 任一 pattern >10%，输出 `MEASUREMENT_UNSTABLE`，保留 raw evidence，但不下 performance conclusion。

只有 integrity 与 stability 两个 gate 都通过，checker 才允许报告 contiguous/scattered median ratio，而且只把它当作这个 workload 的 observation。

本章**不**加入 Scatter/Gather descriptor、interrupt、multiple outstanding master、HPC/CCI coherency tuning、cache-policy experiment、custom Linux DMA driver、手写 AXI master、正式 synapse-store migration 或 CPU/GPU/FPGA comparison。

**通过证据：** LAB-HW-10 bitstream SHA-256；Vivado build/program log；DRC/timing/resource report；AXI CDMA configuration；固定 control address；buffer-provider identity/size/physical base/cache-mode contract；deterministic payload hash；pre/post integrity evidence；全部 warm-up/measured raw sample；每种 pattern 两批 median/min/max；stability percentage；允许时的 stable ratio；helper SHA-256；Git commit；OS/kernel；board/carrier revision；experiment date。普通 CI dry-run 只验证 benchmark logic，不能宣称 physical T-HW-010 PASS。


## 6. 哪些内容故意不教

第一轮 Physical Lab 不系统教授：

- JTAG protocol 内部状态机；
- boot firmware 内部实现；
- Linux kernel/driver 开发；
- DDR PHY training；
- 完整 AXI channel/ordering/outstanding/coherency；
- Vivado 所有 IP Integrator 功能；
- floorplanning / advanced timing closure；
- clock-domain crossing 全体系。

只有 FlyBrain 实际需要并且现有抽象不足时，再增加独立 bridge lab。

## 7. 作业与验收形式

Physical Lab 不强行套用 Python grader。允许的正式作业证据包括：

- toolchain/version preflight log；
- Vivado report 解析结果；
- programming/target log；
- UART boot log；
- terminal readback；
- self-checking host script；
- hardware output trace；
- photo（只作补充证据）；
- resource/timing summary；
- bitstream/build manifest；
- differential replay report；
- bandwidth raw samples + summary。

每个 Lab 的自动化部分仍进入 CI；真正需要 KV260 的步骤放入 physical checkpoint / hardware runner，不伪造普通 CI 的“板上通过”。

## 8. 文档优先实现顺序

本轮先完成：

1. URD / ADD / LEARNING_PATH / ROADMAP；
2. RMD / MDD / TDD / TRACE；
3. KV260 reference platform 与本 Lab 规范。

之后才允许：

4. 编写 `labs/zh/`、`labs/en/`；
5. 在 LAB-HW-00/02/03/05/06 prose 中冻结具体 Vivado version、board files、pin/constraint、starter Linux image 与 host transport；
6. 写 `boards/kv260/`、RTL/platform scripts；
7. 在真实 KV260 上逐 Lab dry run；
8. 将可自动化部分加入 CI。

没有完成对应文档与 oracle 的 Lab，不进入 board-specific implementation。
