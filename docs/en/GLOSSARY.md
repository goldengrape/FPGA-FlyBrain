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
| synthesis | synthesis | Transformation of RTL into a network implementable with FPGA logic resources. |
| implementation | implementation / place-and-route stage | Mapping, placing, and routing synthesized logic onto specific FPGA resources. |
| timing analysis | timing analysis | Checking whether signal propagation satisfies clock-period constraints. |
| bitstream | bitstream | Configuration data used to program FPGA resources. |
| latency | latency | Time from starting one operation until its result becomes available. |
| throughput | throughput | Sustained work completed per unit time. |
| bandwidth | bandwidth | Sustained data moved per unit time. |
| critical path | critical path | The longest relevant combinational path in a timing analysis scope and a common limiter of target clock period. |
| slack | slack | Remaining timing margin after subtracting path delay from the available time budget; negative slack fails the lesson's simplified timing rule. |
| memory hierarchy | memory hierarchy | A view of registers, on-chip RAM, external memory, and other storage levels with different capacity, distance, and access cost. |
| development board | development board | An experiment platform that surrounds an FPGA with power, clocks, reset, I/O, configuration paths, and common peripherals. |
| host | host | The software/control side that exchanges data with FPGA programmable logic through a platform communication path. |
| PL | programmable logic | The FPGA region configured by a bitstream into concrete hardware datapaths and control logic. |
| DDR | Double Data Rate Synchronous Dynamic Random-Access Memory (DDR SDRAM) | Large external memory commonly found on FPGA boards; it offers much more capacity than on-chip memory but has different access costs and behavior. |
| burst | burst | A contiguous batch of adjacent data transfers that can amortize fixed startup cost. |
| transaction | transaction | A complete read or write operation at the protocol level; in AXI it can contain one or more beats. |
| beat | beat | One data-transfer unit inside a transaction. |
| VALID/READY handshake | VALID/READY handshake | The sender marks a payload valid with VALID, the receiver marks acceptance capability with READY, and transfer occurs only when both are high on an active clock edge. |
| AXI | Advanced eXtensible Interface | A family of on-chip communication protocols common in ARM/FPGA systems; this project will teach only the subset it actually needs. |
| CPU | Central Processing Unit | A general-purpose processor optimized for flexible instruction execution and complex control flow. |
| GPU | Graphics Processing Unit | A highly parallel processor especially effective for large amounts of regular numerical work. |
| SoC | System on Chip | A chip that integrates multiple system functions such as processors, memory interfaces, and peripherals. |
| BRAM | Block RAM | Dedicated on-chip memory blocks inside an FPGA. |
| URAM | UltraRAM | Larger on-chip memory blocks available in some FPGA families. |
| CSR | Compressed Sparse Row | A compact data structure for sparse matrices/graphs; later it can represent synaptic connectivity. |
| CI | Continuous Integration | An engineering workflow that automatically runs tests and checks after code changes. |
| synapse stream | synapse stream | An ordered stream of synapse records such as source, target, weight, and an end marker. |
| router | router / routing logic | Control logic that uses event/source information to decide which lookup or destination comes next. |
| source index | source index | A mapping from source neuron ID to a contiguous synapse-record range, such as `(start_offset, fanout_count)`. |
| adjacency list | adjacency list | A sparse representation that directly lists the real neighboring targets for each source. |
| sparse graph | sparse graph | A graph in which real edges occupy only a small fraction of all possible node-to-node connections. |
| backpressure | backpressure | A control mechanism that makes an upstream producer wait/hold data when the downstream consumer cannot accept it. |
| event | event | A discrete record that the system must process; a minimal spike event may carry only a source neuron ID. |
| time multiplexing | time multiplexing | Reusing one physical compute unit for several virtual objects at different times, trading time for hardware resources. |
| address | address | A number selecting a memory location; it says where to access, not what data is stored there. |
| memory | memory | Storage for many values or pieces of state; different organizations can implement RAM, register files, and related structures. |
| connectome | connectome | A dataset describing structural connections among neurons; it may include neuron/edge metadata but is not the same as runtime membrane state or spike queues. |
| manifest | manifest | A small description shipped with an artifact, recording fields such as schema version, byte count, checksum, and provenance. |
| checksum | checksum | A deterministic digest of exact bytes used to verify data integrity; matching checksums do not by themselves prove scientific/model correctness. |
| utilization | utilization | Demand relative to a stage's capacity, such as demand/capacity. |
| bottleneck | bottleneck | The stage currently limiting a workload; it depends on demand and capacity and can move with scale or traffic pattern. |
| hotspot | hotspot | Work or traffic concentrated on a small set of neurons, banks, queues, or resources, potentially causing local congestion. |
| closed loop | closed loop | A system whose output changes the environment and therefore changes later input; future input depends on prior system behavior. |
| sensory encoder | sensory encoder | A boundary that maps environment observations to selected neural stimulation; manual mappings must be documented explicitly. |
| output decoder | output decoder | A boundary that maps selected neural activity to behavior/control signals; manual mappings must be documented explicitly. |
| benchmark | benchmark | A reproducible comparison experiment that freezes model, data, input, and measurement rules before comparing latency, throughput, energy, or related metrics. |
| energy per event | energy per event | Total measured energy over an interval divided by completed events/work units; the power and time measurement boundary must be explicit. |

## Usage rules

1. First-use abbreviations must still be expanded in the lesson body.
2. This table is for review, not memorization on day one.
3. If a term is unnecessary for the current lesson, delay introducing it.
4. New terms must be added to both English and Chinese glossaries together.
