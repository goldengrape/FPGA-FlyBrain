# LAB-HW-04: build a PS-clock/reset-driven PL blink proof.
# PS is used only as clock/reset infrastructure; this lab does not teach AXI/Linux.

set script_dir [file dirname [file normalize [info script]]]
set board_dir [file normalize [file join $script_dir ..]]
set repo_root [file normalize [file join $board_dir .. ..]]
set build_dir [file join $repo_root build kv260 lab-hw-04]
set rtl_file [file join $board_dir rtl kv260_blink_core.sv]
set xdc_file [file join $board_dir constraints bank45_gpio.xdc]
set part_name "xck26-sfvc784-2LV-c"
set board_part_name "xilinx.com:kv260_som:part0:1.4"

file delete -force $build_dir
file mkdir $build_dir

puts "FPGA_FLYBRAIN_LAB=LAB-HW-04"
puts "VIVADO_VERSION=[version -short]"
puts "FPGA_PART=$part_name"
puts "BOARD_PART=$board_part_name"

if {[llength [get_board_parts -quiet $board_part_name]] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_KV260_BOARD_PART_1_4"
    puts stderr "DETAIL=Install/refresh the KV260 board definition before LAB-HW-04."
    exit 2
}

create_project lab_hw_04 $build_dir -part $part_name -force
set_property BOARD_PART $board_part_name [current_project]
add_files -norecurse $rtl_file
add_files -fileset constrs_1 -norecurse $xdc_file

create_bd_design system
update_compile_order -fileset sources_1

set ps_defs [get_ipdefs -all xilinx.com:ip:zynq_ultra_ps_e:*]
if {[llength $ps_defs] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_ZYNQ_ULTRA_PS_E"
    exit 3
}
set ps_vlnv [get_property VLNV [lindex $ps_defs end]]
create_bd_cell -type ip -vlnv $ps_vlnv ps
apply_bd_automation -rule xilinx.com:bd_rule:zynq_ultra_ps_e -config {apply_board_preset "1"} [get_bd_cells ps]

set rst_defs [get_ipdefs -all xilinx.com:ip:proc_sys_reset:*]
if {[llength $rst_defs] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_PROC_SYS_RESET"
    exit 4
}
set rst_vlnv [get_property VLNV [lindex $rst_defs end]]
create_bd_cell -type ip -vlnv $rst_vlnv rst

create_bd_cell -type module -reference kv260_blink_core blink_core
create_bd_port -dir O -from 4 -to 0 bank45_gpio

connect_bd_net [get_bd_pins ps/pl_clk0] [get_bd_pins rst/slowest_sync_clk] [get_bd_pins blink_core/clk]
connect_bd_net [get_bd_pins ps/pl_resetn0] [get_bd_pins rst/ext_reset_in]
connect_bd_net [get_bd_pins rst/peripheral_aresetn] [get_bd_pins blink_core/resetn]
connect_bd_net [get_bd_pins blink_core/bank45_gpio] [get_bd_ports bank45_gpio]

validate_bd_design
save_bd_design
generate_target all [get_files system.bd]

set wrapper [make_wrapper -files [get_files system.bd] -top]
add_files -norecurse $wrapper
set_property top system_wrapper [current_fileset]

launch_runs synth_1 -jobs 4
wait_on_run synth_1
set synth_status [get_property STATUS [get_runs synth_1]]
puts "SYNTH_RUN_STATUS=$synth_status"
if {![string match "*Complete*" $synth_status]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=SYNTHESIS_RUN_FAILED"
    exit 5
}

# Stop at routed implementation. Timing is an oracle: do not create the
# bitstream until the routed design has real clocked paths and non-negative
# setup/hold slack.
launch_runs impl_1 -to_step route_design -jobs 4
wait_on_run impl_1
set impl_status [get_property STATUS [get_runs impl_1]]
puts "IMPL_RUN_STATUS=$impl_status"
if {![string match "*Complete*" $impl_status]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=IMPLEMENTATION_RUN_FAILED"
    exit 6
}

open_run impl_1

set timing_report [file join $build_dir timing_summary.rpt]
set util_report [file join $build_dir utilization.rpt]
set drc_report [file join $build_dir drc.rpt]
set bit_file [file join $build_dir kv260_blink.bit]

report_timing_summary -file $timing_report
report_utilization -file $util_report
report_drc -file $drc_report

set clocks [get_clocks -quiet]
puts "CLOCK_COUNT=[llength $clocks]"
if {[llength $clocks] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NO_IMPLEMENTED_CLOCK"
    exit 7
}

set setup_paths [get_timing_paths -quiet -setup -max_paths 1 -nworst 1]
if {[llength $setup_paths] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NO_SETUP_TIMING_PATH"
    exit 8
}
set hold_paths [get_timing_paths -quiet -hold -max_paths 1 -nworst 1]
if {[llength $hold_paths] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NO_HOLD_TIMING_PATH"
    exit 9
}

set setup_slack [get_property SLACK [lindex $setup_paths 0]]
set hold_slack [get_property SLACK [lindex $hold_paths 0]]
puts "TIMING_SETUP_WORST_SLACK_NS=$setup_slack"
puts "TIMING_HOLD_WORST_SLACK_NS=$hold_slack"

if {[expr {double($setup_slack) < 0.0}]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NEGATIVE_SETUP_SLACK"
    puts stderr "DETAIL=$setup_slack"
    exit 10
}
if {[expr {double($hold_slack) < 0.0}]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NEGATIVE_HOLD_SLACK"
    puts stderr "DETAIL=$hold_slack"
    exit 11
}

write_bitstream -force $bit_file

puts "CLOCK_SOURCE=ps/pl_clk0"
puts "RESET_SOURCE=ps/pl_resetn0->proc_sys_reset/peripheral_aresetn"
puts "DESIGN_LOCAL_RESET=blink_core/resetn(active-low)"
puts "BITSTREAM=$bit_file"
puts "TIMING_REPORT=$timing_report"
puts "UTILIZATION_REPORT=$util_report"
puts "DRC_REPORT=$drc_report"
puts "STATUS=PASS"
exit 0
