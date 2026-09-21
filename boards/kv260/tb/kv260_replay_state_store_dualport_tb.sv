module kv260_replay_state_store_dualport_tb;
    logic clk = 1'b0;
    logic resetn = 1'b0;

    logic        a_en = 1'b0;
    logic [3:0]  a_we = 4'h0;
    logic [31:0] a_addr = 32'd0;
    logic [31:0] a_wrdata = 32'd0;
    logic [31:0] a_rddata;

    logic        b_en = 1'b0;
    logic        b_we = 1'b0;
    logic [31:0] b_addr = 32'd0;
    logic [31:0] b_wrdata = 32'd0;
    logic [31:0] b_rddata;

    always #5 clk = ~clk;

    kv260_replay_state_store dut (
        .a_clk(clk),
        .a_rst(!resetn),
        .a_en(a_en),
        .a_we(a_we),
        .a_addr(a_addr),
        .a_wrdata(a_wrdata),
        .a_rddata(a_rddata),
        .b_clk(clk),
        .b_rst(!resetn),
        .b_en(b_en),
        .b_we(b_we),
        .b_addr(b_addr),
        .b_wrdata(b_wrdata),
        .b_rddata(b_rddata)
    );

    task automatic a_write(input integer index, input logic [31:0] value);
        begin
            @(negedge clk);
            a_en = 1'b1;
            a_we = 4'hf;
            a_addr = index * 4;
            a_wrdata = value;
            @(posedge clk);
            #1;
            @(negedge clk);
            a_en = 1'b0;
            a_we = 4'h0;
        end
    endtask

    task automatic b_write(input integer index, input logic [31:0] value);
        begin
            @(negedge clk);
            b_en = 1'b1;
            b_we = 1'b1;
            b_addr = index * 4;
            b_wrdata = value;
            @(posedge clk);
            #1;
            @(negedge clk);
            b_en = 1'b0;
            b_we = 1'b0;
        end
    endtask

    task automatic a_read(input integer index, input logic [31:0] expected);
        begin
            @(negedge clk);
            a_en = 1'b1;
            a_we = 4'h0;
            a_addr = index * 4;
            @(posedge clk);
            #1;
            if (a_rddata !== expected) begin
                $fatal(1, "Port A word=%0d expected=%08x read=%08x", index, expected, a_rddata);
            end
            @(negedge clk);
            a_en = 1'b0;
        end
    endtask

    task automatic b_read(input integer index, input logic [31:0] expected);
        begin
            @(negedge clk);
            b_en = 1'b1;
            b_we = 1'b0;
            b_addr = index * 4;
            @(posedge clk);
            #1;
            if (b_rddata !== expected) begin
                $fatal(1, "Port B word=%0d expected=%08x read=%08x", index, expected, b_rddata);
            end
            @(negedge clk);
            b_en = 1'b0;
        end
    endtask

    initial begin
        repeat (3) @(posedge clk);
        @(negedge clk);
        resetn = 1'b1;

        a_write(3, 32'h11223344);
        b_read(3, 32'h11223344);

        b_write(7, 32'h55667788);
        a_read(7, 32'h55667788);

        // Port-A partial byte enables are outside the teaching contract and
        // must not alter the stored word.
        @(negedge clk);
        a_en = 1'b1;
        a_we = 4'b0011;
        a_addr = 3 * 4;
        a_wrdata = 32'hdeadbeef;
        @(posedge clk);
        #1;
        @(negedge clk);
        a_en = 1'b0;
        a_we = 4'h0;
        a_read(3, 32'h11223344);

        // Same clock, different addresses: both ports may write independently.
        @(negedge clk);
        a_en = 1'b1;
        a_we = 4'hf;
        a_addr = 9 * 4;
        a_wrdata = 32'haaaaaaaa;
        b_en = 1'b1;
        b_we = 1'b1;
        b_addr = 10 * 4;
        b_wrdata = 32'hbbbbbbbb;
        @(posedge clk);
        #1;
        @(negedge clk);
        a_en = 1'b0;
        a_we = 4'h0;
        b_en = 1'b0;
        b_we = 1'b0;

        a_read(9, 32'haaaaaaaa);
        b_read(10, 32'hbbbbbbbb);
        b_read(9, 32'haaaaaaaa);
        a_read(10, 32'hbbbbbbbb);

        // Resets clear only registered read outputs, not BRAM contents.
        @(negedge clk);
        resetn = 1'b0;
        repeat (2) @(posedge clk);
        #1;
        if (a_rddata !== 32'd0 || b_rddata !== 32'd0) begin
            $fatal(1, "reset did not clear registered read outputs");
        end
        @(negedge clk);
        resetn = 1'b1;
        a_read(3, 32'h11223344);
        b_read(7, 32'h55667788);

        $display("PASS: kv260_replay_state_store same-clock dual-port teaching contract");
        $finish;
    end
endmodule
