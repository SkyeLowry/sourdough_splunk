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

function main {
  # Delay so the light is completely turned on when a photo is taken
  sleep 2

  # Take image
  take_photo $CAM_DELAY $(pwd)/$1 $RES_W $RES_H

  echo "Captured: ${FILE_NAME}"

  IDX=$((IDX + 1))

  sleep 2

  if [ -n "$S3_BUCKET_ENDPOINT" ]
  then
    add_image_to_s3 $S3_BUCKET_ENDPOINT $1
  fi

  analyze_image "examine_single_file.py" $(pwd)/$1

  sleep $SLEEP_DELAY
}

while true; do
  FOLDER_FILE_NAME=$(create_image_folder ${IDX})

  if [ -n "$LIGHT_ON_ENDPOINT" ] && [ -n "$LIGHT_OFF_ENDPOINT" ] 
  then
    # Turn light on
    ON_STATUS=$(turn_light_on ${LIGHT_ON_ENDPOINT})

    if [ $ON_STATUS -eq 200 ]
    then
      echo "Light turned on"
      main $FOLDER_FILE_NAME

      # Turn light off
      OFF_STATUS=$(turn_light_off ${LIGHT_OFF_ENDPOINT})
    else
      echo "Light did not turn on"
    fi
  else
    main $FOLDER_FILE_NAME
  fi
done
