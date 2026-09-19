`timescale 1ns/1ps
module clocked_accumulator_edge_tb;
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

    task automatic reset_state;
        begin
            rst_n = 1'b0;
            input_value = '0;
            #4 clk = 1'b1;
            #1;
            if (state !== 8'sd0)
                $fatal(1, "synchronous reset failed");
            #5 clk = 1'b0;
            rst_n = 1'b1;
        end
    endtask

    initial begin
        reset_state();

        // Positive boundary and wraparound: 127 + 1 -> -128.
        tick_and_check(8'sd100, 8'sd100);
        tick_and_check(8'sd27, 8'sd127);
        tick_and_check(8'sd1, -8'sd128);

        // Negative boundary and wraparound: -128 - 1 -> +127.
        reset_state();
        tick_and_check(-8'sd100, -8'sd100);
        tick_and_check(-8'sd28, -8'sd128);
        tick_and_check(-8'sd1, 8'sd127);

        // Synchronous reset must not change state until a clock edge.
        rst_n = 1'b0;
        #3;
        if (state !== 8'sd127)
            $fatal(1, "state changed without a clock edge during synchronous reset");
        #1 clk = 1'b1;
        #1;
        if (state !== 8'sd0)
            $fatal(1, "reset did not take effect at the clock edge");
        #5 clk = 1'b0;

        $display("PASS clocked_accumulator_edge_tb (8-bit wraparound characterized)");
        $finish;
    end

    initial begin
        #1000;
        $fatal(1, "watchdog timeout");
    end
endmodule
