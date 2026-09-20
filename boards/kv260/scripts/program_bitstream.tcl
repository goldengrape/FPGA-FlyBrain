# Program an already-built LAB-HW-03/04 bitstream over JTAG.
# Example:
#   vivado -mode batch -nojournal -log lab-hw-03-program.log \
#     -source boards/kv260/scripts/program_bitstream.tcl \
#     -tclargs build/kv260/lab-hw-03/kv260_marker_top.bit

if {$argc != 1} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=BITSTREAM_ARGUMENT_REQUIRED"
    puts stderr "DETAIL=Pass exactly one .bit path with -tclargs."
    exit 2
}

set bit_file [file normalize [lindex $argv 0]]
if {![file exists $bit_file]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=BITSTREAM_NOT_FOUND"
    puts stderr "BITSTREAM=$bit_file"
    exit 3
}
if {[string tolower [file extension $bit_file]] ne ".bit"} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=BITSTREAM_EXTENSION_NOT_BIT"
    puts stderr "BITSTREAM=$bit_file"
    exit 4
}

puts "VIVADO_VERSION=[version -short]"
puts "BITSTREAM=$bit_file"
puts "HW_SERVER_URL=localhost:3121"

open_hw_manager
if {[catch {connect_hw_server -url localhost:3121} err]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=HW_SERVER_CONNECT_FAILED"
    puts stderr "DETAIL=$err"
    catch {close_hw_manager}
    exit 5
}
if {[catch {open_hw_target} err]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=OPEN_HW_TARGET_FAILED"
    puts stderr "DETAIL=$err"
    catch {disconnect_hw_server}
    catch {close_hw_manager}
    exit 6
}

set devices [get_hw_devices -quiet xck26*]
if {[llength $devices] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NO_KV260_FPGA_DEVICE"
    catch {close_hw_target}
    catch {disconnect_hw_server}
    catch {close_hw_manager}
    exit 7
}

set device [lindex $devices 0]
current_hw_device $device
refresh_hw_device -update_hw_probes false $device
puts "KV260_FPGA_DEVICE=$device"

set_property PROGRAM.FILE $bit_file $device
if {[catch {program_hw_devices $device} err]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=PROGRAM_HW_DEVICE_FAILED"
    puts stderr "DETAIL=$err"
    catch {close_hw_target}
    catch {disconnect_hw_server}
    catch {close_hw_manager}
    exit 8
}
refresh_hw_device -update_hw_probes false $device

puts "PROGRAM_FILE=[get_property PROGRAM.FILE $device]"
puts "STATUS=PASS"

catch {close_hw_target}
catch {disconnect_hw_server}
catch {close_hw_manager}
exit 0
