// LAB-HW-04: clock/reset/I/O proof.
// clk is supplied by PS pl_clk0. resetn is the synchronized design-local reset
// from proc_sys_reset/peripheral_aresetn; it is not the physical SW2 signal.
module kv260_blink_core #(
    parameter int COUNTER_WIDTH = 26
) (
    input  logic       clk,
    input  logic       resetn,
    output logic [4:0] bank45_gpio
);
    logic [COUNTER_WIDTH-1:0] counter;

    always_ff @(posedge clk) begin
        if (!resetn) begin
            counter <= '0;
        end else begin
            counter <= counter + 1'b1;
        end
    end

    always_comb begin
        bank45_gpio = 5'b10100;
        bank45_gpio[0] = counter[COUNTER_WIDTH-1];
    end
endmodule
