# About

Simple webservice demo to read and write from Raspberry i2c bus via a web API

# Prerequisites

* Raspberry Pi (Tested with: `Hardware Version 3`, Raspbian version `May 2016`)
* Some i2c device connected to the i2c bus 1

# Getting started

* Make sure i2c is enabled in your "Raspberry Pi Configuration"
* Install php5-cli so we can execute php from the commandline:

  ```
  sudo apt-get install php5-cli
  ```
* PHP cannot access the i2c device directly, we need to install the i2c-tools:

  ```
  sudo apt-get install i2c-tools
  ```

* Clone this repository with `git`:

  ```
  git clone https://github.com/chartinger/raspi-i2c-demos.git
  ```
  
* Change to the php directory:

  ```
  cd raspi-i2c-demos/php/
  ```
  
* Install [Composer](https://getcomposer.org/download/). Just follow the instructions in the link.
  
* Use composer to install the needed libraries:

  ```
  php composer.phar install
  ```
  
* Run the demo:

  ```
  php -S 0.0.0.0:5000 web/index.php
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
