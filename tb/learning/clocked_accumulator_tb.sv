`timescale 1ns/1ps
module clocked_accumulator_tb;
  localparam int WIDTH=8;
  logic clk=0, rst_n=0;
  logic signed [WIDTH-1:0] input_value='0;
  logic signed [WIDTH-1:0] state;
  clocked_accumulator #(.WIDTH(WIDTH)) dut(.*);
  task automatic tick(input integer x,input integer exp);
    begin input_value=x; #4 clk=1; #1;
      if ($signed(state)!==exp) $fatal(1,"state got=%0d expected=%0d",$signed(state),exp);
      #5 clk=0;
    end
  endtask
  initial begin
    #4 clk=1; #1; if ($signed(state)!==0) $fatal(1,"reset failed"); #5 clk=0; rst_n=1;
    tick(1,1); tick(2,3); tick(3,6);
    $display("PASS lesson06 clocked_accumulator"); $finish;
  end
endmodule
