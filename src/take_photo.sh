source helpers.sh

export_env_var ../.env

test_dir=imgs/test
test_photo_name=$test_dir/test_photo.jpg

if [ ! -d $test_dir ]
then 
  mkdir -p $test_dir
fi

take_photo $test_photo_name

echo "Photo saved as ${test_photo_name}"
