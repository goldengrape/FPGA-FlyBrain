// LAB-HW-07: one simple BRAM-backed neuron-state teaching store.
//
// Contract:
//   - 1024 x 32-bit words
//   - byte address in bram_addr; word index is bram_addr[11:2]
//   - synchronous read
//   - read-first behavior for a same-cycle read/write
//   - full 32-bit writes only in this teaching slice
//
// The X_INTERFACE_INFO attributes let Vivado IP Integrator group these ports
// as a native BRAM interface behind AXI BRAM Controller.
module kv260_neuron_state_store (
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT CLK" *)
    input  logic        bram_clk,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT RST" *)
    input  logic        bram_rst,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT EN" *)
    (* X_INTERFACE_PARAMETER = "MEM_SIZE 4096, MEM_WIDTH 32, READ_WRITE_MODE READ_WRITE" *)
    input  logic        bram_en,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT WE" *)
    input  logic [3:0]  bram_we,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT ADDR" *)
    input  logic [31:0] bram_addr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT DIN" *)
    input  logic [31:0] bram_wrdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORT DOUT" *)
    output logic [31:0] bram_rddata
);

    localparam int STATE_WORDS = 1024;
    localparam int WORD_ADDR_WIDTH = 10;

    wire [WORD_ADDR_WIDTH-1:0] word_addr = bram_addr[WORD_ADDR_WIDTH+1:2];

    (* ram_style = "block" *)
    logic [31:0] state_mem [0:STATE_WORDS-1];

    always_ff @(posedge bram_clk) begin
        if (bram_rst) begin
            bram_rddata <= 32'd0;
        end else if (bram_en) begin
            // Read first: the output receives the pre-write contents.
            bram_rddata <= state_mem[word_addr];

            // AXI4-Lite host accesses in this Lab are aligned full-word writes.
            // Partial byte writes are intentionally outside the teaching contract.
            if (bram_we == 4'hf) begin
                state_mem[word_addr] <= bram_wrdata;
            end
        end
    end

endmodule
