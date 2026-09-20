module kv260_loopback_transform_tb;
    logic [31:0] write_value;
    logic [31:0] read_value;

    kv260_loopback_transform dut (
        .write_value(write_value),
        .read_value(read_value)
    );

    task automatic check_value(input logic [31:0] value, input logic [31:0] expected);
        begin
            write_value = value;
            #1;
            if (read_value !== expected) begin
                $fatal(1, "write=%08x expected=%08x read=%08x", value, expected, read_value);
            end
        end
    endtask

    initial begin
        check_value(32'h00000000, 32'h00000001);
        check_value(32'h00000001, 32'h00000002);
        check_value(32'h00000007, 32'h00000008);
        check_value(32'h12345678, 32'h12345679);
        check_value(32'hfffffffe, 32'hffffffff);
        check_value(32'hffffffff, 32'h00000000);
        $display("PASS: kv260_loopback_transform +1 modulo 2^32");
        $finish;
    end
endmodule
