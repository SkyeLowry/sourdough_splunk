# Sourdough Splunk Project
An image processor that uses a Raspberry Pi to monitor a sourdough starter in Splunk

## Requirements
- Python & pip (click [here](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#installing-pip) for instructions)

- `.env` file
  - Create `.env` file using `.env.example` and locate it at the root of the directory
  - Please ensure to add all required variables before running scripts

## Setup 
### Mandatory Setup
- Python Virtual Environment
  - Click [here](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#installing-virtualenv) and follow instructions from `Installing virtualenv` and `Creating a virtual environment`
  Note: Make sure the virtualenv folder name is `env` inside `./src` folder as seen in the official Python instruction

- Raspberry Pi

  - How test camera?
    Go to `src` folder and run the following command: `. take_photo.sh`
- Splunk Universal Forwarder

### Optional setup
- [IFTTT](https://ifttt.com/)

  IFTTT was used to automatically turn on a light source when Rasberry Pi takes a photo of sourdough and then turn it back off. You may use any other API webhook to control background light or skip this step.

- [AWS S3](https://aws.amazon.com/s3/)

  AWS S3 was used to store sourdough images and show them in the Splunk dashboard.

## How to run scripts
1. Go to `src` directory
2. Activate virtualenv
```
source env/bin/activate
```
3. Download required libraries
```
pip3 install -r requirements.txt
```

4. Run the following script (**dot** required before `run_sourdough_monitor.sh`)
```
. run_sourdough_monitor.sh
```
