// Teaching artifact: fixed 8-bit signed demo.
// Reset is synchronous and active-low.
// candidate uses finite-width two's-complement wraparound if addition overflows.
// Overflow is deliberately outside this lesson's approved neuron contract; this
// module is not formal MOD-003. Formal numeric semantics are frozen later.
module tutorial_if_neuron (
    input  logic              clk,
    input  logic              rst_n,
    input  logic signed [7:0] input_current,
    input  logic signed [7:0] threshold,
    input  logic signed [7:0] reset_value,
    output logic signed [7:0] membrane_v,
    output logic              spike
);
    logic signed [7:0] candidate;
    logic signed [7:0] next_v;
    logic spike_next;

    always_comb begin
        candidate = membrane_v + input_current;
        spike_next = candidate >= threshold;

        if (spike_next)
            next_v = reset_value;
        else
            next_v = candidate;
    end

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            membrane_v <= reset_value;
            spike <= 1'b0;
        end else begin
            membrane_v <= next_v;
            spike <= spike_next;
        end
    end
endmodule
