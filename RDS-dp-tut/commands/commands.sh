#!/bin/bash

# List of switches and corresponding thrift ports
switches=("R1" "R2" "R3")
thrift_ports=("9090" "9091" "9092")

# Get the length of the arrays
length=${#switches[@]}

# Loop over the arrays
for ((i=0; i<$length; i++)); do
    switch=${switches[$i]}
    thrift_port=${thrift_ports[$i]}
    simple_switch_CLI --thrift-port $thrift_port < $switch.txt
done