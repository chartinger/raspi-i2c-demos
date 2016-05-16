package main

import (
    "fmt"
    "log"
    "strconv"
    "net/http"
    "encoding/hex"
    "encoding/json"

    "github.com/gorilla/mux"
    "github.com/davecheney/i2c"
)

func check(err error) {
	if err != nil { log.Fatal(err) }
}

type Response map[string]interface{}

var i2c_bridge *i2c.I2C;

func main() {
    fmt.Println("Starting server ...")
    router := mux.NewRouter().StrictSlash(true)
    router.HandleFunc("/i2c/get/{device}", ReadI2CValue)
    router.HandleFunc("/i2c/set/{device}/{value}", WriteI2CValue)
    log.Fatal(http.ListenAndServe(":5000", router))
}

func ReadI2CValue(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json; charset=UTF-8")

    vars := mux.Vars(r)
    device, parse_error := strconv.ParseInt(vars["device"], 0, 32)
    if (parse_error != nil) {
        w.WriteHeader(http.StatusBadRequest)
        json.NewEncoder(w).Encode(Response{"message": "Invalid device address"})
        return
    }
    
	i2c_bridge, device_error := i2c.New(uint8(device), 1)
    defer i2c_bridge.Close()

    if (device_error != nil) {
        w.WriteHeader(http.StatusInternalServerError)
        json.NewEncoder(w).Encode(Response{"message": "Could not open device"})
        return
    }
    
    buffer := make([]byte, 1)
    bytes_read, read_error := i2c_bridge.Read(buffer)
    if (read_error != nil || bytes_read != 1) {
        w.WriteHeader(http.StatusInternalServerError)
        json.NewEncoder(w).Encode(Response{"message": "Could not read from device"})
        return
    }
    
    json.NewEncoder(w).Encode(Response{"value": "0x" + hex.EncodeToString(buffer)})
}

func WriteI2CValue(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json; charset=UTF-8")

    vars := mux.Vars(r)
    device, parse_error := strconv.ParseInt(vars["device"], 0, 32)
    if (parse_error != nil) {
        w.WriteHeader(http.StatusBadRequest)
        json.NewEncoder(w).Encode(Response{"message": "Invalid device address"})
        return
    }

    value, parse_error := strconv.ParseInt(vars["value"], 0, 32)
    if (parse_error != nil) {
        w.WriteHeader(http.StatusBadRequest)
        json.NewEncoder(w).Encode(Response{"message": "Invalid write value", "temp": vars, "err": parse_error})
        return
    }
    
	i2c_bridge, device_error := i2c.New(uint8(device), 1)
    defer i2c_bridge.Close()

    if (device_error != nil) {
        w.WriteHeader(http.StatusInternalServerError)
        json.NewEncoder(w).Encode(Response{"message": "Could not open device"})
        return
    }
    
    bytes_written, write_error := i2c_bridge.WriteByte(uint8(value))
    if (write_error != nil || bytes_written != 1) {
        w.WriteHeader(http.StatusInternalServerError)
        json.NewEncoder(w).Encode(Response{"message": "Could not write to device"})
        return
    }
    
    json.NewEncoder(w).Encode(Response{"message": "OK"})
}



