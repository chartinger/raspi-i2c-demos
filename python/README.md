# About

Simple webservice demo to read and write from Raspberry i2c bus via a web API

# Prerequisites

* Raspberry Pi (Tested with: `Hardware Version 3`, Raspbian version `May 2016`)
* Some i2c device connected to the i2c bus 1

# Getting started

* Make sure i2c is enabled in your "Raspberry Pi Configuration"
* Install needed python3 libraries with:

  ```
  sudo apt-get install python3-smbus
  sudo apt-get install python3-flask
  ```
* Clone this repository with `git`:

  ```
  git clone https://github.com/chartinger/raspi-i2c-demos.git
  ```
  
* Change to the python directory:

  ```
  cd raspi-i2c-demos/python/
  ```
  
* Run the demo:

  ```
  python3 i2c-server.py
  ```
  This will start a webserver at port 5000
  
# Usage

Given you are on your Raspberry Pi, and your i2c device is available at address `0x20` you can use to read its data by typing
```
http://127.0.0.1:5000/i2c/get/0x20
```
into your browser

Likewise, to write `0xAA` to this device use
```
http://127.0.0.1:5000/i2c/set/0x20/0xAA
```
