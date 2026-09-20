# LAB-HW-02: discover the real K26 FPGA device through the local Vivado hardware server.
# Prerequisites: LAB-HW-00 passed; KV260 powered from J12; J4 USB data connected.

puts "FPGA_FLYBRAIN_LAB=LAB-HW-02"
puts "VIVADO_VERSION=[version -short]"
puts "HW_SERVER_URL=localhost:3121"

if {[catch {open_hw_manager} err]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=OPEN_HW_MANAGER_FAILED"
    puts stderr "DETAIL=$err"
    exit 2
}

if {[catch {connect_hw_server -url localhost:3121} err]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=HW_SERVER_CONNECT_FAILED"
    puts stderr "DETAIL=$err"
    catch {close_hw_manager}
    exit 3
}

set targets [get_hw_targets -quiet]
puts "HW_TARGET_COUNT=[llength $targets]"

if {[llength $targets] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NO_HW_TARGET"
    catch {disconnect_hw_server}
    catch {close_hw_manager}
    exit 4
}

set discovered_devices {}
set kv260_fpga_devices {}

foreach target $targets {
    puts "HW_TARGET=$target"

    if {[catch {open_hw_target $target} err]} {
        puts "HW_TARGET_OPEN_WARNING=$target"
        puts "HW_TARGET_OPEN_DETAIL=$err"
        continue
    }

    set devices [get_hw_devices -quiet -of_objects $target]
    foreach device $devices {
        lappend discovered_devices $device
        puts "HW_DEVICE=$device"

        set normalized [string tolower $device]
        if {[string match "xck26*" $normalized]} {
            lappend kv260_fpga_devices $device
            puts "KV260_FPGA_DEVICE=$device"
        }
    }

    catch {close_hw_target $target}
}

puts "HW_DEVICE_COUNT=[llength $discovered_devices]"
puts "KV260_FPGA_DEVICE_COUNT=[llength $kv260_fpga_devices]"

catch {disconnect_hw_server}
catch {close_hw_manager}

if {[llength $kv260_fpga_devices] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NO_KV260_FPGA_DEVICE"
    puts stderr "DETAIL=Expected an XCK26 device. Check J12 power, J4 data cable, cable driver, and target ownership."
    exit 5
}

puts "STATUS=PASS"
exit 0
