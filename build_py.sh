#!/bin/bash

# Stop the existing service and kill any running processes
sudo systemctl stop raspivid_service.service
sudo killall -9 python3

# Define a temporary file for output
output_file="/home/piz/pi_fs/output.log"

# Start the new process, redirect output to the temporary file
nohup python3 -u /home/piz/pi_fs/mqtt.py > $output_file 2>&1 &
