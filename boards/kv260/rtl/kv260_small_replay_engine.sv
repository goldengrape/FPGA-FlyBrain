// LAB-HW-08 fixed four-neuron replay engine.
//
// This is deliberately a board-level teaching replay harness for the exact
// Lesson-12 event machine. It is not the formal LIF neuron or MOD-004~009.
//
// Register contract:
//   control_word[0]   = start pulse/rising edge
//   control_word[31:1] = reserved; write zero
//   status_word[0]    = busy
//   status_word[1]    = done
//   status_word[2]    = error
//   status_word[7:4]  = spike_count
//   status_word[15:8] = event_count
//   status_word[31:16] = reserved
//
// Numeric/trace boundary:
//   - the frozen Lesson-12 fixture uses non-negative signed-8-bit weights;
//   - threshold comparison is therefore valid in this teaching slice;
//   - event trace stores accumulator_after_add[7:0] only;
//   - the fixed four-neuron topology can emit at most four spikes, so words
//     16..19 cannot overlap SPIKE_COUNT_WORD=20. Widening the network requires
//     revisiting this memory map and the oracle.
module kv260_small_replay_engine (
    input  logic        clk,
    input  logic        resetn,
    input  logic [31:0] control_word,
    output logic [31:0] status_word,

    output logic        mem_en,
    output logic        mem_we,
    output logic [31:0] mem_addr,
    output logic [31:0] mem_wdata,
    input  logic [31:0] mem_rdata
);

    localparam int SPIKE_TRACE_BASE_WORD = 16;
    localparam int SPIKE_COUNT_WORD      = 20;
    localparam int EVENT_TRACE_BASE_WORD = 32;
    localparam int EVENT_COUNT_WORD      = 36;

    typedef enum logic [3:0] {
        S_IDLE,
        S_POP,
        S_WRITE_SPIKE,
        S_EDGE_SETUP,
        S_READ_REQ,
        S_READ_CAPTURE,
        S_WRITE_STATE,
        S_WRITE_EVENT,
        S_WRITE_SPIKE_COUNT,
        S_WRITE_EVENT_COUNT,
        S_DONE
    } state_t;

    state_t state;

    logic start_d;
    logic busy;
    logic done;
    logic error_flag;

    logic [1:0] queue_mem [0:7];
    logic [2:0] q_head;
    logic [2:0] q_tail;
    logic [3:0] q_count;

    logic [1:0] current_source;
    logic [1:0] current_target;
    logic signed [7:0] current_weight;
    logic [2:0] edge_start;
    logic [2:0] edge_count;
    logic [2:0] edge_pos;

    logic [31:0] accumulator_after_add;
    logic event_spiked;

    logic [3:0] spike_count;
    logic [7:0] event_count;

    function automatic [2:0] source_edge_start(input logic [1:0] source);
        case (source)
            2'd0: source_edge_start = 3'd0;
            2'd1: source_edge_start = 3'd2;
            2'd2: source_edge_start = 3'd3;
            default: source_edge_start = 3'd4;
        endcase
    endfunction

    function automatic [2:0] source_edge_count(input logic [1:0] source);
        case (source)
            2'd0: source_edge_count = 3'd2;
            2'd1: source_edge_count = 3'd1;
            2'd2: source_edge_count = 3'd1;
            default: source_edge_count = 3'd0;
        endcase
    endfunction

    function automatic [1:0] record_target(input logic [2:0] record_index);
        case (record_index)
            3'd0: record_target = 2'd1;
            3'd1: record_target = 2'd2;
            3'd2: record_target = 2'd3;
            default: record_target = 2'd3;
        endcase
    endfunction

    function automatic signed [7:0] record_weight(input logic [2:0] record_index);
        case (record_index)
            3'd0: record_weight = 8'sd2;
            3'd1: record_weight = 8'sd1;
            3'd2: record_weight = 8'sd2;
            default: record_weight = 8'sd1;
        endcase
    endfunction

    function automatic [31:0] target_threshold(input logic [1:0] target);
        case (target)
            2'd0: target_threshold = 32'd99;
            2'd1: target_threshold = 32'd2;
            2'd2: target_threshold = 32'd1;
            default: target_threshold = 32'd3;
        endcase
    endfunction

    function automatic [31:0] encode_event(
        input logic [1:0] source,
        input logic [1:0] target,
        input logic signed [7:0] weight,
        input logic [31:0] after_add,
        input logic spiked
    );
        encode_event = {
            2'b00, source,
            2'b00, target,
            weight[7:0],
            after_add[7:0],
            7'b0,
            spiked
        };
    endfunction

    always_comb begin
        mem_en = 1'b0;
        mem_we = 1'b0;
        mem_addr = 32'd0;
        mem_wdata = 32'd0;

        case (state)
            S_WRITE_SPIKE: begin
                mem_en = 1'b1;
                mem_we = 1'b1;
                mem_addr = (SPIKE_TRACE_BASE_WORD * 4) + {26'd0, spike_count, 2'b00};
                mem_wdata = {30'd0, current_source};
            end

            S_READ_REQ: begin
                mem_en = 1'b1;
                mem_we = 1'b0;
                mem_addr = {28'd0, current_target, 2'b00};
            end

            S_WRITE_STATE: begin
                mem_en = 1'b1;
                mem_we = 1'b1;
                mem_addr = {28'd0, current_target, 2'b00};
                mem_wdata = event_spiked ? 32'd0 : accumulator_after_add;
            end

            S_WRITE_EVENT: begin
                mem_en = 1'b1;
                mem_we = 1'b1;
                mem_addr = (EVENT_TRACE_BASE_WORD * 4) + {22'd0, event_count, 2'b00};
                mem_wdata = encode_event(
                    current_source,
                    current_target,
                    current_weight,
                    accumulator_after_add,
                    event_spiked
                );
            end

            S_WRITE_SPIKE_COUNT: begin
                mem_en = 1'b1;
                mem_we = 1'b1;
                mem_addr = SPIKE_COUNT_WORD * 4;
                mem_wdata = {28'd0, spike_count};
            end

            S_WRITE_EVENT_COUNT: begin
                mem_en = 1'b1;
                mem_we = 1'b1;
                mem_addr = EVENT_COUNT_WORD * 4;
                mem_wdata = {24'd0, event_count};
            end

            default: begin
            end
        endcase
    end

    always_comb begin
        status_word = 32'd0;
        status_word[0] = busy;
        status_word[1] = done;
        status_word[2] = error_flag;
        status_word[7:4] = spike_count;
        status_word[15:8] = event_count;
    end

    always_ff @(posedge clk) begin
        if (!resetn) begin
            state <= S_IDLE;
            start_d <= 1'b0;
            busy <= 1'b0;
            done <= 1'b0;
            error_flag <= 1'b0;
            q_head <= 3'd0;
            q_tail <= 3'd0;
            q_count <= 4'd0;
            current_source <= 2'd0;
            current_target <= 2'd0;
            current_weight <= 8'sd0;
            edge_start <= 3'd0;
            edge_count <= 3'd0;
            edge_pos <= 3'd0;
            accumulator_after_add <= 32'd0;
            event_spiked <= 1'b0;
            spike_count <= 4'd0;
            event_count <= 8'd0;
        end else begin
            start_d <= control_word[0];

            case (state)
                S_IDLE: begin
                    busy <= 1'b0;
                    if (!control_word[0]) begin
                        done <= 1'b0;
                    end
                    if (control_word[0] && !start_d) begin
                        queue_mem[0] <= 2'd0;
                        q_head <= 3'd0;
                        q_tail <= 3'd1;
                        q_count <= 4'd1;
                        spike_count <= 4'd0;
                        event_count <= 8'd0;
                        error_flag <= 1'b0;
                        done <= 1'b0;
                        busy <= 1'b1;
                        state <= S_POP;
                    end
                end

                S_POP: begin
                    if (q_count == 0) begin
                        state <= S_WRITE_SPIKE_COUNT;
                    end else begin
                        current_source <= queue_mem[q_head];
                        q_head <= q_head + 3'd1;
                        q_count <= q_count - 4'd1;
                        state <= S_WRITE_SPIKE;
                    end
                end

                S_WRITE_SPIKE: begin
                    spike_count <= spike_count + 4'd1;
                    edge_start <= source_edge_start(current_source);
                    edge_count <= source_edge_count(current_source);
                    edge_pos <= 3'd0;
                    state <= S_EDGE_SETUP;
                end

                S_EDGE_SETUP: begin
                    if (edge_pos >= edge_count) begin
                        state <= S_POP;
                    end else begin
                        current_target <= record_target(edge_start + edge_pos);
                        current_weight <= record_weight(edge_start + edge_pos);
                        state <= S_READ_REQ;
                    end
                end

                S_READ_REQ: begin
                    state <= S_READ_CAPTURE;
                end

                S_READ_CAPTURE: begin
                    accumulator_after_add <= mem_rdata + {{24{current_weight[7]}}, current_weight};
                    event_spiked <=
                        (mem_rdata + {{24{current_weight[7]}}, current_weight})
                        >= target_threshold(current_target);
                    state <= S_WRITE_STATE;
                end

                S_WRITE_STATE: begin
                    if (event_spiked) begin
                        if (q_count >= 4'd8) begin
                            error_flag <= 1'b1;
                            state <= S_WRITE_SPIKE_COUNT;
                        end else begin
                            queue_mem[q_tail] <= current_target;
                            q_tail <= q_tail + 3'd1;
                            q_count <= q_count + 4'd1;
                            state <= S_WRITE_EVENT;
                        end
                    end else begin
                        state <= S_WRITE_EVENT;
                    end
                end

                S_WRITE_EVENT: begin
                    event_count <= event_count + 8'd1;
                    edge_pos <= edge_pos + 3'd1;
                    state <= S_EDGE_SETUP;
                end

                S_WRITE_SPIKE_COUNT: begin
                    state <= S_WRITE_EVENT_COUNT;
                end

                S_WRITE_EVENT_COUNT: begin
                    state <= S_DONE;
                end

                S_DONE: begin
                    busy <= 1'b0;
                    done <= 1'b1;
                    if (!control_word[0]) begin
                        done <= 1'b0;
                        state <= S_IDLE;
                    end
                end

                default: begin
                    error_flag <= 1'b1;
                    busy <= 1'b0;
                    done <= 1'b1;
                    state <= S_DONE;
                end
            endcase
        end
    end

endmodule
