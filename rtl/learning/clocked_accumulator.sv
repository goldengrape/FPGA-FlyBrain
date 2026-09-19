// Teaching artifact: fixed 8-bit signed arithmetic.
// Reset is synchronous and active-low: rst_n is sampled only on posedge clk.
// Overflow intentionally follows 8-bit two's-complement wraparound here.
// This is not the formal MOD-003 numeric policy; formal saturation/overflow
// semantics are frozen later by the fixed-point reference and RMD checkpoints.
module clocked_accumulator (
    input  logic              clk,
    input  logic              rst_n,
    input  logic signed [7:0] input_value,
    output logic signed [7:0] state
);
    always_ff @(posedge clk) begin
        if (!rst_n)
            state <= '0;
        else
            state <= state + input_value;
    end
endmodule
