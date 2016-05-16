<?php
require_once __DIR__.'/../vendor/autoload.php';

use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Process\Process;

// Define some exceptions for common error cases

class InvalidDeviceAddress extends Exception {};
class InvalidWriteValue extends Exception {};
class I2CReadError extends Exception {};
class I2CWriteError extends Exception {};
class I2CToolsNotFound extends Exception {};

// Initialitze libs

$app = new Silex\Application();
$app['debug'] = true;

// Helper functions for parsing the hex values
// Return as Base 10

function getDeviceAddress($device)
{
    $device = str_replace('0x', '', $device);
    if ((strlen($device) == 2) && ctype_xdigit($device)) {
        return hexdec($device);
    } else {
        throw new InvalidDeviceAddress();
    }
}

function getWriteValue($value)
{
    $value = str_replace('0x', '', $value);
    if ((strlen($value) == 2) && ctype_xdigit($value)) {
        return hexdec($value);
    } else {
        throw new InvalidWriteValue();
    }
}

// Here we define our web api

$app->get('/i2c/get/{device}', function ($device) use ($app) {
    $device = getDeviceAddress($device);
    $process = new Process('/usr/sbin/i2cget -y 1 ' . $device);
    $process->run();
    if (!$process->isSuccessful()) {
        throw new I2CReadError();
    }
    $output = trim($process->getOutput());
    return $app->json(array('value' => $output, 'message' => 'Value of 0x' . dechex($device ). ': ' . $output));
});

$app->get('/i2c/set/{device}/{value}', function ($device, $value) use ($app) {
    $device = getDeviceAddress($device);
    $value = getWriteValue($value);
    $process = new Process('/usr/sbin/i2cset -y 1 ' . $device . ' ' . $value);
    $process->run();
    if (!$process->isSuccessful()) {
        throw new I2CWriteError();
    }
    $output = trim($process->getOutput());
    return $app->json(array('message' => 'OK'));
});

// In case of an exception (we defined them above), return the error as json

$app->error(function (I2CReadError $e, $code) use ($app) {
    return $app->json(array('message' => 'Could not read from device'), 500);
});

$app->error(function (I2CWriteError $e, $code) use ($app) {
    return $app->json(array('message' => 'Could not write to device'), 500);
});

$app->error(function (InvalidDeviceAddress $e, $code) use ($app) {
    return $app->json(array('message' => 'Invalid device address'), 400);
});

$app->error(function (InvalidWriteValue $e, $code) use ($app) {
    return $app->json(array('message' => 'Invalid write value'), 400);
});

// Start the server

$app->run();
