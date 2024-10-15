from smbus2 import SMBus, i2c_msg
import time

# i2c slave addr
MAX10_I2C_SLAVE_ADDRESS = 0x41
I2C_BUS_NUMBER = 1

# initialize
bus = SMBus(I2C_BUS_NUMBER)


# 讀取RPD檔案
def read_rpd_file(file_path):
    
    with open(file_path, 'rb') as file:
        rpd_data = file.read()
        print(rpd_data)
    return rpd_data

def wait_for_ack():
    ack = bus.read_byte
    try:       
        _ = bus.read_byte()
        return True
    except IOError:
        return False

def write_unprotect_sector(bus, address, data):
    msg = i2c_msg.write(MAX10_I2C_SLAVE_ADDRESS, [address] + list(data.to_bytes(4, 'big')))
    bus.i2c_rdwr(msg)

def erase_sector(bus, address, data):
    msg = i2c_msg.write(MAX10_I2C_SLAVE_ADDRESS, [address] + list(data.to_bytes(4, 'big')))
    bus.i2c_rdwr(msg)

def read_busy_bit(bus, address):
    # Write address to read from
    write_msg = i2c_msg.write(MAX10_I2C_SLAVE_ADDRESS, [address])
    bus.i2c_rdwr(write_msg)
    # Read 4 bytes of data
    read_msg = i2c_msg.read(MAX10_I2C_SLAVE_ADDRESS, 4)
    bus.i2c_rdwr(read_msg)
    return list(read_msg)

def program_flash(bus, address, data):
    msg = i2c_msg.write(MAX10_I2C_SLAVE_ADDRESS, [address] + list(data.to_bytes(4, 'big')))
    bus.i2c_rdwr(msg)

def re_protect_sector(bus, address, data):
    msg = i2c_msg.write(MAX10_I2C_SLAVE_ADDRESS, [address] + list(data.to_bytes(4, 'big')))
    bus.i2c_rdwr(msg)

def re_configure(bus, address, data):   
    msg = i2c_msg.write(MAX10_I2C_SLAVE_ADDRESS, [address] + list(data.to_bytes(4, 'big')))
    bus.i2c_rdwr(msg)

def main():
    with SMBus(1) as bus:  
        # Unprotect Sector
        write_unprotect_sector(bus, 0x00200024, 0xfcffffff)
        
        # Erase Sector CFM2[Sector2]
        erase_sector(bus, 0x00200024, 0xfcafffff)
        
        # Check if erase done
        busy_bit = read_busy_bit(bus, 0x00200020)
        print(f"Erase Check: {busy_bit}")
        
        # Erase Sector CFM1[Sector3]
        erase_sector(bus, 0x00200024, 0xfcbfffff)
        
        # Check if erase done
        busy_bit = read_busy_bit(bus, 0x00200020)
        print(f"Erase Check: {busy_bit}")
        
        # Reset erase bits to default
        write_unprotect_sector(bus, 0x00200024, 0xfcffffff)
        
        # Programming Flash
        # Read the data from file
        with open('123.txt', 'r') as f:
            addr = 0x00004000
            for line in f:           
                hex_data = line.strip().split()         
                program_flash(bus, addr, hex_data)
                
                # 驗證寫入
                busy_bit = read_busy_bit(bus, 0x00200020)
                print(f"Write Check at {hex(addr)}: {busy_bit}")                 
                addr += 4
        
        # Re-protect sectors
        re_protect_sector(bus, 0x00200024, 0xffffffff)    
        # Re-Configure
        re_configure(bus, 0x00200004, 0x00000001)

        
if __name__ == "__main__":
    main()

#照bmc_PROGRAM文件步驟下指令，依照各個動作分別設定function





rpd_file_path = 'D:\Training\remoteupdate\RPi\rpd_file\ '
# update_firmware(rpd_file_path)
read_rpd_file(rpd_file_path)


