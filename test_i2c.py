
我目前在樹梅派系統 想要一個簡單的python程式測試i2c的smbus功能
G
在樹莓派上，你可以使用 smbus 模組來進行 I2C 通訊。 smbus 是 Linux 系統上 I2C 使用的一個 Python 封裝。以下是一個簡單的 Python 範例，示範如何在樹莓派上使用 smbus 模組與 I2C 設備通訊。

首先，你需要確保樹莓派的 I2C 接口是開啟的，並且安裝了必要的軟體包：

開啓 I2C 介面：

在終端機中輸入 sudo raspi-config
選擇 Interfacing Options
選擇 I2C
選擇 Yes 開啓 I2C
安裝 smbus 模組:

在終端機中輸入 sudo apt-get install python3-smbus
以及 sudo apt-get install i2c-tools 用於掃描 I2C 設備
裝置好之後，可以執行以下程式：

import smbus
import time

# I2C bus number (on Raspberry Pi it's typically 1)
bus = smbus.SMBus(1)

# I2C device address (replace with your device's address)
DEVICE_ADDRESS = 0x48

# Registers (replace with your device's registers)
REGISTER_A = 0x00
REGISTER_B = 0x01

def read_register(register):
    """Read a byte from the specified register."""
    value = bus.read_byte_data(DEVICE_ADDRESS, register)
    return value

def write_register(register, value):
    """Write a byte to the specified register."""
    bus.write_byte_data(DEVICE_ADDRESS, register, value)

def main():
    try:
        while True:
            # Read from register A
            value = read_register(REGISTER_A)
            print(f"Register A value: {value}")

            # Write to register B (for example)
            write_register(REGISTER_B, 0x55)

            # Wait a bit before reading again
            time.sleep(1)
    
    except KeyboardInterrupt:
        # Exit gracefully when interrupted
        print("Exiting program")

if __name__ == "__main__":
    main()