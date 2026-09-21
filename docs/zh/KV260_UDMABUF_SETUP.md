# KV260 Ubuntu / u-dma-buf 准备与预检

这份说明位于 **LAB-HW-09 与 LAB-HW-10 之间**。LAB-HW-09 只使用 Linux-managed memory；LAB-HW-10 第一次要求 programmable logic 通过 non-coherent `S_AXI_HP0_FPD` 访问 DDR，因此需要一个明确的 DMA-safe buffer provider。

本文面向两类人：

- **学生**：确认课程 runtime image 已经准备好，执行预检后再开始 LAB-HW-10；
- **课程维护者/教师**：在精确匹配的 KV260 Ubuntu/kernel 上准备 u-dma-buf。内核模块构建不是 LAB-HW-10 的学习目标，不应在 graded run 中临时完成。

当前状态仍是 **authoring candidate**。真实 KV260 + 课程 Ubuntu/kernel 尚未留下 T-HW-010 physical PASS，因此下面的版本与步骤必须在实体板验证后才能升级为 tested baseline。

## 1. 冻结的课程 contract

课程当前固定：

- upstream：`ikwzm/udmabuf`；
- source commit：`15bcde3cb960321e99983e227aeacc5807888333`；
- upstream driver version：`5.5.0`；
- course buffer：**4 MiB**；
- LAB-HW-10 实际最低需求：**2 MiB**；
- device：`/dev/udmabuf0`；
- sysfs：`/sys/class/u-dma-buf/udmabuf0`；
- open mode：`O_RDWR | O_SYNC`；
- 可接受 `sync_mode`：**1 或 2**；
- LAB-HW-10 第一版 mapped aperture：`HP0_DDR_LOW = [0x00000000, 0x80000000)`。

机器可读版本在：

`boards/kv260/runtime/udmabuf_source.json`

不要用旧的同名 Linux `udmabuf` 模块代替 **u-dma-buf**。上游说明明确区分了二者；本课程使用的 sysfs class 是 `/sys/class/u-dma-buf/`。

## 2. 学生：先判断课程 image 是否已经准备好

在 **KV260 runtime host** 上执行：

```bash
uname -a
uname -m
cat /etc/os-release
ls -l /dev/udmabuf0
cat /sys/class/u-dma-buf/udmabuf0/driver_version
cat /sys/class/u-dma-buf/udmabuf0/phys_addr
cat /sys/class/u-dma-buf/udmabuf0/size
cat /sys/class/u-dma-buf/udmabuf0/sync_mode
```

如果任意路径不存在，不要直接进入 HW-10，也不要临时从互联网下载一个未记录版本的 kernel module。转到本文第 4 节，由课程维护者准备与当前 kernel **精确匹配**的 module。

## 3. 学生：运行课程预检

把下面两个文件复制到 runtime host：

- `boards/kv260/runtime/preflight_udmabuf.py`
- `boards/kv260/runtime/udmabuf_source.json`（用于保存 source identity；checker 本身也冻结了同一 commit/version）

例如 Ethernet 已可用时：

```bash
scp boards/kv260/runtime/preflight_udmabuf.py \
    boards/kv260/runtime/udmabuf_source.json \
    ubuntu@<kv260-ip>:/tmp/
```

在 KV260 上：

```bash
sudo python3 /tmp/preflight_udmabuf.py \
  --physical \
  --json-out /tmp/lab-hw-10-udmabuf-preflight.json
```

PASS 必须同时证明：

1. runtime model 可识别为 Kria/KV260；
2. runtime architecture 是 ARM64；
3. `u-dma-buf` module 已加载；
4. `/dev/udmabuf0` 与 sysfs 都存在；
5. sysfs `driver_version` 与课程冻结版本 **5.5.0** 一致；
6. size ≥ 2 MiB；
7. `sync_mode` 是 1 或 2；
8. benchmark 使用的 2 MiB window 完整位于 `HP0_DDR_LOW`；
9. root 可以用 `O_SYNC` 打开并 mmap u-dma-buf；
10. root 可以打开 `/dev/mem`。

通过时最后出现：

`STATUS=PASS`

这仍然**不**证明 AXI CDMA、bitstream 或真实 DMA 已工作。它只关闭 HW-10 的 Ubuntu/buffer-provider prerequisite。

## 4. 教师/课程维护者：准备与当前 kernel 匹配的 module

先记录精确 kernel，并确认 build tree 存在：

```bash
uname -r
uname -m
test -e /lib/modules/$(uname -r)/build && echo KERNEL_BUILD_TREE=FOUND
```

如果 build tree 不存在，可以先尝试当前 Ubuntu repository 提供的匹配 headers：

```bash
sudo apt update
sudo apt install -y build-essential git linux-headers-$(uname -r)
```

如果 `linux-headers-$(uname -r)` 不存在，**停止**。不要拿“看起来差不多”的 headers 编译。课程 image 必须同时提供与 running kernel 对应的 headers/source tree，或者提供已针对该 kernel 构建并验证过的 module。

取得冻结 source：

```bash
git clone https://github.com/ikwzm/udmabuf.git
cd udmabuf
git checkout 15bcde3cb960321e99983e227aeacc5807888333
git rev-parse HEAD
make all
```

安装到当前 kernel：

```bash
sudo install -D -m 0644 u-dma-buf.ko \
  /lib/modules/$(uname -r)/extra/u-dma-buf.ko
sudo depmod -a
```

一次性测试加载 4 MiB buffer：

```bash
sudo modprobe u-dma-buf udmabuf0=4194304
ls -l /dev/udmabuf0
cat /sys/class/u-dma-buf/udmabuf0/driver_version
cat /sys/class/u-dma-buf/udmabuf0/size
```

确认无误后再做持久化：

```bash
printf '%s\n' 'options u-dma-buf udmabuf0=4194304' | \
  sudo tee /etc/modprobe.d/fpga-flybrain-udmabuf.conf

printf '%s\n' 'u-dma-buf' | \
  sudo tee /etc/modules-load.d/fpga-flybrain-udmabuf.conf
```

重启后重新运行第 3 节 physical preflight。

## 5. 一个容易被忽略的失败：buffer 落在错误 physical aperture

u-dma-buf 能创建 `/dev/udmabuf0`，不等于 LAB-HW-10 一定能用它。第一版 bitstream 只映射 `HP0_DDR_LOW`，因此 checker 会拒绝 benchmark window 落在 `0x80000000` 及以上的 allocation。

若出现：

`ERROR=DMA_BUFFER_OUTSIDE_HP0_DDR_LOW`

学生不要自行猜 physical address，也不要随意改 `dma_mask_bit`、CMA 或 kernel boot parameters。保存：

- `phys_addr`；
- `size`；
- kernel/OS identity；
- preflight JSON；
- boot log。

这个失败说明**课程 image/platform 还没有满足 HW-10 的物理放置 contract**，应由课程维护者修正并重新做实体 dry-run。

## 6. sync_mode 为什么也必须检查

上游 u-dma-buf 文档说明，`O_SYNC` 的 cache behavior 由 `sync_mode` 决定。课程的 HP0 path 是 non-coherent，因此 HW-10 只接受：

- `sync_mode=1`：O_SYNC 时 CPU cache disabled；
- `sync_mode=2`：O_SYNC 时使用 write-combine 语义。

当前教学 contract 不接受 `sync_mode=3`。LAB-HW-10 benchmark helper 也会再次检查，不只依赖学生手工预检。

## 7. 失败时不要做什么

不要为了 PASS：

- 用不匹配的 kernel headers 编译；
- 从随机教程复制未知版本的 `.ko`；
- 猜 `phys_addr`；
- 降低 kernel security 来绕过 `/dev/mem` policy；
- 在 graded benchmark 当天临时改变 CMA、device tree 或 boot arguments；
- 把 dry-run PASS 写成 physical PASS。

## 8. 需要保存的 prerequisite evidence

进入 HW-10 前保存：

- Ubuntu image identity；
- `uname -a` / `uname -r` / `uname -m`；
- u-dma-buf upstream commit 与 driver version；
- module file identity/hash（课程 image 冻结后）；
- `/dev/udmabuf0` 权限；
- `phys_addr` / `size` / `sync_mode` / `dma_coherent`；
- `lab-hw-10-udmabuf-preflight.json`；
- Git commit 与日期。

这些 evidence 属于 HW-10 prerequisite，不替代 T-HW-010 的真实 AXI CDMA data-integrity 与 measurement evidence。

## 9. 上游依据

本说明使用 upstream `ikwzm/udmabuf` 在上述冻结 commit 的文档与源码作为依据：上游说明了 ARM64/Zynq UltraScale+ MPSoC、out-of-tree build、`udmabuf0=<bytes>` module parameter、`/dev/udmabuf0`、`phys_addr`、`size`、`sync_mode` 与 `O_SYNC` cache behavior。

真实 KV260/Ubuntu 组合的最终支持状态仍以课程自己的 physical evidence 为准。
