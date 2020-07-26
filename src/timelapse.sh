#!/bin/bash
# Calls 'raspistill' every 300s (ie. 5 mins) and writes the images
# to a new date/timestamped folder.

source ./helpers.sh

export_env_var ../.env

# Create image root folder if not exist
mkdir -p imgs 

# Set initial image index
IDX=0 

# Calculate width resolution (RES_W : RES_H = 1.33)
RES_W=$(($RES_H * 133 / 100))

# Calculate the total delay time per cycle
SLEEP_DELAY=$(($TOTAL_DELAY - $CAM_DELAY))

trap cleanup INT

while true
do
  FOLDER_FILE_NAME=$(create_image_folder ${IDX})

  if [ -n "$LIGHT_ON_ENDPOINT" ] && [ -n "$LIGHT_OFF_ENDPOINT" ] 
  then
    # Turn light on
    ON_STATUS=$(turn_light_on)

    if [ $ON_STATUS -eq 200 ]
    then
      echo "Light turned on"
      run_main_sourdough $FOLDER_FILE_NAME

      # Turn light off
      OFF_STATUS=$(turn_light_off)
    else
      echo "Light did not turn on"
    fi
  else
    run_main_sourdough $FOLDER_FILE_NAME
  fi
done
