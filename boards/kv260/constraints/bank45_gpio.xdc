# KV260 Bank 45 GPIO LED-class interface.
# Grounded in XilinxBoardStore:
#   kv260_carrier/1.3/board.xml -> bank45_gpio / leds_4bits_tri_o
#   kv260_som/1.4/part0_pins.xml -> K26 package locations.
#
# This XDC is intentionally course-provided in LAB-HW-03.
# LAB-HW-04 is where learners inspect and explain the mapping.

set_property PACKAGE_PIN J11 [get_ports {bank45_gpio[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {bank45_gpio[0]}]

set_property PACKAGE_PIN J10 [get_ports {bank45_gpio[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {bank45_gpio[1]}]

set_property PACKAGE_PIN K13 [get_ports {bank45_gpio[2]}]
set_property IOSTANDARD LVCMOS33 [get_ports {bank45_gpio[2]}]

set_property PACKAGE_PIN F11 [get_ports {bank45_gpio[3]}]
set_property IOSTANDARD LVCMOS33 [get_ports {bank45_gpio[3]}]

set_property PACKAGE_PIN A12 [get_ports {bank45_gpio[4]}]
set_property IOSTANDARD LVCMOS33 [get_ports {bank45_gpio[4]}]
