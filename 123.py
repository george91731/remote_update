    with open(file_path, 'r') as f: 
        for line in f:                   
            
            hex_data_part = line[5:54].strip()  
            hex_data = hex_data_part.split()          
            print(f'Extracted hex data: {hex_data}')
            
            for i in range(0, len(hex_data), 4):
                if addr >= END_ADDR:
                    print(f'Reached end address: {addr:08X}')
                    return
                if i + 3 >= len(hex_data):
                    break
                try:                
                    data_bytes = bytes(int(hex_data[j], 16) for j in range(i, i+4))
                    
                    if len(data_bytes) != 4:
                        print(f'Invalid data length: {len(data_bytes)} for data: {data_bytes.hex().upper()}')
                        continue

                    print(f'Programming addr {addr:08X} with data {data_bytes.hex().upper()}')                
                    
                    program_flash(bus, addr, data_bytes)

                    while not read_busy_bit(bus, 0x00200020):
                        print('check if busy...')
                    addr += 1
                except Exception as e:
                    print(f"Error: {e} for data: {hex_data[i:i+4]}")
