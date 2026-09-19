# GLOSSARY — 初学者术语表

这是一份备查表，不替代 Notebook 中的首次解释。课程正文第一次出现缩写时，仍必须写出全称并用白话说明。

| 术语 | 全称 | 白话解释 |
|---|---|---|
| FPGA | 现场可编程门阵列（Field-Programmable Gate Array） | 一种可以在制造完成后按设计重新配置内部数字电路的芯片。它不是“跑程序的 CPU”那么简单，而是能把我们的逻辑结构真正变成并行硬件。 |
| LIF | 漏电积分发放模型（Leaky Integrate-and-Fire） | 一种简化神经元模型：状态会衰减，输入会累积，超过阈值时产生一次 spike，然后按规则复位。 |
| SNN | 脉冲神经网络（Spiking Neural Network） | 用离散 spike 事件传递信息的一类神经网络。 |
| bit | binary digit，二进制位 | 数字系统中最小的信息单位，通常取 0 或 1。 |
| floating point | 浮点数 | 用类似“有效数字 + 指数”的方式表示很大范围数值的有限精度格式。Python 常用 `float` 通常是 64 位二进制浮点数。 |
| fixed point | 定点数 | 小数点位置固定的有限位宽数值表示，硬件实现简单、可控。 |
| quantization | 量化 | 把连续或高精度数值映射到有限的一组离散数值。 |
| rounding | 舍入 | 当数值落在两个可表示值之间时，决定取哪个值的规则。 |
| overflow | 溢出 | 计算结果超出当前位宽能表示的范围。 |
| saturation | 饱和 | 溢出时把数值限制在最大或最小可表示值，而不是让它绕回另一端。 |
| register | 寄存器 | 能在时钟控制下保存少量数字状态的硬件结构。 |
| clock | 时钟 | 周期性信号，用来约定同步数字电路在什么时候更新状态。 |
| clock edge | 时钟边沿 | 时钟从低到高或从高到低的瞬间；很多寄存器在指定边沿更新。 |
| combinational logic | 组合逻辑 | 输出只由当前输入决定、不负责记忆过去状态的电路。 |
| sequential logic | 时序逻辑 | 输出/行为与过去保存的状态有关的电路。 |
| RAM | 随机存取存储器（Random-Access Memory） | 通过地址读写许多数据位置的存储结构。 |
| FIFO | 先进先出队列（First-In, First-Out） | 最先进入的数据最先离开的队列，适合给 spike/event 排队。 |
| RTL | 寄存器传输级（Register-Transfer Level） | 描述“寄存器里保存什么、寄存器之间每个时钟周期如何传递和计算数据”的硬件设计层次。 |
| HDL | 硬件描述语言（Hardware Description Language） | 用来描述数字硬件结构和行为的语言类别。 |
| SystemVerilog | SystemVerilog | 本项目计划使用的硬件描述与验证语言。 |
| testbench | 测试平台 | 在仿真中给硬件模块输入刺激、检查输出是否正确的测试代码。 |
| waveform | 波形 | 把数字信号随时间的 0/1 或数值变化画出来，帮助理解硬件时序。 |
| synthesis | 综合 | 把 RTL 描述转换成可由 FPGA 逻辑资源实现的网络。 |
| implementation | 实现 / 布局布线阶段 | 把综合后的逻辑映射、放置并连接到具体 FPGA 资源。 |
| timing analysis | 时序分析 | 检查信号传播是否满足 clock period 等时间约束。 |
| bitstream | 配置比特流 | 用于配置 FPGA 可编程资源的数据。 |
| latency | 延迟 | 一次操作从发起到结果可用经历的时间。 |
| throughput | 吞吐 | 单位时间持续完成的工作量。 |
| bandwidth | 带宽 | 单位时间可持续搬运的数据量。 |
| critical path | 关键路径（critical path） | 在当前时序分析范围内延迟最长、最容易限制最高时钟频率的组合逻辑路径。 |
| slack | 时序裕量（slack） | 所需时间预算减去实际路径延迟后的余量；本课程简化模型中负值表示目标周期过短。 |
| memory hierarchy | 内存层次（memory hierarchy） | 把寄存器、片上 RAM、外部内存等不同容量、距离和访问成本的存储层次组织起来看待。 |
| development board | 开发板（development board） | 围绕 FPGA 芯片提供供电、clock、reset、I/O、配置路径和常用外设的实验平台。 |
| host | 主机（host） | 运行实验控制、文件、网络或管理软件的一侧，与 FPGA/PL 通过平台通信路径交换数据。 |
| PL | 可编程逻辑（programmable logic） | 由 bitstream 配置成具体硬件数据路径和控制逻辑的可编程区域。 |
| DDR | 双倍数据速率同步动态随机存储器（Double Data Rate Synchronous Dynamic Random-Access Memory, DDR SDRAM） | FPGA 板上常见的大容量外部内存；容量大，但访问方式和片上存储不同。 |
| burst | 突发传输（burst） | 把多个相邻数据组织成一段连续批量传输，以减少固定启动成本被重复支付的次数。 |
| transaction | 事务（transaction） | 一次较完整的读或写操作；在 AXI 中可以包含一个或多个 beat。 |
| beat | 传输拍（beat） | 一次 transaction 中的一个数据传输单位。 |
| VALID/READY handshake | VALID/READY 握手 | sender 用 VALID 表示当前 payload 有效，receiver 用 READY 表示可接收；两者在有效 clock edge 同时为 1 时才完成 transfer。 |
| AXI | 高级可扩展接口（Advanced eXtensible Interface） | ARM/FPGA 系统里常见的一组片上通信协议，本项目只学习实际需要的部分。 |
| CPU | 中央处理器（Central Processing Unit） | 通用处理器，擅长灵活执行指令和控制复杂程序流程。 |
| GPU | 图形处理器（Graphics Processing Unit） | 高度并行的处理器，尤其擅长大量规则的数值运算。 |
| SoC | 片上系统（System on Chip） | 在一颗芯片里集成处理器、内存接口、外设等多种系统功能。 |
| BRAM | 块随机存取存储器（Block RAM） | FPGA 芯片内部专门用于存储数据的片上内存块。 |
| URAM | 超级随机存取存储器（UltraRAM） | 部分 FPGA 中容量更大的片上存储块。 |
| CSR | 压缩稀疏行（Compressed Sparse Row） | 一种高效存储稀疏矩阵/图连接的数据结构；本项目后期可用于表示突触连接。 |
| CI | 持续集成（Continuous Integration） | 每次代码变化后自动运行测试和检查的工程流程。 |
| synapse stream | 突触记录流（synapse stream） | 按顺序产生的 synapse records 流，例如 source、target、weight 与结束标记。 |
| router | 路由器 / 路由逻辑（router） | 根据 event 的 source 等信息决定后续查找或发送方向的控制逻辑。 |
| source index | source 索引（source index） | 从 source neuron ID 映射到连续 synapse record 区间，例如 `(start_offset, fanout_count)`。 |
| adjacency list | 邻接表（adjacency list） | 为每个 source 直接列出真实相邻 target 的稀疏图表示。 |
| sparse graph | 稀疏图（sparse graph） | 可能连接很多 node，但真实 edge 只占所有可能连接很小一部分的图。 |
| backpressure | 背压（backpressure） | 当下游暂时不能接收数据时，用控制信号要求上游等待/保持数据，避免静默丢失。 |
| event | 事件（event） | 系统需要处理的一条离散记录；本项目中 spike event 最小可只携带 source neuron ID。 |
| time multiplexing | 时间复用（time multiplexing） | 让同一物理计算单元在不同时间片轮流服务多个虚拟对象，以时间换取硬件资源。 |
| address | 地址（address） | 选择 memory 中某个位置的编号；address 决定“访问哪里”，不是被保存的数据本身。 |
| memory | 存储器（memory） | 保存许多数据或 state 的硬件/抽象；通过不同组织方式可实现 register file、RAM 等。 |

## 使用规则

1. 第一次出现的缩写仍在正文展开。
2. 本表只帮助复习，不要求第一天背诵。
3. 如果某个词对完成当前 lesson 不必要，应尽量延后引入。
4. 新增术语时，中英文 glossary 同步更新。
