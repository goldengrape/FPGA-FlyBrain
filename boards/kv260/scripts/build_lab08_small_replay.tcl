# LAB-HW-08: build the fixed Lesson-12 four-neuron replay.
#
# PS-visible paths:
#   0xA0000000: 4 KiB shared state/trace BRAM through AXI BRAM Controller
#   0xA0010000: dual-channel AXI GPIO control/status
#
# Host accesses BRAM only while engine busy=0. No concurrent arbitration is taught.

set script_dir [file dirname [file normalize [info script]]]
set board_dir [file normalize [file join $script_dir ..]]
set repo_root [file normalize [file join $board_dir .. ..]]
set build_dir [file join $repo_root build kv260 lab-hw-08]

set state_rtl [file join $board_dir rtl kv260_replay_state_store.sv]
set engine_rtl [file join $board_dir rtl kv260_small_replay_engine.sv]

set part_name "xck26-sfvc784-2LV-c"
set board_part_name "xilinx.com:kv260_som:part0:1.4"
set state_base 0xA0000000
set state_range 0x00001000
set gpio_base 0xA0010000
set gpio_range 0x00010000

file delete -force $build_dir
file mkdir $build_dir

puts "FPGA_FLYBRAIN_LAB=LAB-HW-08"
puts "FIXTURE_ID=lesson12_four_neuron_replay_v1"
puts "VIVADO_VERSION=[version -short]"
puts "FPGA_PART=$part_name"
puts "BOARD_PART=$board_part_name"
puts [format "STATE_BASE=0x%08X" $state_base]
puts [format "STATE_RANGE=0x%08X" $state_range]
puts [format "CONTROL_BASE=0x%08X" $gpio_base]
puts "ADDRESS_REFERENCE=Xilinx/kria-base-hardware:k26_starter_kits/base_gpio_bram"

if {[llength [get_board_parts -quiet $board_part_name]] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_KV260_BOARD_PART_1_4"
    exit 2
}

create_project lab_hw_08 $build_dir -part $part_name -force
set_property BOARD_PART $board_part_name [current_project]
add_files -norecurse [list $state_rtl $engine_rtl]

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

set bram_defs [get_ipdefs -all xilinx.com:ip:axi_bram_ctrl:*]
if {[llength $bram_defs] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_AXI_BRAM_CTRL"
    exit 4
}
set bram_vlnv [get_property VLNV [lindex $bram_defs end]]
create_bd_cell -type ip -vlnv $bram_vlnv axi_bram
set_property -dict [list     CONFIG.ECC_TYPE {0}     CONFIG.PROTOCOL {AXI4LITE}     CONFIG.SINGLE_PORT_BRAM {1} ] [get_bd_cells axi_bram]

set gpio_defs [get_ipdefs -all xilinx.com:ip:axi_gpio:*]
if {[llength $gpio_defs] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_AXI_GPIO"
    exit 5
}
set gpio_vlnv [get_property VLNV [lindex $gpio_defs end]]
create_bd_cell -type ip -vlnv $gpio_vlnv axi_gpio
set_property -dict [list     CONFIG.C_ALL_OUTPUTS {1}     CONFIG.C_ALL_INPUTS_2 {1}     CONFIG.C_GPIO_WIDTH {32}     CONFIG.C_GPIO2_WIDTH {32}     CONFIG.C_IS_DUAL {1}     CONFIG.C_INTERRUPT_PRESENT {0} ] [get_bd_cells axi_gpio]

set smc_defs [get_ipdefs -all xilinx.com:ip:smartconnect:*]
if {[llength $smc_defs] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_SMARTCONNECT"
    exit 6
}
set smc_vlnv [get_property VLNV [lindex $smc_defs end]]
create_bd_cell -type ip -vlnv $smc_vlnv axi_smc
set_property -dict [list CONFIG.NUM_MI {2} CONFIG.NUM_SI {1}] [get_bd_cells axi_smc]

set rst_defs [get_ipdefs -all xilinx.com:ip:proc_sys_reset:*]
if {[llength $rst_defs] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_PROC_SYS_RESET"
    exit 7
}
set rst_vlnv [get_property VLNV [lindex $rst_defs end]]
create_bd_cell -type ip -vlnv $rst_vlnv rst

create_bd_cell -type module -reference kv260_replay_state_store state_store
create_bd_cell -type module -reference kv260_small_replay_engine replay_engine

connect_bd_intf_net [get_bd_intf_pins ps/M_AXI_HPM0_FPD] [get_bd_intf_pins axi_smc/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins axi_smc/M00_AXI] [get_bd_intf_pins axi_bram/S_AXI]
connect_bd_intf_net [get_bd_intf_pins axi_smc/M01_AXI] [get_bd_intf_pins axi_gpio/S_AXI]
connect_bd_intf_net [get_bd_intf_pins axi_bram/BRAM_PORTA] [get_bd_intf_pins state_store/BRAM_PORTA]

connect_bd_net [get_bd_pins ps/pl_clk0]     [get_bd_pins ps/maxihpm0_fpd_aclk]     [get_bd_pins axi_smc/aclk]     [get_bd_pins axi_bram/s_axi_aclk]     [get_bd_pins axi_gpio/s_axi_aclk]     [get_bd_pins rst/slowest_sync_clk]     [get_bd_pins state_store/b_clk]     [get_bd_pins replay_engine/clk]

connect_bd_net [get_bd_pins ps/pl_resetn0] [get_bd_pins rst/ext_reset_in]
connect_bd_net [get_bd_pins rst/peripheral_aresetn]     [get_bd_pins axi_smc/aresetn]     [get_bd_pins axi_bram/s_axi_aresetn]     [get_bd_pins axi_gpio/s_axi_aresetn]     [get_bd_pins replay_engine/resetn]
connect_bd_net [get_bd_pins rst/peripheral_reset] [get_bd_pins state_store/b_rst]

connect_bd_net [get_bd_pins axi_gpio/gpio_io_o] [get_bd_pins replay_engine/control_word]
connect_bd_net [get_bd_pins replay_engine/status_word] [get_bd_pins axi_gpio/gpio2_io_i]

connect_bd_net [get_bd_pins replay_engine/mem_en] [get_bd_pins state_store/b_en]
connect_bd_net [get_bd_pins replay_engine/mem_we] [get_bd_pins state_store/b_we]
connect_bd_net [get_bd_pins replay_engine/mem_addr] [get_bd_pins state_store/b_addr]
connect_bd_net [get_bd_pins replay_engine/mem_wdata] [get_bd_pins state_store/b_wrdata]
connect_bd_net [get_bd_pins state_store/b_rddata] [get_bd_pins replay_engine/mem_rdata]

assign_bd_address     -offset $state_base     -range $state_range     -target_address_space [get_bd_addr_spaces ps/Data]     [get_bd_addr_segs axi_bram/S_AXI/Mem0]     -force

assign_bd_address     -offset $gpio_base     -range $gpio_range     -target_address_space [get_bd_addr_spaces ps/Data]     [get_bd_addr_segs axi_gpio/S_AXI/Reg]     -force

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
    exit 8
}

launch_runs impl_1 -to_step route_design -jobs 4
wait_on_run impl_1
set impl_status [get_property STATUS [get_runs impl_1]]
puts "IMPL_RUN_STATUS=$impl_status"
if {![string match "*Complete*" $impl_status]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=IMPLEMENTATION_RUN_FAILED"
    exit 9
}

open_run impl_1

set timing_report [file join $build_dir timing_summary.rpt]
set util_report [file join $build_dir utilization.rpt]
set drc_report [file join $build_dir drc.rpt]
set bit_file [file join $build_dir kv260_small_replay.bit]

report_timing_summary -file $timing_report
report_utilization -file $util_report
report_drc -file $drc_report

set drc_errors [get_drc_violations -quiet -filter {SEVERITY == "Error"}]
puts "DRC_ERROR_COUNT=[llength $drc_errors]"
if {[llength $drc_errors] > 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=DRC_ERROR_PRESENT"
    exit 10
}

set setup_paths [get_timing_paths -quiet -setup -max_paths 1 -nworst 1]
set hold_paths [get_timing_paths -quiet -hold -max_paths 1 -nworst 1]
if {[llength $setup_paths] == 0 || [llength $hold_paths] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_TIMING_PATH"
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

set ramb18_cells [get_cells -quiet -hier -filter {REF_NAME =~ RAMB18*}]
set ramb36_cells [get_cells -quiet -hier -filter {REF_NAME =~ RAMB36*}]
set bram_primitive_count [expr {[llength $ramb18_cells] + [llength $ramb36_cells]}]
puts "RAMB18_COUNT=[llength $ramb18_cells]"
puts "RAMB36_COUNT=[llength $ramb36_cells]"
puts "BRAM_PRIMITIVE_COUNT=$bram_primitive_count"
if {$bram_primitive_count < 1} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NO_BLOCK_RAM_PRIMITIVE"
    exit 14
}

write_bitstream -force $bit_file

puts "TRANSPORT=FIXED_BRAM_PLUS_AXI_GPIO_CONTROL"
puts "GPIO_DATA_OFFSET=0x0000"
puts "GPIO2_DATA_OFFSET=0x0008"
puts "STATUS_BITS=busy:0,done:1,error:2,spike_count:7:4,event_count:15:8"
puts "HOST_BRAM_ACCESS_RULE=ONLY_WHEN_BUSY_ZERO"
puts "BITSTREAM=$bit_file"
puts "TIMING_REPORT=$timing_report"
puts "UTILIZATION_REPORT=$util_report"
puts "DRC_REPORT=$drc_report"
puts "STATUS=PASS"
exit 0
