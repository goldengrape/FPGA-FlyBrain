# LAB-HW-10: AXI CDMA Simple-DMA benchmark path to K26 DDR.
#
# Control:
#   PS M_AXI_HPM0_FPD -> SmartConnect -> AXI CDMA S_AXI_LITE @ 0xA0020000
#
# Data:
#   AXI CDMA M_AXI (128 bit, max burst 64) -> PS S_AXI_HP0_FPD -> DDR
#
# S_AXI_HP0_FPD is non-coherent. Runtime software therefore requires a
# DMA-safe u-dma-buf mapping opened with O_SYNC. This build does not add
# cache-coherency claims or a Linux DMA driver.

set script_dir [file dirname [file normalize [info script]]]
set board_dir [file normalize [file join $script_dir ..]]
set repo_root [file normalize [file join $board_dir .. ..]]
set build_dir [file join $repo_root build kv260 lab-hw-10]

set part_name "xck26-sfvc784-2LV-c"
set board_part_name "xilinx.com:kv260_som:part0:1.4"
set cdma_base 0xA0020000
set cdma_range 0x00010000
set ddr_low_base 0x00000000
set ddr_low_range 0x80000000

file delete -force $build_dir
file mkdir $build_dir

puts "FPGA_FLYBRAIN_LAB=LAB-HW-10"
puts "VIVADO_VERSION=[version -short]"
puts "FPGA_PART=$part_name"
puts "BOARD_PART=$board_part_name"
puts [format "CDMA_CONTROL_BASE=0x%08X" $cdma_base]
puts "CDMA_MODE=SIMPLE_DMA"
puts "CDMA_DATA_WIDTH_BITS=128"
puts "CDMA_MAX_BURST_BEATS=64"
puts "CDMA_ADDRESS_WIDTH_BITS=64"
puts "CDMA_DRE=DISABLED"
puts "PL_DDR_PORT=S_AXI_HP0_FPD"
puts "PL_DDR_COHERENCY=NON_COHERENT"
puts "DMA_BUFFER_CONTRACT=U_DMA_BUF_O_SYNC"
puts "DDR_APERTURE=HP0_DDR_LOW"

if {[llength [get_board_parts -quiet $board_part_name]] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_KV260_BOARD_PART_1_4"
    exit 2
}

create_project lab_hw_10 $build_dir -part $part_name -force
set_property BOARD_PART $board_part_name [current_project]

create_bd_design system

set ps_defs [get_ipdefs -all xilinx.com:ip:zynq_ultra_ps_e:*]
if {[llength $ps_defs] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_ZYNQ_ULTRA_PS_E"
    exit 3
}
set ps_vlnv [get_property VLNV [lindex $ps_defs end]]
create_bd_cell -type ip -vlnv $ps_vlnv ps
apply_bd_automation -rule xilinx.com:bd_rule:zynq_ultra_ps_e -config {apply_board_preset "1"} [get_bd_cells ps]
set_property -dict [list     CONFIG.PSU__USE__M_AXI_GP0 {1}     CONFIG.PSU__USE__S_AXI_GP2 {1}     CONFIG.PSU__SAXIGP2__DATA_WIDTH {128} ] [get_bd_cells ps]

set cdma_defs [get_ipdefs -all xilinx.com:ip:axi_cdma:*]
if {[llength $cdma_defs] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_AXI_CDMA"
    exit 4
}
set cdma_vlnv [get_property VLNV [lindex $cdma_defs end]]
create_bd_cell -type ip -vlnv $cdma_vlnv axi_cdma
set_property -dict [list     CONFIG.C_INCLUDE_SG {0}     CONFIG.C_M_AXI_DATA_WIDTH {128}     CONFIG.C_M_AXI_MAX_BURST_LEN {64}     CONFIG.C_ADDR_WIDTH {64}     CONFIG.C_INCLUDE_DRE {0}     CONFIG.C_USE_DATAMOVER_LITE {0} ] [get_bd_cells axi_cdma]

set smc_defs [get_ipdefs -all xilinx.com:ip:smartconnect:*]
if {[llength $smc_defs] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_SMARTCONNECT"
    exit 5
}
set smc_vlnv [get_property VLNV [lindex $smc_defs end]]
create_bd_cell -type ip -vlnv $smc_vlnv ctrl_smc
set_property -dict [list CONFIG.NUM_MI {1} CONFIG.NUM_SI {1}] [get_bd_cells ctrl_smc]

set rst_defs [get_ipdefs -all xilinx.com:ip:proc_sys_reset:*]
if {[llength $rst_defs] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_PROC_SYS_RESET"
    exit 6
}
set rst_vlnv [get_property VLNV [lindex $rst_defs end]]
create_bd_cell -type ip -vlnv $rst_vlnv rst

connect_bd_intf_net [get_bd_intf_pins ps/M_AXI_HPM0_FPD] [get_bd_intf_pins ctrl_smc/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins ctrl_smc/M00_AXI] [get_bd_intf_pins axi_cdma/S_AXI_LITE]
connect_bd_intf_net [get_bd_intf_pins axi_cdma/M_AXI] [get_bd_intf_pins ps/S_AXI_HP0_FPD]

connect_bd_net [get_bd_pins ps/pl_clk0]     [get_bd_pins ps/maxihpm0_fpd_aclk]     [get_bd_pins ps/saxihp0_fpd_aclk]     [get_bd_pins ctrl_smc/aclk]     [get_bd_pins axi_cdma/s_axi_lite_aclk]     [get_bd_pins axi_cdma/m_axi_aclk]     [get_bd_pins rst/slowest_sync_clk]

connect_bd_net [get_bd_pins ps/pl_resetn0] [get_bd_pins rst/ext_reset_in]
connect_bd_net [get_bd_pins rst/peripheral_aresetn]     [get_bd_pins ctrl_smc/aresetn]     [get_bd_pins axi_cdma/s_axi_lite_aresetn]

assign_bd_address     -offset $cdma_base     -range $cdma_range     -target_address_space [get_bd_addr_spaces ps/Data]     [get_bd_addr_segs axi_cdma/S_AXI_LITE/Reg]     -force

assign_bd_address     -offset $ddr_low_base     -range $ddr_low_range     -target_address_space [get_bd_addr_spaces axi_cdma/Data]     [get_bd_addr_segs ps/SAXIGP2/HP0_DDR_LOW]     -force

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
set bit_file [file join $build_dir kv260_axi_cdma_benchmark.bit]

report_timing_summary -file $timing_report
report_utilization -file $util_report
report_drc -file $drc_report

set drc_errors [get_drc_violations -quiet -filter {SEVERITY == "Error"}]
puts "DRC_ERROR_COUNT=[llength $drc_errors]"
if {[llength $drc_errors] > 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=DRC_ERROR_PRESENT"
    exit 9
}

set setup_paths [get_timing_paths -quiet -setup -max_paths 1 -nworst 1]
set hold_paths [get_timing_paths -quiet -hold -max_paths 1 -nworst 1]
if {[llength $setup_paths] == 0 || [llength $hold_paths] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=MISSING_TIMING_PATH"
    exit 10
}
set setup_slack [get_property SLACK [lindex $setup_paths 0]]
set hold_slack [get_property SLACK [lindex $hold_paths 0]]
puts "TIMING_SETUP_WORST_SLACK_NS=$setup_slack"
puts "TIMING_HOLD_WORST_SLACK_NS=$hold_slack"
if {[expr {double($setup_slack) < 0.0}]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NEGATIVE_SETUP_SLACK"
    exit 11
}
if {[expr {double($hold_slack) < 0.0}]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NEGATIVE_HOLD_SLACK"
    exit 12
}

write_bitstream -force $bit_file

puts "CDMA_REGISTER_MAP=PG034_00_04_18_1C_20_24_28"
puts "CONTROL_PATH=M_AXI_HPM0_FPD_TO_AXI_CDMA_S_AXI_LITE"
puts "DATA_PATH=AXI_CDMA_M_AXI_TO_S_AXI_HP0_FPD_TO_DDR"
puts "BITSTREAM=$bit_file"
puts "TIMING_REPORT=$timing_report"
puts "UTILIZATION_REPORT=$util_report"
puts "DRC_REPORT=$drc_report"
puts "STATUS=PASS"
exit 0
