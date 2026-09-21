# KV260 Ubuntu / u-dma-buf Setup and Preflight

This prerequisite sits **between LAB-HW-09 and LAB-HW-10**. LAB-HW-09 uses Linux-managed memory only. LAB-HW-10 is the first Lab where programmable logic reaches DDR through the non-coherent `S_AXI_HP0_FPD` path, so it requires an explicit DMA-safe buffer provider.

This document is for two audiences:

- **learners** verify that the course runtime image is already prepared and pass the preflight before LAB-HW-10;
- **course maintainers/instructors** prepare u-dma-buf against the exact KV260 Ubuntu/kernel. Building a kernel module is not a LAB-HW-10 learning objective and must not be improvised during a graded run.

The status is still **authoring candidate**. No real-KV260 T-HW-010 PASS has yet certified this Ubuntu/kernel combination.

## 1. Frozen course contract

The current course freezes:

- upstream: `ikwzm/udmabuf`;
- source commit: `15bcde3cb960321e99983e227aeacc5807888333`;
- upstream driver version: `5.5.0`;
- course buffer: **4 MiB**;
- LAB-HW-10 minimum actually used: **2 MiB**;
- device: `/dev/udmabuf0`;
- sysfs: `/sys/class/u-dma-buf/udmabuf0`;
- open mode: `O_RDWR | O_SYNC`;
- accepted `sync_mode`: **1 or 2**;
- first LAB-HW-10 mapped aperture: `HP0_DDR_LOW = [0x00000000, 0x80000000)`.

The machine-readable source identity is in:

`boards/kv260/runtime/udmabuf_source.json`

Do not substitute the older Linux module named `udmabuf`. Upstream distinguishes it from **u-dma-buf**; this course expects the `/sys/class/u-dma-buf/` class.

## 2. Learner: determine whether the course image is already prepared

On the **KV260 runtime host**:

```bash
uname -a
uname -m
cat /etc/os-release
ls -l /dev/udmabuf0
cat /sys/class/u-dma-buf/udmabuf0/phys_addr
cat /sys/class/u-dma-buf/udmabuf0/size
cat /sys/class/u-dma-buf/udmabuf0/sync_mode
```

If any required path is missing, do not continue directly into HW-10 and do not download an unrecorded kernel module during the graded run. Use section 4 to prepare a module that exactly matches the running kernel.

## 3. Learner: run the course preflight

Copy these files to the runtime host:

- `boards/kv260/runtime/preflight_udmabuf.py`;
- `boards/kv260/runtime/udmabuf_source.json`.

For example, if Ethernet already works:

```bash
scp boards/kv260/runtime/preflight_udmabuf.py \
    boards/kv260/runtime/udmabuf_source.json \
    ubuntu@<kv260-ip>:/tmp/
```

On the KV260:

```bash
sudo python3 /tmp/preflight_udmabuf.py \
  --physical \
  --json-out /tmp/lab-hw-10-udmabuf-preflight.json
```

A PASS proves all of the following:

1. the runtime identifies as Kria/KV260;
2. the runtime architecture is ARM64;
3. the `u-dma-buf` module is loaded;
4. `/dev/udmabuf0` and its sysfs directory exist;
5. size is at least 2 MiB;
6. `sync_mode` is 1 or 2;
7. the complete 2 MiB benchmark window lies inside `HP0_DDR_LOW`;
8. root can open and mmap u-dma-buf with `O_SYNC`;
9. root can open `/dev/mem`.

Success ends with:

`STATUS=PASS`

This does **not** prove the AXI CDMA bitstream or a real DMA transfer. It only closes the Ubuntu/buffer-provider prerequisite.

## 4. Instructor/course maintainer: build for the exact running kernel

Record the exact kernel and verify that its build tree exists:

```bash
uname -r
uname -m
test -e /lib/modules/$(uname -r)/build && echo KERNEL_BUILD_TREE=FOUND
```

If the build tree is missing, first try the matching headers from the current Ubuntu repository:

```bash
sudo apt update
sudo apt install -y build-essential git linux-headers-$(uname -r)
```

If `linux-headers-$(uname -r)` is unavailable, **stop**. Do not compile against a merely similar kernel. The course image must provide the matching headers/source tree or a module already built and validated for that exact kernel.

Fetch the frozen source:

```bash
git clone https://github.com/ikwzm/udmabuf.git
cd udmabuf
git checkout 15bcde3cb960321e99983e227aeacc5807888333
git rev-parse HEAD
make all
```

Install it for the current kernel:

```bash
sudo install -D -m 0644 u-dma-buf.ko \
  /lib/modules/$(uname -r)/extra/u-dma-buf.ko
sudo depmod -a
```

One-time test load with a 4 MiB buffer:

```bash
sudo modprobe u-dma-buf udmabuf0=4194304
ls -l /dev/udmabuf0
cat /sys/class/u-dma-buf/udmabuf0/size
```

Only after that succeeds, make the load persistent:

```bash
printf '%s\n' 'options u-dma-buf udmabuf0=4194304' | \
  sudo tee /etc/modprobe.d/fpga-flybrain-udmabuf.conf

printf '%s\n' 'u-dma-buf' | \
  sudo tee /etc/modules-load.d/fpga-flybrain-udmabuf.conf
```

Reboot and rerun the physical preflight from section 3.

## 5. A subtle failure: the buffer can land outside the mapped aperture

The existence of `/dev/udmabuf0` does not make it usable by this LAB-HW-10 bitstream. The first design maps only `HP0_DDR_LOW`, so the checker rejects a benchmark window allocated at or above `0x80000000`.

If you see:

`ERROR=DMA_BUFFER_OUTSIDE_HP0_DDR_LOW`

the learner must not guess a physical address or casually alter `dma_mask_bit`, CMA, or kernel boot parameters. Retain:

- `phys_addr`;
- `size`;
- kernel/OS identity;
- preflight JSON;
- boot log.

This means the **course image/platform does not yet satisfy the HW-10 placement contract**. It is a maintainer issue that requires another controlled physical dry run.

## 6. Why sync_mode is also checked

Upstream u-dma-buf documents that the cache behavior associated with `O_SYNC` is controlled by `sync_mode`. Because the course HP0 path is non-coherent, HW-10 accepts only:

- `sync_mode=1`: CPU cache disabled when opened with O_SYNC;
- `sync_mode=2`: write-combine semantics when opened with O_SYNC.

The current teaching contract does not accept `sync_mode=3`. The LAB-HW-10 benchmark helper repeats this check so safety does not depend only on a manual preflight.

## 7. Do not force a PASS

Do not:

- compile with mismatched kernel headers;
- copy an unknown `.ko` from a random tutorial;
- guess `phys_addr`;
- weaken kernel security to bypass `/dev/mem` policy;
- change CMA, device tree, or boot arguments during the graded benchmark;
- report a dry-run PASS as a physical PASS.

## 8. Prerequisite evidence to retain

Before LAB-HW-10 retain:

- Ubuntu image identity;
- `uname -a` / `uname -r` / `uname -m`;
- u-dma-buf upstream commit and driver version;
- module-file identity/hash once the course image is frozen;
- `/dev/udmabuf0` permissions;
- `phys_addr` / `size` / `sync_mode` / `dma_coherent`;
- `lab-hw-10-udmabuf-preflight.json`;
- Git commit and date.

These are prerequisite evidence. They do not replace T-HW-010 AXI-CDMA data-integrity and measurement evidence.

## 9. Upstream basis

This procedure uses the documentation and source at the frozen commit of `ikwzm/udmabuf`. Upstream documents ARM64/Zynq UltraScale+ MPSoC, out-of-tree builds, the `udmabuf0=<bytes>` module parameter, `/dev/udmabuf0`, `phys_addr`, `size`, `sync_mode`, and the `O_SYNC` cache behavior.

The final supported KV260/Ubuntu combination remains governed by this course's own physical evidence.
