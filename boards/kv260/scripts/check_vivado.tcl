# LAB-HW-00: development-host Vivado/KV260-board-data preflight.
# This script intentionally does not open Hardware Manager or require a board.

set expected_vivado_prefix "2026.1"
set vivado_version [version -short]

puts "FPGA_FLYBRAIN_LAB=LAB-HW-00"
puts "VIVADO_VERSION=$vivado_version"
puts "EXPECTED_VIVADO_VERSION=$expected_vivado_prefix"

if {![string match "${expected_vivado_prefix}*" $vivado_version]} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=UNSUPPORTED_VIVADO_VERSION"
    puts stderr "DETAIL=Expected Vivado ${expected_vivado_prefix}.x authoring baseline."
    exit 2
}

set kv260_parts [get_board_parts -quiet *kv260*]
puts "KV260_BOARD_PART_COUNT=[llength $kv260_parts]"

if {[llength $kv260_parts] == 0} {
    puts stderr "STATUS=FAIL"
    puts stderr "ERROR=NO_KV260_BOARD_PART"
    puts stderr "DETAIL=Refresh/install KV260 board data from Vivado Store -> Boards."
    exit 3
}

foreach part $kv260_parts {
    puts "KV260_BOARD_PART=$part"
}

puts "STATUS=PASS"
exit 0
