// LAB-HW-08 shared state/trace BRAM.
// Port A is the PS-visible AXI BRAM Controller side.
// Port B is used only by the replay engine while the host promises not to access Port A.
//
// Teaching clock/access contract:
//   - a_clk and b_clk are driven by the same LAB-HW-08 clock net;
//   - host Port A stays idle while the replay engine owns Port B;
//   - cross-port same-address concurrent writes are outside the contract;
//   - Port A accepts full-word writes only (a_we == 4'hf).
//
// The two-process memory inference intentionally triggers Verilator MULTIDRIVEN;
// the course static-check script waives that warning only for this module.
module kv260_replay_state_store (
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORTA CLK" *)
    input  logic        a_clk,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORTA RST" *)
    input  logic        a_rst,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORTA EN" *)
    (* X_INTERFACE_PARAMETER = "MEM_SIZE 4096, MEM_WIDTH 32, READ_WRITE_MODE READ_WRITE" *)
    input  logic        a_en,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORTA WE" *)
    input  logic [3:0]  a_we,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORTA ADDR" *)
    input  logic [31:0] a_addr,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORTA DIN" *)
    input  logic [31:0] a_wrdata,
    (* X_INTERFACE_INFO = "xilinx.com:interface:bram:1.0 BRAM_PORTA DOUT" *)
    output logic [31:0] a_rddata,

    input  logic        b_clk,
    input  logic        b_rst,
    input  logic        b_en,
    input  logic        b_we,
    input  logic [31:0] b_addr,
    input  logic [31:0] b_wrdata,
    output logic [31:0] b_rddata
);

    localparam int WORDS = 1024;
    localparam int WORD_ADDR_WIDTH = 10;

    wire [WORD_ADDR_WIDTH-1:0] a_word = a_addr[WORD_ADDR_WIDTH+1:2];
    wire [WORD_ADDR_WIDTH-1:0] b_word = b_addr[WORD_ADDR_WIDTH+1:2];

    (* ram_style = "block" *)
    logic [31:0] mem [0:WORDS-1];

    always_ff @(posedge a_clk) begin
        if (a_rst) begin
            a_rddata <= 32'd0;
        end else if (a_en) begin
            a_rddata <= mem[a_word];
            if (a_we == 4'hf) begin
                mem[a_word] <= a_wrdata;
            end
        end
    end

    always_ff @(posedge b_clk) begin
        if (b_rst) begin
            b_rddata <= 32'd0;
        end else if (b_en) begin
            b_rddata <= mem[b_word];
            if (b_we) begin
                mem[b_word] <= b_wrdata;
            end
        end
    end

endmodule
