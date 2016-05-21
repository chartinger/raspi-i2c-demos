from flask import Flask, Response
from smbus import SMBus
import time

# LCD 1602 example (on 8574 i2c expander)

usleep = lambda x: time.sleep(x/1000000.0)

class ControlNibble:
    
    RS = 0
    RW = 1
    E_ = 2
    BL = 3
    
    def __init__(self):
        self.flags = 0x00
        
    def setBit(self, location, value):
        if (value):
            self.flags |= (1 << location)
        else:
            self.flags &= ~(1 << location)

    def setEnabled(self, value):
        self.setBit(self.E_, value)

    def setCommand(self, value):
        self.setBit(self.RS, not value)

    def setWriting(self, value):
        self.setBit(self.RW, not value)

    def setBacklight(self, value):
        self.setBit(self.BL, value)

    def asInt(self):
        return self.flags

class LCD:
    
    LCD_CMD_RESET = 0x03
    LCD_CMD_4BINP = 0x02
    
    LCD_CMD_CLEAR      = 0x01
    LCD_CMD_4BIT_2LINE = 0x28
    LCD_CMD_DISPLAY_ON = 0x0C
    LCD_CMD_NORMALMODE = 0x06
    
    LCD_DDRAM_LINE1    = 0x80
    LCD_DDRAM_LINE2    = 0xC0
    
    def __init__(self, address, debug = False):
        self.bus = SMBus(1) 
        self.control = ControlNibble()
        self.address = address
        self.debug = debug
        self.cols = 16
        self.lines = 2

        self.bus.write_byte(self.address, 0x01)

        self.sendCommand(self.LCD_CMD_RESET)
        usleep(1600)
        self.sendCommand(self.LCD_CMD_RESET)
        usleep(1600)
        self.sendCommand(self.LCD_CMD_RESET)
        usleep(1600)
        self.sendCommand(self.LCD_CMD_4BINP)
        usleep(1600)
        
        self.sendCommandByte(self.LCD_CMD_4BIT_2LINE) # Set 4 Bit Mode
        self.sendCommandByte(self.LCD_CMD_DISPLAY_ON) # no cursor no blinking
        self.clear()
        self.sendCommandByte(self.LCD_CMD_NORMALMODE) # No display shift
        
        self.control.setBacklight(True)
        self.send(0x00)

    def clear(self):
        self.sendCommandByte(self.LCD_CMD_CLEAR)
        usleep(1600)

    def setCursorPosition(self, line, col):
        if (col < 0 or self.cols <= col):
            col = 0
        if (line < 1 or self.lines < line):
            line = 1
        pos = 0
        if line == 1:
            pos = self.LCD_DDRAM_LINE1
        elif line == 2:
            pos = self.LCD_DDRAM_LINE2
        else:
            return
        self.sendCommandByte(pos + col)
        
    def setText(self, text, line = 1):
        self.setCursorPosition(line, 0)
        text = text[:16]
        text = text.ljust(16)
        for character in text:
            self.sendDataByte(ord(character))
        
    def sendDataByte(self, value):
        if (self.debug): print("Data Byte")
        self.sendPacket(False, value >> 4, value)

    def sendCommandByte(self, value):
        if (self.debug): print("Command Byte")
        self.sendPacket(True, value >> 4, value)
        
    def sendCommand(self, value):
        if (self.debug): print("Command")
        self.sendPacket(True, value)
        
    def sendPacket(self, command, value, value2 = None):
        self.control.setCommand(command)
        self.send(0x00)
        self.control.setWriting(True)
        self.send(0x00)
        self.control.setEnabled(True)
        self.send(value)
        self.control.setEnabled(False)
        self.send(value)
        if (value2 is not None):
            self.control.setEnabled(True)
            self.send(value2)
            self.control.setEnabled(False)
            self.send(value2)
        self.control.setWriting(False)
        self.send(0x00)
        
    def send(self, data_nibble):
        byte_to_send = self.control.asInt()
        byte_to_send |= (data_nibble & 0x0F) << 4
        self.bus.write_byte(self.address, byte_to_send)
        if (self.debug): print("Sent 0x%0.2x (%s)" % (byte_to_send,  format(byte_to_send, '#010b')))

if __name__ == '__main__':
    app = Flask(__name__)
    lcd = LCD(0x27, False)

    @app.route('/lcd/lines/<int:line>/clear')
    def set_empty_lcd_text(line):
        lcd.setText("", line)
        return "ok"
        
    @app.route('/lcd/lines/<int:line>/set/<string:text>')
    def set_lcd_text(line, text):
        lcd.setText(text, line)
        return "ok"

    @app.route('/lcd/clear')
    def clear_lcd():
        lcd.clear()
        return "ok"
        
    app.debug = True
    app.run(host='0.0.0.0')
