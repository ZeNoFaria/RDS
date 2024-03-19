#!/bin/bash

# List of interfaces to delete
interfaces=("R1-eth1" "R0-eth1" "S0-eth1" "R0-eth3" "R2-eth1" "R1-eth2" "S1-eth1" "R1-eth3" "R0-eth2" "R2-eth2" "S2-eth1" "R2-eth3")

# Loop over the interfaces and delete each one
for intf in "${interfaces[@]}"; do
    sudo ip link delete $intf
done