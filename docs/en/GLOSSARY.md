# GLOSSARY — Beginner Reference

This is a reference sheet, not a substitute for first-use explanations in the lessons. When an abbreviation appears for the first time in a Notebook, the lesson must still spell it out and explain it in plain language.

| Term | Full name | Plain-language meaning |
|---|---|---|
| FPGA | Field-Programmable Gate Array | A chip whose internal digital circuitry can be configured after manufacturing. Rather than merely running instructions like a general-purpose CPU, it can implement our own parallel hardware structure. |
| LIF | Leaky Integrate-and-Fire | A simplified neuron model: state decays, inputs accumulate, crossing a threshold emits a spike, then the state resets according to a rule. |
| SNN | Spiking Neural Network | A neural network in which information is communicated through discrete spike events. |
| bit | binary digit | The smallest basic unit of digital information, usually 0 or 1. |
| floating point | floating-point number | A finite-precision representation that uses a significand-like component and exponent to cover a large numeric range. Python `float` is typically a 64-bit binary floating-point value. |
| fixed point | fixed-point number | A finite-width numeric format in which the binary point is held at a fixed position. |
| quantization | quantization | Mapping a continuous or high-precision value onto a finite set of representable values. |
| rounding | rounding | The rule used when a value lies between representable values. |
| overflow | overflow | A result falls outside the numeric range representable by the chosen width. |
| saturation | saturation | An overflow policy that clamps the result to the largest or smallest representable value instead of wrapping around. |
| register | register | A small hardware storage element that holds digital state under clock control. |
| clock | clock | A periodic signal used to coordinate when synchronous digital circuits update state. |
| clock edge | clock edge | A low-to-high or high-to-low transition of the clock; many registers update at a chosen edge. |
| combinational logic | combinational logic | Circuitry whose output depends only on its current inputs and does not itself store prior state. |
| sequential logic | sequential logic | Circuitry whose behavior depends on previously stored state as well as current inputs. |
| RAM | Random-Access Memory | Storage with many addressable locations that can be read and written by address. |
| FIFO | First-In, First-Out queue | A queue in which the earliest arriving item leaves first; useful for spike/event buffering. |
| RTL | Register-Transfer Level | A hardware-design level that describes what registers store and how data moves and is transformed between registers across clock cycles. |
| HDL | Hardware Description Language | A class of languages used to describe digital hardware structure and behavior. |
| SystemVerilog | SystemVerilog | The hardware design and verification language planned for this project. |
| testbench | testbench | Simulation code that drives inputs into a hardware module and checks its outputs. |
| waveform | waveform | A time plot of digital signals, used to understand hardware timing and state changes. |
| DDR | Double Data Rate SDRAM | Large external memory commonly found on FPGA boards; it offers much more capacity than on-chip memory but has different access costs and behavior. |
| AXI | Advanced eXtensible Interface | A family of on-chip communication protocols common in ARM/FPGA systems; this project will teach only the subset it actually needs. |
| CPU | Central Processing Unit | A general-purpose processor optimized for flexible instruction execution and complex control flow. |
| GPU | Graphics Processing Unit | A highly parallel processor especially effective for large amounts of regular numerical work. |
| SoC | System on Chip | A chip that integrates multiple system functions such as processors, memory interfaces, and peripherals. |
| BRAM | Block RAM | Dedicated on-chip memory blocks inside an FPGA. |
| URAM | UltraRAM | Larger on-chip memory blocks available in some FPGA families. |
| CSR | Compressed Sparse Row | A compact data structure for sparse matrices/graphs; later it can represent synaptic connectivity. |
| CI | Continuous Integration | An engineering workflow that automatically runs tests and checks after code changes. |

## Usage rules

1. First-use abbreviations must still be expanded in the lesson body.
2. This table is for review, not memorization on day one.
3. If a term is unnecessary for the current lesson, delay introducing it.
4. New terms must be added to both English and Chinese glossaries together.
