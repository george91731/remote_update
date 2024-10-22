from smbus2 import SMBus, i2c_msg
import time

# I2C slave 地址和总线号
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
    
    for i in range(0, len(packets), 2):
        byte1 = packets[i]
        byte2 = packets[i + 1] if (i + 1) < len(packets) else 0x00
        print(f'Sending bytes: {byte1:02X}, {byte2:02X}')#
        msg = i2c_msg.write(MAX10_I2C_SLAVE_ADDRESS, [byte1, byte2])
        bus.i2c_rdwr(msg)

def erase_sector(bus, address, data):
    write_data(bus, address, data)

def read_busy_bit(bus, address):
    address_bytes = list(address.to_bytes(4, 'big'))
    for i in range(0, len(address_bytes), 2):
        byte1 = address_bytes[i]
        byte2 = address_bytes[i + 1] if (i + 1) < len(address_bytes) else 0x00
        msg = i2c_msg.write(MAX10_I2C_SLAVE_ADDRESS, [byte1, byte2])
        bus.i2c_rdwr(msg) 

    read_msg = i2c_msg.read(MAX10_I2C_SLAVE_ADDRESS, 4)
    bus.i2c_rdwr(read_msg)
    busy_bit = int.from_bytes(read_msg, 'big')
    print(f'Busy bit value at address {address:08X}: {busy_bit:08X}')
    
    return busy_bit


def program_flash(bus, address, data):
    addr_bytes = address.to_bytes(4, 'big')
    data_bytes = reverse_bytes(data).to_bytes(4, 'big')
    
    packets = addr_bytes + data_bytes
    print(f'Programming address {address:08X}: data {data:08X}')  # 打印调试信息
    
    for i in range(0, len(packets), 2):
        byte1 = packets[i]
        byte2 = packets[i + 1] if (i + 1) < len(packets) else 0x00
        msg = i2c_msg.write(MAX10_I2C_SLAVE_ADDRESS, [byte1, byte2])
        bus.i2c_rdwr(msg)

def main():
    with SMBus(I2C_BUS_NUMBER) as bus:  
        # 1. un-protect
        write_data(bus, 0x00200024, 0xfcffffff)
        time.sleep(0.1)
        
        # 2.  erase CFM2[Sector2]  ?
        erase_sector(bus, 0x00200024, 0xfcafffff)
        time.sleep(0.1)
        
        # 3. check busy bit
        while read_busy_bit(bus, 0x00200020) & 0x3 != 0x0:
            time.sleep(0.1)
        
        # 4. erase CFM1[Sector3]    ?
        erase_sector(bus, 0x00200024, 0xfcbfffff)
        time.sleep(0.1)
        
        # 5. check busy bit
        while read_busy_bit(bus, 0x00200020) & 0x3 != 0x0:
            time.sleep(0.1)
        
        # 6. write erase sector bits to default
        write_data(bus, 0x00200024, 0xfcffffff)
        time.sleep(0.1)
        
        # 7. program flash
        addr = 0x00004000
        
        # read rpd flow
        with open('123.txt', 'r') as f:
            for line in f:                
                hex_data = int(line.strip(), 16)
                data_reversed = reverse_bytes(hex_data)               
                
                program_flash(bus, addr, data_reversed)
                
                # check write done
                while read_busy_bit(bus, 0x00200020) & 0x3 != 0x0:
                    time.sleep(0.1)
                
                addr += 4
        
        # 8. re-protect
        write_data(bus, 0x00200024, 0xffffffff)
        time.sleep(0.1)

        # 9. re-configure
        write_data(bus, 0x00200004, 0x00000001)
        time.sleep(0.1)
       
if __name__ == "__main__":
    main()
