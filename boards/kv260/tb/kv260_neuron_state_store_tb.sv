module kv260_neuron_state_store_tb;
    logic        bram_clk = 1'b0;
    logic        bram_rst = 1'b1;
    logic        bram_en = 1'b0;
    logic [3:0]  bram_we = 4'h0;
    logic [31:0] bram_addr = 32'd0;
    logic [31:0] bram_wrdata = 32'd0;
    logic [31:0] bram_rddata;

    kv260_neuron_state_store dut (
        .bram_clk(bram_clk),
        .bram_rst(bram_rst),
        .bram_en(bram_en),
        .bram_we(bram_we),
        .bram_addr(bram_addr),
        .bram_wrdata(bram_wrdata),
        .bram_rddata(bram_rddata)
    );

    always #5 bram_clk = ~bram_clk;

    task automatic write_word(input logic [9:0] index, input logic [31:0] value);
        begin
            @(negedge bram_clk);
            bram_en = 1'b1;
            bram_we = 4'hf;
            bram_addr = {20'd0, index, 2'b00};
            bram_wrdata = value;
            @(posedge bram_clk);
            #1;
            @(negedge bram_clk);
            bram_en = 1'b0;
            bram_we = 4'h0;
        end
    endtask

    task automatic read_word(input logic [9:0] index, input logic [31:0] expected);
        logic [31:0] before_edge;
        begin
            @(negedge bram_clk);
            before_edge = bram_rddata;
            bram_en = 1'b1;
            bram_we = 4'h0;
            bram_addr = {20'd0, index, 2'b00};

            // Synchronous-read proof: changing the address does not immediately
            // change the registered output before the active clock edge.
            #1;
            if (bram_rddata !== before_edge) begin
                $fatal(1, "read data changed before clock edge");
            end

            @(posedge bram_clk);
            #1;
            if (bram_rddata !== expected) begin
                $fatal(
                    1,
                    "index=%0d expected=%08x read=%08x",
                    index,
                    expected,
                    bram_rddata
                );
            end

            @(negedge bram_clk);
            bram_en = 1'b0;
        end
    endtask

    task automatic check_read_first(
        input logic [9:0] index,
        input logic [31:0] old_value,
        input logic [31:0] new_value
    );
        begin
            @(negedge bram_clk);
            bram_en = 1'b1;
            bram_we = 4'hf;
            bram_addr = {20'd0, index, 2'b00};
            bram_wrdata = new_value;

            @(posedge bram_clk);
            #1;
            if (bram_rddata !== old_value) begin
                $fatal(
                    1,
                    "read-first mismatch index=%0d old=%08x observed=%08x",
                    index,
                    old_value,
                    bram_rddata
                );
            end

            @(negedge bram_clk);
            bram_en = 1'b0;
            bram_we = 4'h0;
        end
    endtask

    initial begin
        repeat (2) @(posedge bram_clk);
        @(negedge bram_clk);
        bram_rst = 1'b0;

        write_word(10'd0,    32'h10203040);
        write_word(10'd1,    32'h11223344);
        write_word(10'd7,    32'h55667788);
        write_word(10'd31,   32'h89abcdef);
        write_word(10'd511,  32'h13579bdf);
        write_word(10'd1023, 32'hffffffff);

        read_word(10'd0,    32'h10203040);
        read_word(10'd1,    32'h11223344);
        read_word(10'd7,    32'h55667788);
        read_word(10'd31,   32'h89abcdef);
        read_word(10'd511,  32'h13579bdf);
        read_word(10'd1023, 32'hffffffff);

        check_read_first(10'd31, 32'h89abcdef, 32'hcafebabe);
        read_word(10'd31, 32'hcafebabe);

        // Neighbor preservation catches accidental address aliasing.
        read_word(10'd7,    32'h55667788);
        read_word(10'd511,  32'h13579bdf);
        read_word(10'd1023, 32'hffffffff);

        $display("PASS: kv260_neuron_state_store synchronous multi-address BRAM semantics");
        $finish;
    end
endmodule
