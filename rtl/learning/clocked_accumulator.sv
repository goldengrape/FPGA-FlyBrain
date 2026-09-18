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
