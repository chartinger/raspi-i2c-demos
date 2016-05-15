from flask import Flask, Response
from smbus import SMBus
import json

# Initialitze the http and i2c libs

app = Flask(__name__)
bus = SMBus(1) 

# Define some exceptions for common error cases

class InvalidDeviceAddress(Exception):
    pass

class InvalidWriteValue(Exception):
    pass

class I2CReadError(Exception):
    pass

class I2CWriteError(Exception):
    pass

# Helper functions for parsing the hex values

def get_device_address(device):
    try:
        return int(device, 16)
    except ValueError:
        raise InvalidDeviceAddress

def get_write_value(value):
    try:
        return int(value, 16)
    except ValueError:
        raise InvalidWriteValue

# Helper function to return a nice json response

def json_response(message, status=200):
    if isinstance(message, str):
        ret = {}
        ret['message'] = message
    else:
        ret = message
    json_response = json.dumps(ret)
    return Response(response=json_response, status=status, mimetype="application/json")

# Here we define our web api

@app.route('/i2c/get/<string:device>')
def read_i2c_value(device):
    device = get_device_address(device)
    try:
        value = bus.read_byte(device)
    except OSError:
        raise I2CReadError
    return json_response({'value': '0x%02X' % value, 'message': 'Value of 0x%02x: 0x%02X' % (device, value)})

@app.route('/i2c/set/<string:device>/<string:value>')
def write_i2c_value(device, value):
    device = get_device_address(device)
    value = get_write_value(value)
    try:
        bus.write_byte(device, value)
    except OSError:
        raise I2CWriteError
    return json_response('OK')

# In case of an exception (we defined them above), return the error as json

@app.errorhandler(I2CReadError)
def handle_device_error(error):
    return json_response("Could not read from device", 500)

@app.errorhandler(I2CWriteError)
def handle_device_error(error):
    return json_response("Could not write to device", 500)

@app.errorhandler(InvalidDeviceAddress)
def handle_invalid_usage(error):
    return json_response("Invalid device address", 400)

@app.errorhandler(InvalidWriteValue)
def handle_invalid_usage(error):
    return json_response("Invalid write value", 400)

# Start the server

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')

