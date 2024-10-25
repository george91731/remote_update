from smbus2 import SMBus, i2c_msg
import time


MAX10_I2C_SLAVE_ADDRESS = 0x55
I2C_BUS_NUMBER = 1

def reverse_bytes(data):
    byte_array = data.to_bytes(4, 'big')
    return int.from_bytes(byte_array[::-1], 'big')

def write_data(bus, address, data):   
    address_bytes = list(address.to_bytes(4, 'big'))
    data_bytes = list(reverse_bytes(data).to_bytes(4, 'big'))
    packets = address_bytes + data_bytes
    print(f'Writing to address {address:08X}: data {data:08X}')
    print(f'Sending packets: {" ".join(f"{byte:02X}" for byte in packets)}')  
    msg = i2c_msg.write(MAX10_I2C_SLAVE_ADDRESS, packets)
    bus.i2c_rdwr(msg)


def main():
    with SMBus(I2C_BUS_NUMBER) as bus:  
        # re-configure
        write_data(bus, 0x00200004, 0x00000001)        

if __name__ == "__main__":
    main()
