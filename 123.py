
def program_flash_from_file(bus, file_path, START_ADDR, END_ADDR):
    addr = START_ADDR

    with open(file_path, 'r') as f:  # 以文本模式读取文件
        for line in f:
            # 打印读取的每行调试信息
            print(f'Raw line: "{line.strip()}"')

            # 提取每行中间的数据信息
            print(f'Extracted hex data: {hex_data}')

            for i in range(0, len(hex_data), 4):
                if addr >= END_ADDR:
                    print(f'Reached end address: {addr:08X}')
            hex_data_part = line[6:53].strip()  # 从第7个字符到第53个字符处提取数据部分
            hex_data = hex_data_part.split()
            
            # 打印提取的十六进制数据部分
                    return
                if i + 3 >= len(hex_data):
                    break
                try:
                    # 连接分段数据形成32位整数
                    data_str = ''.join(hex_data[i:i+4])
                    
                    # 确保数据长度为8个字符
                    if len(data_str) != 8:
                        print(f'Invalid hex data length: {data_str} (from segments {hex_data[i:i+4]})')
                        continue

                    data_32bit = int(data_str, 16)
                    addr_bytes = addr.to_bytes(4, 'big')
                    data_bytes = data_32bit.to_bytes(4, 'big')
                    packets = addr_bytes + data_bytes

                    print(f'Programming address {addr:08X}: data {data_32bit:08X}')
                    print(f'Sending packets: {" ".join(f"{byte:02X}" for byte in packets)}')

                    msg = i2c_msg.write(0x50, packets)  # 0x50 是 I2C 设备地址，根据实际情况修改
                    bus.i2c_rdwr(msg)

                    addr += 4
                except Exception as e:
                    print(f"Error: {e} for data: {hex_data[i:i+4]}")
