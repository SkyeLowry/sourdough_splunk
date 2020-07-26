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

  raspistill --nopreview -t $CAM_DELAY -o $1 -w $RES_W -h $RES_H
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
  
  aws s3 cp $(pwd)/$1 $S3_BUCKET_ENDPOINT/$1
}

function analyze_image {  
  # $1: Python file to run
  # $2: Full image name

  source $(pwd)/env/bin/activate

  python $(pwd)/examine_single_file.py $1

  echo "Python closed."

  deactivate
}

function turn_light_on {
  ON_STATUS="$(curl -I ${LIGHT_ON_ENDPOINT} | head -n 1 | cut -d$' ' -f2)"

  echo $ON_STATUS
}

function turn_light_off {
  OFF_STATUS="$(curl -I ${LIGHT_OFF_ENDPOINT} | head -n 1 | cut -d$' ' -f2)"

  echo $OFF_STATUS
}

function run_main_sourdough {
  # Delay so the light is completely turned on when a photo is taken
  sleep 2

  # Take image
  take_photo $(pwd)/$1

  echo "Captured: ${1}"

  IDX=$((IDX + 1))

  sleep 2

  if [ -n "$S3_BUCKET_ENDPOINT" ]
  then
    add_image_to_s3 $1
  fi

  analyze_image $(pwd)/$1

  sleep $SLEEP_DELAY
}
