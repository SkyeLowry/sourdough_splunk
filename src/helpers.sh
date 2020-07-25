function export_env_var {
  # $1: `.env` file directory

  if [ -f $1 ] 
  then
    export $(cat $1 | sed 's/#.*//g' | xargs)
  fi
}

function cleanup {
  echo "Exiting."
  exit 0
}

function take_photo {
  # $1: Delay in seconds
  # $2: Full image filename
  # $3: Width resolution
  # $4: Height resolution
  # raspistill reference: https://www.raspberrypi.org/documentation/usage/camera/raspicam/raspistill.md

  raspistill --nopreview -t $1 -o $2 -w $3 -h $4
}

function create_image_folder {
  # $1: Image file index number

  DATE=$(date +%Y-%m-%d_%H-%M-%S)

  # Create folder for current timelapse set
  if [ $1 -eq 0 ]; then
    FOLDER_NAME=imgs/$DATE
    mkdir -p $FOLDER_NAME
  fi

  FOLDER_FILE_NAME=$FOLDER_NAME/"${DATE}_(${1}).jpg"

  echo $FOLDER_FILE_NAME
}

function add_image_to_s3 {
  # $2: Image folder + file name
  
  aws s3 cp $(pwd)/$2 $1/$2
}

function analyze_image {  
  # $1: Python file to run
  # $2: Full image name

  source $(pwd)/env/bin/activate

  python $(pwd)/$1 $2

  echo "Python closed."

  deactivate
}

function turn_light_on {
  ON_STATUS="$(curl -I ${1} | head -n 1 | cut -d$' ' -f2)"

  echo $ON_STATUS
}

function turn_light_off {
  OFF_STATUS="$(curl -I ${1} | head -n 1 | cut -d$' ' -f2)"

  echo $OFF_STATUS
}

function run_main_sourdough {
  # Delay so the light is completely turned on when a photo is taken
  sleep 2

  # Take image
  take_photo $CAM_DELAY $(pwd)/$1 $RES_W $RES_H

  echo "Captured: ${$1}"

  IDX=$((IDX + 1))

  sleep 2

  if [ -n "$S3_BUCKET_ENDPOINT" ]
  then
    add_image_to_s3 $S3_BUCKET_ENDPOINT $1
  fi

  analyze_image "examine_single_file.py" $(pwd)/$1

  sleep $SLEEP_DELAY
}
