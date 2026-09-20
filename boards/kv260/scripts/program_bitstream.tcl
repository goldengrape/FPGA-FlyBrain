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

if {[catch {open_hw_manager} err]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=OPEN_HW_MANAGER_FAILED"
    puts stderr "DETAIL=$err"
    exit 5
}
if {[catch {connect_hw_server -url localhost:3121} err]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=HW_SERVER_CONNECT_FAILED"
    puts stderr "DETAIL=$err"
    catch {close_hw_manager}
    exit 6
}

set targets [get_hw_targets -quiet]
puts "HW_TARGET_COUNT=[llength $targets]"
if {[llength $targets] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NO_HW_TARGET"
    catch {disconnect_hw_server}
    catch {close_hw_manager}
    exit 7
}

# Discover exactly one target/device pair containing an XCK26 FPGA. This
# avoids silently programming the wrong target when multiple JTAG chains are
# attached to the development host.
set candidates {}
foreach target $targets {
    puts "HW_TARGET=$target"
    if {[catch {open_hw_target $target} err]} {
        puts "HW_TARGET_OPEN_WARNING=$target"
        puts "HW_TARGET_OPEN_DETAIL=$err"
        continue
    }

    set devices [get_hw_devices -quiet -of_objects $target]
    foreach device $devices {
        puts "HW_DEVICE=$device"
        if {[string match "xck26*" [string tolower $device]]} {
            lappend candidates [list $target $device]
            puts "KV260_FPGA_CANDIDATE=$target|$device"
        }
    }
    catch {close_hw_target $target}
}

puts "KV260_FPGA_CANDIDATE_COUNT=[llength $candidates]"
if {[llength $candidates] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NO_KV260_FPGA_DEVICE"
    catch {disconnect_hw_server}
    catch {close_hw_manager}
    exit 8
}
if {[llength $candidates] > 1} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=AMBIGUOUS_KV260_FPGA_DEVICE"
    puts stderr "DETAIL=Disconnect extra targets or close competing hardware sessions, then retry."
    foreach candidate $candidates {
        puts stderr "CANDIDATE=[lindex $candidate 0]|[lindex $candidate 1]"
    }
    catch {disconnect_hw_server}
    catch {close_hw_manager}
    exit 9
}

set selected [lindex $candidates 0]
set selected_target [lindex $selected 0]
set selected_device_name [lindex $selected 1]

if {[catch {open_hw_target $selected_target} err]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=SELECTED_HW_TARGET_OPEN_FAILED"
    puts stderr "DETAIL=$err"
    catch {disconnect_hw_server}
    catch {close_hw_manager}
    exit 10
}

set device ""
foreach candidate_device [get_hw_devices -quiet -of_objects $selected_target] {
    if {$candidate_device eq $selected_device_name} {
        set device $candidate_device
        break
    }
}
if {$device eq ""} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=SELECTED_KV260_DEVICE_DISAPPEARED"
    catch {close_hw_target $selected_target}
    catch {disconnect_hw_server}
    catch {close_hw_manager}
    exit 11
}

current_hw_device $device
refresh_hw_device -update_hw_probes false $device
puts "KV260_HW_TARGET=$selected_target"
puts "KV260_FPGA_DEVICE=$device"

set_property PROGRAM.FILE $bit_file $device
if {[catch {program_hw_devices $device} err]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=PROGRAM_HW_DEVICE_FAILED"
    puts stderr "DETAIL=$err"
    catch {close_hw_target $selected_target}
    catch {disconnect_hw_server}
    catch {close_hw_manager}
    exit 12
}
refresh_hw_device -update_hw_probes false $device

puts "PROGRAM_FILE=[get_property PROGRAM.FILE $device]"
puts "STATUS=PASS"

catch {close_hw_target $selected_target}
catch {disconnect_hw_server}
catch {close_hw_manager}
exit 0
