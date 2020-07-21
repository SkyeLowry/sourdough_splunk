#!/bin/bash
# Calls 'raspistill' every 300s (ie. 5 mins) and writes the images
# to a new date/timestamped folder.

ENV_FILE_DIR=../.env

if [ -f $ENV_FILE_DIR ] 
then
  export $(cat $ENV_FILE_DIR | sed 's/#.*//g' | xargs)
fi

# Light on and off variables
LIGHT_ON=https://maker.ifttt.com/trigger/sourdough_on/with/key/${KEY}
LIGHT_OFF=https://maker.ifttt.com/trigger/sourdough_off/with/key/${KEY}

# Delay variables
TOTAL_DELAY=300 # in seconds
CAM_DELAY=1     # need to have a nonzero delay for raspistill

# Must be 1.33 ratio
RES_W=1440
RES_H=1080

# Calculate the total delay time per cycle
SLEEP_DELAY=$(($TOTAL_DELAY - $CAM_DELAY))

FOLDER_NAME=imgs
mkdir -p $FOLDER_NAME # create image root folder if not exist

IDX=0 # image index

function cleanup() {
  echo "Exiting."
  exit 0
}

trap cleanup INT

while true; do
  DATE=$(date +%Y-%m-%d_%H-%M-%S)
  FNAME="${DATE}_(${IDX})" # image filename

  # Create folder for current timelapse set
  if [ $IDX -eq 0 ]; then
    FOLDER_NAME=$FOLDER_NAME/$DATE
    mkdir -p $FOLDER_NAME
    echo "Created folder: ${FOLDER_NAME}"
  fi

  # Turn light on
  ON_STATUS="$(curl -I ${LIGHT_ON} | head -n 1 | cut -d$' ' -f2)"

  if [ $ON_STATUS -eq 200 ]
  then
    echo "Light turned on"

    # Delay so the light is completely turned on when a photo is taken
    sleep 2

    # Take image
    raspistill --nopreview -t $CAM_DELAY -o ./$FOLDER_NAME/$FNAME.jpg -w $RES_W -h $RES_H

    echo "Captured: ${FNAME}"
    IDX=$((IDX + 1))

    sleep 2

    # Turn light off
    OFF_STATUS="$(curl -I ${LIGHT_OFF} | head -n 1 | cut -d$' ' -f2)"

    if [ $OFF_STATUS -eq 200 ] 
    then
      echo "Light turned off"
    else
      echo "Light did NOT turn off"
    fi

    # Copy the image to S3
    ORIGINAL_DIR=$(pwd)/$FOLDER_NAME/$FNAME.jpg
    
    aws s3 cp $ORIGINAL_DIR $S3_BUCKET/$FOLDER_NAME/$FNAME.jpg

    source env/bin/activate

    python env/examine_single_file.py $PWD/$FOLDER_NAME/$FNAME.jpg

    echo "Python closed."

    deactivate

    sleep $SLEEP_DELAY
  else
    echo "Light did NOT turn on"
  fi
done
