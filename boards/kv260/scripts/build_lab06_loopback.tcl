# LAB-HW-06: build the minimal PS/Linux -> PL MMIO loopback.
# Runtime path:
#   PS M_AXI_HPM0_FPD -> SmartConnect -> dual-channel AXI GPIO @ 0xA0010000
# Channel 1 output drives kv260_loopback_transform; Channel 2 reads the result.

set script_dir [file dirname [file normalize [info script]]]
set board_dir [file normalize [file join $script_dir ..]]
set repo_root [file normalize [file join $board_dir .. ..]]
set build_dir [file join $repo_root build kv260 lab-hw-06]
set rtl_file [file join $board_dir rtl kv260_loopback_transform.sv]
set part_name "xck26-sfvc784-2LV-c"
set board_part_name "xilinx.com:kv260_som:part0:1.4"
set axi_gpio_base 0xA0010000

file delete -force $build_dir
file mkdir $build_dir

puts "FPGA_FLYBRAIN_LAB=LAB-HW-06"
puts "VIVADO_VERSION=[version -short]"
puts "FPGA_PART=$part_name"
puts "BOARD_PART=$board_part_name"
puts [format "AXI_GPIO_BASE=0x%08X" $axi_gpio_base]

if {[llength [get_board_parts -quiet $board_part_name]] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_KV260_BOARD_PART_1_4"
    exit 2
}

create_project lab_hw_06 $build_dir -part $part_name -force
set_property BOARD_PART $board_part_name [current_project]
add_files -norecurse $rtl_file

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
set_property -dict [list CONFIG.PSU__USE__M_AXI_GP0 {1}] [get_bd_cells ps]

set gpio_defs [get_ipdefs -all xilinx.com:ip:axi_gpio:*]
if {[llength $gpio_defs] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_AXI_GPIO"
    exit 4
}
set gpio_vlnv [get_property VLNV [lindex $gpio_defs end]]
create_bd_cell -type ip -vlnv $gpio_vlnv axi_gpio
set_property -dict [list \
    CONFIG.C_ALL_OUTPUTS {1} \
    CONFIG.C_ALL_INPUTS_2 {1} \
    CONFIG.C_GPIO_WIDTH {32} \
    CONFIG.C_GPIO2_WIDTH {32} \
    CONFIG.C_IS_DUAL {1} \
    CONFIG.C_INTERRUPT_PRESENT {0} \
] [get_bd_cells axi_gpio]

set smc_defs [get_ipdefs -all xilinx.com:ip:smartconnect:*]
if {[llength $smc_defs] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_SMARTCONNECT"
    exit 5
}
set smc_vlnv [get_property VLNV [lindex $smc_defs end]]
create_bd_cell -type ip -vlnv $smc_vlnv axi_smc
set_property -dict [list CONFIG.NUM_MI {1} CONFIG.NUM_SI {1}] [get_bd_cells axi_smc]

set rst_defs [get_ipdefs -all xilinx.com:ip:proc_sys_reset:*]
if {[llength $rst_defs] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_PROC_SYS_RESET"
    exit 6
}
set rst_vlnv [get_property VLNV [lindex $rst_defs end]]
create_bd_cell -type ip -vlnv $rst_vlnv rst

create_bd_cell -type module -reference kv260_loopback_transform loopback_core

connect_bd_intf_net [get_bd_intf_pins ps/M_AXI_HPM0_FPD] [get_bd_intf_pins axi_smc/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins axi_smc/M00_AXI] [get_bd_intf_pins axi_gpio/S_AXI]

connect_bd_net [get_bd_pins ps/pl_clk0] \
    [get_bd_pins ps/maxihpm0_fpd_aclk] \
    [get_bd_pins axi_smc/aclk] \
    [get_bd_pins axi_gpio/s_axi_aclk] \
    [get_bd_pins rst/slowest_sync_clk]

connect_bd_net [get_bd_pins ps/pl_resetn0] [get_bd_pins rst/ext_reset_in]
connect_bd_net [get_bd_pins rst/peripheral_aresetn] \
    [get_bd_pins axi_smc/aresetn] \
    [get_bd_pins axi_gpio/s_axi_aresetn]

connect_bd_net [get_bd_pins axi_gpio/gpio_io_o] [get_bd_pins loopback_core/write_value]
connect_bd_net [get_bd_pins loopback_core/read_value] [get_bd_pins axi_gpio/gpio2_io_i]

assign_bd_address \
    -offset $axi_gpio_base \
    -range 0x00010000 \
    -target_address_space [get_bd_addr_spaces ps/Data] \
    [get_bd_addr_segs axi_gpio/S_AXI/Reg] \
    -force

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
    exit 7
}

launch_runs impl_1 -to_step route_design -jobs 4
wait_on_run impl_1
set impl_status [get_property STATUS [get_runs impl_1]]
puts "IMPL_RUN_STATUS=$impl_status"
if {![string match "*Complete*" $impl_status]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=IMPLEMENTATION_RUN_FAILED"
    exit 8
}

open_run impl_1

set timing_report [file join $build_dir timing_summary.rpt]
set util_report [file join $build_dir utilization.rpt]
set drc_report [file join $build_dir drc.rpt]
set bit_file [file join $build_dir kv260_loopback.bit]

report_timing_summary -file $timing_report
report_utilization -file $util_report
report_drc -file $drc_report

set clocks [get_clocks -quiet]
puts "CLOCK_COUNT=[llength $clocks]"
if {[llength $clocks] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NO_IMPLEMENTED_CLOCK"
    exit 9
}

set setup_paths [get_timing_paths -quiet -setup -max_paths 1 -nworst 1]
set hold_paths [get_timing_paths -quiet -hold -max_paths 1 -nworst 1]
if {[llength $setup_paths] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NO_SETUP_TIMING_PATH"
    exit 10
}
if {[llength $hold_paths] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NO_HOLD_TIMING_PATH"
    exit 11
}

set setup_slack [get_property SLACK [lindex $setup_paths 0]]
set hold_slack [get_property SLACK [lindex $hold_paths 0]]
puts "TIMING_SETUP_WORST_SLACK_NS=$setup_slack"
puts "TIMING_HOLD_WORST_SLACK_NS=$hold_slack"

if {[expr {double($setup_slack) < 0.0}]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NEGATIVE_SETUP_SLACK"
    exit 12
}
if {[expr {double($hold_slack) < 0.0}]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NEGATIVE_HOLD_SLACK"
    exit 13
}

write_bitstream -force $bit_file

puts "TRANSPORT=PS_M_AXI_HPM0_FPD_TO_AXI_GPIO"
puts "GPIO_DATA_OFFSET=0x0000"
puts "GPIO2_DATA_OFFSET=0x0008"
puts "BITSTREAM=$bit_file"
puts "TIMING_REPORT=$timing_report"
puts "UTILIZATION_REPORT=$util_report"
puts "DRC_REPORT=$drc_report"
puts "STATUS=PASS"
exit 0
