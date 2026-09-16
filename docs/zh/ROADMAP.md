# 从零到 FPGA 果蝇 — 学习与实现路线

> 这是一份面向人的高层路线图。实际任务顺序、编号与验收标准以 [RMD](RMD.md) 为准。

## 目标
从一个可检查的 LIF 神经元开始，逐步实现事件驱动的 FPGA 神经系统，最终运行由真实 MaleCNS 连接组约束的目标网络，并能与软件参考模型做正确性和性能对比。

## 工程原则
1. 先有软件 reference，再有 RTL。
2. 先证明小规模架构正确，再扩大规模。
3. 把计算与存储/数据移动分开看。
4. 每个学习阶段只引入一个主要新概念；跨度过大就增加 bridge slice。
5. AI 可以加速实现，但验证标准与架构判断由人负责。

## 阶段 0 — 把神经元变成可检查的程序
- Python LIF float reference。
- 固定随机种子，输出膜电位与 spike 轨迹。
- 建立最基础的生理/数学 sanity checks。

完成感：你能看到一个神经元按照明确规则放电。

## 阶段 1 — 学 fixed point，而不是马上写 RTL
- 在 Python 中模拟位宽、Q-format、rounding、saturation。
- 比较 float 与 fixed-point 的误差和 spike timing。
- 冻结第一版 neuron semantics。

完成感：你知道硬件数值为什么不是“无限精度实数”。

## 阶段 2 — 从程序变量跨到数字状态
- combinational adder。
- clocked counter。
- accumulator + threshold。
- 学会读 waveform，理解 register、clock、combinational/sequential。

完成感：你第一次理解“程序里的状态”如何成为电路里的状态。

## 阶段 3 — 第一个 SystemVerilog 神经元
- 实现 `lif_neuron_engine`。
- Python fixed-point vector 与 RTL 逐项比较。
- 用 testbench 和 waveform 解释输入、状态、threshold、spike、reset。

完成感：同一个神经元同时存在于 Python 和数字电路中，而且结果一致。

## 阶段 4 — 少量硬件模拟很多神经元
- neuron state RAM。
- scheduler / time multiplexing。
- 从 128 个扩到 1K。
- 测 cycles/update 和 RAM usage。

完成感：理解“16 万神经元不等于 16 万套物理电路”。

## 阶段 5 — 从神经元数组变成事件计算机
先用 4 个神经元手工走完整个事件旅程：

```text
spike(source)
→ queue
→ connectivity lookup
→ (target, weight)
→ target update
```

随后引入：
- sparse adjacency / CSR-like image；
- spike FIFO；
- synapse reader；
- synapse engine；
- target accumulator。

完成感：小网络可以只处理发生的 spike，而不是扫描全部连接。

## 阶段 6 — 第一次进入真实 FPGA
在买板前先做 synthesis dry run。

买板后顺序：
1. counter / observable register；
2. host ↔ FPGA 最小 loopback；
3. 把已验证的小网络迁移到 FPGA。

完成感：仿真里的电路真的在芯片中运行。

## 阶段 7 — 理解内存为什么会成为瓶颈
先建立 memory hierarchy / bandwidth 直觉，再接 DDR/AXI。

实验比较：
- sequential access；
- random access；
- burst access。

然后：
- DDR read/write integrity；
- AXI burst；
- 把 synapse store 从片上搬到 DDR；
- 测 bandwidth、latency、synaptic events/s。

完成感：理解现代 AI hardware 为什么经常被数据移动限制，而不是被加法限制。

## 阶段 8 — 第一次运行真实 connectome
- MaleCNS converter。
- versioned binary image + manifest/checksum。
- 先跑约 1K 神经元真实子图。
- 软件与 FPGA differential test。

完成感：你不再运行手写小网络，而是在运行真实生物连接数据。

## 阶段 9 — 扩规模到完整目标网络
按顺序扩展：

```text
1K → 10K → 50K → full target
```

持续测：
- DDR 带宽；
- FIFO 深度；
- bank conflict；
- hotspot；
- FPGA resource；
- real-time factor。

只有 baseline 正确后才做 lazy update、cache、banking、多 synapse engine 等优化。

## 阶段 10 — 给果蝇一个世界
Host 负责：
- sensory encoder；
- experiment control；
- visualization；
- output decoder。

FPGA 负责持续运行神经系统。

先从简单二维环境开始，再考虑虚拟身体、游戏或机器人。

最终可以在同一模型、同一数据、同一输入下比较 CPU / GPU / FPGA 的：
- latency；
- throughput；
- memory traffic；
- power / energy efficiency。

## 五个学习平台
```text
1. 计算神经元
2. 数字神经元
3. 事件神经网络
4. 真实 FPGA 与外部内存
5. 真实 MaleCNS 连接组
```

每个平台都必须以一个可见、可测试的成果结束，而不是“学完一批理论”。
