`timescale 1ns/1ps
module tutorial_if_neuron_tb;
    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic signed [7:0] input_current = 8'sd0;
    logic signed [7:0] threshold = 8'sd4;
    logic signed [7:0] reset_value = 8'sd0;
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

    task automatic apply_and_check(
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

    initial begin
        $dumpfile("tutorial_if_neuron.vcd");
        $dumpvars(0, tutorial_if_neuron_tb);

        #4 clk = 1'b1;
        #1;
        if (membrane_v !== 8'sd0 || spike !== 1'b0)
            $fatal(1, "reset failed");
        #5 clk = 1'b0;
        rst_n = 1'b1;

        apply_and_check(8'sd1, 8'sd1, 1'b0);
        apply_and_check(8'sd1, 8'sd2, 1'b0);
        apply_and_check(8'sd1, 8'sd3, 1'b0);
        apply_and_check(8'sd1, 8'sd0, 1'b1);
        apply_and_check(8'sd2, 8'sd2, 1'b0);
        apply_and_check(8'sd2, 8'sd0, 1'b1);

        $display("PASS lesson08 tutorial_if_neuron");
        $finish;
    end
endmodule
