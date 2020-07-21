# sourdough_splunk
An image processor that uses a Raspberry Pi to monitor a sourdough starter in Splunk

## Requirements
- Python & pip ([instruction](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#linux-and-macos))

## Setup 
- Python Virtualenv
  - Click [here](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#installing-virtualenv) and follow instructions from `Installing virtualenv` and `Creating a virtual environment`
  Note: Make sure the virtualenv folder name is `~/src/env` as seen in the official Python instruction

- Raspberry Pi

- Splunk Universal Forwarder

- IFTTT 

    Note: You can use any other API webhook to control background light

- AWS S3

- `.env`
  - Create `.env` file using `.env.example` and locate it at the root of the directory
  - Please ensure to add all required variables before running scripts

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

Run the following script
```
. run_sourdough_monitor.sh
```
