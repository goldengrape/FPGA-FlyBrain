# LAB-HW-03: build the first minimal KV260 bitstream.
# Run from the repository root:
#   vivado -mode batch -nojournal -log lab-hw-03-build.log \
#     -source boards/kv260/scripts/build_lab03_marker.tcl

set script_dir [file dirname [file normalize [info script]]]
set board_dir [file normalize [file join $script_dir ..]]
set repo_root [file normalize [file join $board_dir .. ..]]
set build_dir [file join $repo_root build kv260 lab-hw-03]
set rtl_file [file join $board_dir rtl kv260_marker_top.sv]
set xdc_file [file join $board_dir constraints bank45_gpio.xdc]
set part_name "xck26-sfvc784-2LV-c"

file delete -force $build_dir
file mkdir $build_dir

puts "FPGA_FLYBRAIN_LAB=LAB-HW-03"
puts "VIVADO_VERSION=[version -short]"
puts "FPGA_PART=$part_name"
puts "TOP=kv260_marker_top"

create_project lab_hw_03 $build_dir -part $part_name -force
add_files -norecurse $rtl_file
add_files -fileset constrs_1 -norecurse $xdc_file
set_property top kv260_marker_top [current_fileset]

synth_design -top kv260_marker_top -part $part_name
opt_design
place_design
route_design

set timing_report [file join $build_dir timing_summary.rpt]
set util_report [file join $build_dir utilization.rpt]
set drc_report [file join $build_dir drc.rpt]
set bit_file [file join $build_dir kv260_marker_top.bit]

report_timing_summary -file $timing_report
report_utilization -file $util_report
report_drc -file $drc_report

# LAB-HW-03 is intentionally clockless. Make that boundary explicit instead
# of printing a misleading "timing passed" message.
set clocks [get_clocks -quiet]
puts "CLOCK_COUNT=[llength $clocks]"
if {[llength $clocks] != 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=UNEXPECTED_CLOCK_IN_CLOCKLESS_MARKER"
    puts stderr "DETAIL=LAB-HW-03 must remain clockless; investigate the project/source set."
    exit 2
}
puts "TIMING_CHECK=NOT_APPLICABLE_CLOCKLESS"

write_bitstream -force $bit_file

puts "BITSTREAM=$bit_file"
puts "TIMING_REPORT=$timing_report"
puts "UTILIZATION_REPORT=$util_report"
puts "DRC_REPORT=$drc_report"
puts "STATUS=PASS"
exit 0
