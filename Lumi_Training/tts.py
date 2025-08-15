import serial
import serial.tools.list_ports
import time


def list_serial_ports():
    """列出所有可用的串口"""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]


def serial_communication_example(port_name, baudrate=115200, timeout=1):
    """
    串口通信示例
    :param port_name: 串口名称，如 'COM3' 或 '/dev/ttyUSB0'
    :param baudrate: 波特率，默认9600
    :param timeout: 超时时间(秒)，默认1
    """
    try:
        # 初始化串口
        ser = serial.Serial(
            port=port_name,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,  # 8位数据位
            parity=serial.PARITY_NONE,  # 无校验位
            stopbits=serial.STOPBITS_ONE,  # 1位停止位
            timeout=timeout
        )

        print(f"已连接串口: {ser.name}")
        print(f"串口设置: {ser.get_settings()}")

        # 485设备通常需要控制发送/接收模式
        # 有些USB转485适配器会自动控制，有些需要手动控制
        # 如果需要手动控制，可能需要额外的GPIO控制线

        # 示例通信
        while True:
            # 发送数据
            send_data = input("请输入要发送的数据(输入'exit'退出): ")
            if send_data.lower() == 'exit':
                break

            # 转换为字节
            send_bytes = send_data.encode('utf-8')
            print(f"发送: {send_bytes}")

            # 485设备在发送前可能需要设置发送模式
            # 例如: set_rts(True) 或 set_dtr(True)，取决于具体硬件

            ser.write(send_bytes)

            # 485设备发送完成后需要切换回接收模式
            # 例如: set_rts(False) 或 set_dtr(False)

            # 等待数据发送完成
            time.sleep(0.1)

            # 读取返回数据
            if ser.in_waiting:
                received_data = ser.read(ser.in_waiting)
                print(f"接收: {received_data}")
            else:
                print("未接收到数据")

    except serial.SerialException as e:
        print(f"串口错误: {e}")
    except KeyboardInterrupt:
        print("用户中断")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("串口已关闭")


if __name__ == "__main__":
    # 列出可用串口
    available_ports = list_serial_ports()
    print("可用串口:")
    for i, port in enumerate(available_ports, 1):
        print(f"{i}. {port}")

    if not available_ports:
        print("没有找到可用的串口!")
        exit()

    # 选择串口
    port_index = int(input("请选择要使用的串口编号: ")) - 1
    selected_port = available_ports[port_index]

    # 设置波特率 (根据你的设备要求调整)
    baudrate = int(input("请输入波特率(默认9600): ") or 9600)

    # 运行示例
    serial_communication_example(selected_port, baudrate)