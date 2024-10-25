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

def erase_sector(bus, address, data):
    write_data(bus, address, data)

def read_busy_bit(bus, address):    
    address_bytes = list(address.to_bytes(4, 'big'))
    print(f'Sending address for reading busy bit check: {" ".join(f"{byte:02X}" for byte in address_bytes)}') 
    write_msg = i2c_msg.write(MAX10_I2C_SLAVE_ADDRESS, address_bytes)
    try:
        bus.i2c_rdwr(write_msg)
    except Exception as e:
        print(f"Write Address Error: {e}")    

    read_msg = i2c_msg.read(MAX10_I2C_SLAVE_ADDRESS, 4)
    try:
        bus.i2c_rdwr(read_msg)
        busy_bit = int.from_bytes(read_msg, 'big')
        print(f'Busy bit value at address {address:08X}: {busy_bit:08X}')
        
        if (busy_bit & 0x3) == 0x0:
            print(f'Slave is idle')
            return True  
        else:
            print(f'Slave is busy')
            return False
            
    except Exception as e:
        print(f"Read Error: {e}")
        return False


def program_flash(bus, address, data):
    addr_bytes = address.to_bytes(4, 'big')
    data_bytes = data.to_bytes(4, 'big')    
    packets = addr_bytes + data_bytes
    print(f'Programming address {address:08X}: data {data:08X}')     
    print(f'Sending packets: {" ".join(f"{byte:02X}" for byte in packets)}')
    msg = i2c_msg.write(MAX10_I2C_SLAVE_ADDRESS, packets)
    bus.i2c_rdwr(msg)


def main():
    with SMBus(I2C_BUS_NUMBER) as bus:  
        # 1. un-protect
        write_data(bus, 0x00200024, 0xfcffffff)     
        
        # 2.  erase CFM2[Sector2]  ?
        erase_sector(bus, 0x00200024, 0xfcafffff)        
        
        # 3. check busy bit
        while not read_busy_bit(bus, 0x00200020):
            print('Still busy...')
            time.sleep(0.1)
        
        # 4. erase CFM1[Sector3]    ?
        erase_sector(bus, 0x00200024, 0xfcbfffff)       
        
        # 5. check busy bit
        while not read_busy_bit(bus, 0x00200020):
            print('Still busy...')
            time.sleep(0.1)
        
        # 6. write erase sector bits to default
        write_data(bus, 0x00200024, 0xfcffffff)
   
        
        # 7. program flash
        addr = 0x00004000         
 
        with open('Single.txt', 'r') as f:
            for line in f:
                hex_data = line.strip().split()              
                for i in range(0, len(hex_data), 4):
                    if i + 3 >= len(hex_data):
                        break
                    data_32bit = int(''.join(hex_data[i:i+4]), 16)                   
                    program_flash(bus, addr, data_32bit)  

                    while not read_busy_bit(bus, 0x00200020):
                        print('Still busy...')
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
