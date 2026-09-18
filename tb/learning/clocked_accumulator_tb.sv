`timescale 1ns/1ps
module clocked_accumulator_tb;
    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic signed [7:0] input_value = '0;
    logic signed [7:0] state;

    clocked_accumulator dut (
        .clk(clk),
        .rst_n(rst_n),
        .input_value(input_value),
        .state(state)
    );

    task automatic tick_and_check(
        input logic signed [7:0] value,
        input logic signed [7:0] expected_state
    );
        begin
            input_value = value;
            #4 clk = 1'b1;
            #1;
            if (state !== expected_state)
                $fatal(1, "state got=%0d expected=%0d", state, expected_state);
            #5 clk = 1'b0;
        end
    endtask

    initial begin
        #4 clk = 1'b1;
        #1;
        if (state !== 8'sd0)
            $fatal(1, "reset failed");
        #5 clk = 1'b0;
        rst_n = 1'b1;

        tick_and_check(8'sd1, 8'sd1);
        tick_and_check(8'sd2, 8'sd3);
        tick_and_check(8'sd3, 8'sd6);

        $display("PASS lesson06 clocked_accumulator");
        $finish;
    end
endmodule
