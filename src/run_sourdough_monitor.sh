#!/bin/bash
# Convenience script to run the monitor from home directory and launch
# in background

# Start in background so ssh session can be closed
nohup ./timelapse.sh &> /dev/null &
