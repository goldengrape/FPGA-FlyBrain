`timescale 1ns/1ps
module tutorial_if_neuron_tb;
  localparam int WIDTH=8;
  logic clk=0, rst_n=0;
  logic signed [WIDTH-1:0] input_current='0;
  logic signed [WIDTH-1:0] threshold=8'sd4, reset_value=8'sd0, membrane_v;
  logic spike;
  tutorial_if_neuron #(.WIDTH(WIDTH)) dut(.*);
  task automatic apply(input integer x,input integer exp_v,input bit exp_s);
    begin input_current=x; #4 clk=1; #1;
      if ($signed(membrane_v)!==exp_v) $fatal(1,"v got=%0d expected=%0d",$signed(membrane_v),exp_v);
      if (spike!==exp_s) $fatal(1,"spike got=%0d expected=%0d",spike,exp_s);
      #5 clk=0;
    end
  endtask
  initial begin
    $dumpfile("tutorial_if_neuron.vcd"); $dumpvars(0,tutorial_if_neuron_tb);
    #4 clk=1; #1; if ($signed(membrane_v)!==0 || spike!==0) $fatal(1,"reset failed"); #5 clk=0; rst_n=1;
    apply(1,1,0); apply(1,2,0); apply(1,3,0); apply(1,0,1); apply(2,2,0); apply(2,0,1);
    $display("PASS lesson08 tutorial_if_neuron"); $finish;
  end
endmodule
