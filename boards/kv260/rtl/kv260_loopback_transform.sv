// LAB-HW-06: the smallest visible PL operation behind the MMIO teaching adapter.
// The AXI GPIO IP stores the host write. This core transforms the 32-bit value.
// Full AXI behavior is intentionally kept outside the learner-written RTL.
module kv260_loopback_transform (
    input  logic [31:0] write_value,
    output logic [31:0] read_value
);
    always_comb begin
        read_value = write_value + 32'd1;
    end
endmodule
