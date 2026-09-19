`timescale 1ns/1ps
module tutorial_if_neuron_edge_tb;
    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic signed [7:0] input_current = '0;
    logic signed [7:0] threshold = 8'sd4;
    logic signed [7:0] reset_value = '0;
    logic signed [7:0] membrane_v;
    logic spike;

    tutorial_if_neuron dut (
        .clk(clk),
        .rst_n(rst_n),
        .input_current(input_current),
        .threshold(threshold),
        .reset_value(reset_value),
        .membrane_v(membrane_v),
        .spike(spike)
    );

    task automatic tick_and_check(
        input logic signed [7:0] current,
        input logic signed [7:0] expected_v,
        input logic expected_spike
    );
        begin
            input_current = current;
            #4 clk = 1'b1;
            #1;
            if (membrane_v !== expected_v)
                $fatal(1, "membrane_v got=%0d expected=%0d", membrane_v, expected_v);
            if (spike !== expected_spike)
                $fatal(1, "spike got=%0d expected=%0d", spike, expected_spike);
            #5 clk = 1'b0;
        end
    endtask

    task automatic apply_reset(
        input logic signed [7:0] new_reset,
        input logic signed [7:0] new_threshold
    );
        begin
            reset_value = new_reset;
            threshold = new_threshold;
            input_current = '0;
            rst_n = 1'b0;
            #4 clk = 1'b1;
            #1;
            if (membrane_v !== new_reset || spike !== 1'b0)
                $fatal(1, "reset failed v=%0d spike=%0d", membrane_v, spike);
            #5 clk = 1'b0;
            rst_n = 1'b1;
        end
    endtask

    initial begin
        // Non-zero reset and inhibitory input.
        apply_reset(-8'sd5, 8'sd4);
        tick_and_check(-8'sd3, -8'sd8, 1'b0);

        // Equality uses >= semantics and resets immediately.
        apply_reset(-8'sd5, 8'sd4);
        tick_and_check(8'sd9, -8'sd5, 1'b1);

        // Positive overflow false negative in the teaching 8-bit implementation:
        // mathematical 120 + 120 = 240, but 8-bit candidate wraps to -16.
        apply_reset(8'sd0, 8'sd127);
        tick_and_check(8'sd120, 8'sd120, 1'b0);
        threshold = 8'sd50;
        tick_and_check(8'sd120, -8'sd16, 1'b0);

        // Negative overflow false positive:
        // mathematical -106 + -100 = -206, but 8-bit candidate wraps to +50.
        apply_reset(8'sd0, 8'sd127);
        tick_and_check(-8'sd106, -8'sd106, 1'b0);
        threshold = 8'sd50;
        tick_and_check(-8'sd100, 8'sd0, 1'b1);

        // Parameter boundary: reset_value >= threshold causes tonic firing
        // with zero input. This is characterized, not endorsed as a formal model.
        apply_reset(8'sd4, 8'sd4);
        tick_and_check(8'sd0, 8'sd4, 1'b1);
        tick_and_check(8'sd0, 8'sd4, 1'b1);

        // Runtime synchronous reset.
        rst_n = 1'b0;
        #4 clk = 1'b1;
        #1;
        if (membrane_v !== 8'sd4 || spike !== 1'b0)
            $fatal(1, "runtime reset failed");
        #5 clk = 1'b0;

        $display("PASS tutorial_if_neuron_edge_tb (teaching boundaries characterized)");
        $finish;
    end

    initial begin
        #1500;
        $fatal(1, "watchdog timeout");
    end
endmodule
