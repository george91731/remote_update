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
        read_bytes = list(read_msg)
        print(f'Read bytes: {" ".join(f"{byte:02X}" for byte in read_bytes)}')

        # reverse read bytes
        reversed_bytes = bytes(read_bytes[::-1])
        busy_bit = int.from_bytes(reversed_bytes, 'big')
        
        # check bit1-0 = 00
        print(f'Busy bit value at address {address:08X} after reverse: {busy_bit:08X}')
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

def program_flash_from_file(bus, file_path, START_ADDR, END_ADDR):
    addr = START_ADDR
    addr_increment = 4

    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            hex_data = line.strip().split()
            for i in range(0, len(hex_data), 4):
                if addr >= END_ADDR:
                    print(f'Reached end address: {addr:08X}')
                    return
                
                data_str = ''.join(hex_data[i:i+4])
                                        
                if len(data_str) < 8:
                    data_str = data_str.ljust(8, '0')

                try:
                    data_32bit = int(data_str, 16)
                    print(f'Programming addr {addr:08X} with data {data_32bit:08X}') 
                    program_flash(bus, [(addr, data_32bit)])
                    
                    while not read_busy_bit(bus, 0x00200020):
                        print('Checking if busy...')                

                    addr += addr_increment

                except Exception as e:
                    print(f"Error: {e} for data: {hex_data[i:i+4]}")


def main():
    with SMBus(I2C_BUS_NUMBER) as bus:  
        ######################################Image 2 flow######################################
        # 1. un-protect sector 3 & 4
        write_data(bus, 0x00200024, 0xf9ffffff)     
        
        # 2.  erase Sector3
        erase_sector(bus, 0x00200024, 0xf9bfffff)        
        
        # 3. check busy bit
        while not read_busy_bit(bus, 0x00200020):
            print('Still busy...')         
        
        # 4. erase Sector4
        erase_sector(bus, 0x00200024, 0xf9cfffff)       
        
        # 5. check busy bit
        while not read_busy_bit(bus, 0x00200020):
            print('Still busy...')            
        
        # 6. write erase sector bits to default
        write_data(bus, 0x00200024, 0xf9ffffff)   
        
        # 7. program flash
        program_flash_from_file(bus, 'Single_cfm1.txt', 0x00008000, 0x00026fff) 
 

        # 8. re-protect
        write_data(bus, 0x00200024, 0xffffffff)
        
        ######################################Image 2 flow######################################

        ######################################Image 1 flow######################################
        # 1. un-protect sector 5
        write_data(bus, 0x00200024, 0xf7ffffff)     
        
        # 2.  erase Sector3
        erase_sector(bus, 0x00200024, 0xf7dfffff)        
        
        # 3. check busy bit
        while not read_busy_bit(bus, 0x00200020):
            print('Still busy...')             
         
        # 4. write erase sector bits to default
        write_data(bus, 0x00200024, 0xf9ffffff)   
        
        # 5. program flash
        program_flash_from_file(bus, 'Single_cfm0.txt', 0x0002b000, 0x00049fff) 
 

        # 8. re-protect
        write_data(bus, 0x00200024, 0xffffffff)      

        ######################################Image 1 flow######################################
        # re-configure
        # write_data(bus, 0x00200004, 0x00000001)
        # time.sleep(0.1)

if __name__ == "__main__":
    main()
