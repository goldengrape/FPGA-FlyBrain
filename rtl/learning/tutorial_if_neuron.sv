module tutorial_if_neuron #(
    parameter int WIDTH = 8
) (
    input  logic clk,
    input  logic rst_n,
    input  logic signed [WIDTH-1:0] input_current,
    input  logic signed [WIDTH-1:0] threshold,
    input  logic signed [WIDTH-1:0] reset_value,
    output logic signed [WIDTH-1:0] membrane_v,
    output logic spike
);
    logic signed [WIDTH:0] candidate_ext;
    logic signed [WIDTH-1:0] next_v;
    logic spike_next;

    always_comb begin
        candidate_ext = $signed({membrane_v[WIDTH-1], membrane_v})
                      + $signed({input_current[WIDTH-1], input_current});
        spike_next = candidate_ext >= $signed({threshold[WIDTH-1], threshold});
        next_v = spike_next ? reset_value : candidate_ext[WIDTH-1:0];
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
