module kv260_blink_core_tb;
    logic clk = 1'b0;
    logic resetn = 1'b0;
    logic [4:0] bank45_gpio;

    always #5 clk = ~clk;

    kv260_blink_core #(
        .COUNTER_WIDTH(4)
    ) dut (
        .clk(clk),
        .resetn(resetn),
        .bank45_gpio(bank45_gpio)
    );

    task automatic expect_gpio(input logic expected_bit0, input string label_text);
        #1;
        if (bank45_gpio[4:1] !== 4'b1010) begin
            $fatal(1, "%s: marker bits changed: %b", label_text, bank45_gpio[4:1]);
        end
        if (bank45_gpio[0] !== expected_bit0) begin
            $fatal(1, "%s: blink bit expected %b got %b", label_text, expected_bit0, bank45_gpio[0]);
        end
    endtask

    initial begin
        repeat (2) @(posedge clk);
        expect_gpio(1'b0, "held reset");

        resetn = 1'b1;
        repeat (8) @(posedge clk);
        expect_gpio(1'b1, "after eight counts");

        repeat (8) @(posedge clk);
        expect_gpio(1'b0, "after counter wrap");

        resetn = 1'b0;
        @(posedge clk);
        expect_gpio(1'b0, "reset asserted again");

        $display("PASS: kv260_blink_core clock/reset behavior");
        $finish;
    end
endmodule
