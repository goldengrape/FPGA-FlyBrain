module kv260_marker_top_tb;
    logic [4:0] bank45_gpio;

    kv260_marker_top dut (
        .bank45_gpio(bank45_gpio)
    );

    initial begin
        #1;
        if (bank45_gpio !== 5'b10101) begin
            $fatal(1, "marker mismatch: got %b", bank45_gpio);
        end
        $display("PASS: kv260_marker_top emits 10101");
        $finish;
    end
endmodule
