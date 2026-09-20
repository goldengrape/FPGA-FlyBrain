// LAB-HW-03: first PL proof.
// No clock, reset, AXI, or Linux dependency: the only behavior is a stable marker.
module kv260_marker_top (
    output logic [4:0] bank45_gpio
);
    always_comb begin
        bank45_gpio = 5'b10101;
    end
endmodule
