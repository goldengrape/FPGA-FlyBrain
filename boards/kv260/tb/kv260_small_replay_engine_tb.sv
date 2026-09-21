module kv260_small_replay_engine_tb;
    logic clk = 1'b0;
    logic resetn = 1'b0;
    logic [31:0] control_word = 32'd0;
    logic [31:0] status_word;

    logic        a_en = 1'b0;
    logic [3:0]  a_we = 4'h0;
    logic [31:0] a_addr = 32'd0;
    logic [31:0] a_wrdata = 32'd0;
    logic [31:0] a_rddata;

    logic        b_en;
    logic        b_we;
    logic [31:0] b_addr;
    logic [31:0] b_wdata;
    logic [31:0] b_rdata;

    always #5 clk = ~clk;

    kv260_replay_state_store store (
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
        .b_wrdata(b_wdata),
        .b_rddata(b_rdata)
    );

    kv260_small_replay_engine engine (
        .clk(clk),
        .resetn(resetn),
        .control_word(control_word),
        .status_word(status_word),
        .mem_en(b_en),
        .mem_we(b_we),
        .mem_addr(b_addr),
        .mem_wdata(b_wdata),
        .mem_rdata(b_rdata)
    );

    task automatic host_write_word(input integer index, input logic [31:0] value);
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

    task automatic host_check_word(input integer index, input logic [31:0] expected);
        begin
            @(negedge clk);
            a_en = 1'b1;
            a_we = 4'h0;
            a_addr = index * 4;
            @(posedge clk);
            #1;
            if (a_rddata !== expected) begin
                $fatal(
                    1,
                    "word=%0d expected=%08x read=%08x",
                    index,
                    expected,
                    a_rddata
                );
            end
            @(negedge clk);
            a_en = 1'b0;
        end
    endtask

    integer cycles;

    initial begin
        repeat (3) @(posedge clk);
        @(negedge clk);
        resetn = 1'b1;

        // Lesson-12 fixture initial accumulator state.
        host_write_word(0, 32'd0);
        host_write_word(1, 32'd0);
        host_write_word(2, 32'd0);
        host_write_word(3, 32'd0);

        // Clear trace/count words so stale data cannot accidentally satisfy checks.
        host_write_word(16, 32'hdeadbeef);
        host_write_word(17, 32'hdeadbeef);
        host_write_word(18, 32'hdeadbeef);
        host_write_word(19, 32'hdeadbeef);
        host_write_word(20, 32'hdeadbeef);
        host_write_word(32, 32'hdeadbeef);
        host_write_word(33, 32'hdeadbeef);
        host_write_word(34, 32'hdeadbeef);
        host_write_word(35, 32'hdeadbeef);
        host_write_word(36, 32'hdeadbeef);

        @(negedge clk);
        control_word = 32'h00000001;

        cycles = 0;
        while (!status_word[1] && cycles < 500) begin
            @(posedge clk);
            cycles = cycles + 1;
        end

        if (!status_word[1]) begin
            $fatal(1, "engine timeout");
        end
        if (status_word[2]) begin
            $fatal(1, "engine error flag set");
        end
        if (status_word[7:4] !== 4'd4) begin
            $fatal(1, "status spike_count expected 4 got %0d", status_word[7:4]);
        end
        if (status_word[15:8] !== 8'd4) begin
            $fatal(1, "status event_count expected 4 got %0d", status_word[15:8]);
        end

        // Holding start high after completion must not retrigger the engine.
        repeat (10) begin
            @(posedge clk);
            if (!status_word[1] || status_word[0]) begin
                $fatal(1, "held-high start unexpectedly changed done/busy");
            end
            if (status_word[7:4] !== 4'd4 || status_word[15:8] !== 8'd4) begin
                $fatal(1, "held-high start unexpectedly changed counters");
            end
        end

        @(negedge clk);
        control_word = 32'd0;
        repeat (2) @(posedge clk);

        // Final accumulator state.
        host_check_word(0, 32'd0);
        host_check_word(1, 32'd0);
        host_check_word(2, 32'd0);
        host_check_word(3, 32'd0);

        // Spike trace [0,1,2,3] and count 4.
        host_check_word(16, 32'd0);
        host_check_word(17, 32'd1);
        host_check_word(18, 32'd2);
        host_check_word(19, 32'd3);
        host_check_word(20, 32'd4);

        // Event encoding matches lab08_replay_reference.py.
        host_check_word(32, 32'h01020201);
        host_check_word(33, 32'h02010101);
        host_check_word(34, 32'h13020200);
        host_check_word(35, 32'h23010301);
        host_check_word(36, 32'd4);

        // A new rising edge after returning start low must launch a clean second run.
        @(negedge clk);
        control_word = 32'h00000001;
        cycles = 0;
        while (!status_word[1] && cycles < 500) begin
            @(posedge clk);
            cycles = cycles + 1;
        end
        if (!status_word[1] || status_word[2]) begin
            $fatal(1, "second replay did not complete cleanly");
        end
        if (status_word[7:4] !== 4'd4 || status_word[15:8] !== 8'd4) begin
            $fatal(1, "second replay counters mismatch");
        end

        @(negedge clk);
        control_word = 32'd0;
        repeat (2) @(posedge clk);

        $display("PASS: LAB-HW-08 Lesson-12 four-neuron replay trace and control behavior");
        $finish;
    end
endmodule
