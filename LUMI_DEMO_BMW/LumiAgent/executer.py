# from JAKA_SDK_LINUX import jkrc
# import time
# # robot = jkrc.RC("192.168.1.100")
# robot = jkrc.RC("192.168.10.90")
# ret = robot.login(1)
# print(ret[0])
# robot.power_on()
# robot.enable_robot()
# # robot.set_tio_model(model = 1)
# # robot.set_til_rs485_param(baud_rata=115200)
# # command =[0X01, 0]
# # 夹爪打开
# # robot.set_analog_output(1, 0, 1)
# # time.sleep(1)
# # robot.set_analog_output(1, 1, 1)
# # time.sleep(1)
# # robot.set_analog_output(1, 2, 1)
# # time.sleep(1)
# # robot.set_analog_output(0, 0, 1)
# # time.sleep(1)
# # robot.set_analog_output(0, 1, 1)
# # time.sleep(1)
# # robot.set_analog_output(0, 2, 1)
# # time.sleep(1)
# # robot.set_digital_output(1, 0, 1)

# robot.set_digital_output(1, 0, 1)

# # robot.set_digital_output(1, 2, 1)

# # robot.set_digital_output(1, 3, 1)

# # robot.set_digital_output(1, 4, 1)

# # robot.set_digital_output(1, 5, 1)

# # robot.set_digital_output(1, 6, 1)

# # robot.set_digital_output(1, 7, 1)

# # robot.set_digital_output(1, 8, 1)

# # robot.set_digital_output(1, 9, 1)
# # robot.set_digital_output(1, 10, 1)
# # time.sleep(1)

# # robot.set_digital_output(1, 10, 0)
# # time.sleep(1)

# # robot.set_digital_output(1, 1, 0)
# # time.sleep(1)
# # # robot.set_digital_output(1, 11, 1)
# # # robot.set_digital_output(1, 12, 1)
# # # robot.set_digital_output(1, 13, 1)
# # # robot.set_digital_output(1, 14, 1)
# # # robot.set_digital_output(1, 15, 1)
# # robot.logout()
# # robot.set_digital_output(1, 96, 1)
# # 
# # robot.set_digital_output(1, 1, 20)
# # time.sleep(1)
# # robot.set_digital_output(1, 2, 20)
# # time.sleep(1)
# # robot.set_digital_output(0, 0, 20)
# # time.sleep(1)
# # robot.set_digital_output(0, 1, 20)
# # time.sleep(1)
# # robot.set_digital_output(0, 2, 1)
# # time.sleep(1)
# # robot.set_digital_output(2, 0, 1)
# # time.sleep(1)
# # robot.set_digital_output(2, 1, 1)
# # time.sleep(1)
# # robot.set_digital_output(2, 2, 1)
# # time.sleep(1)
# # # # 夹爪全闭
# # robot.set_digital_output(1, 0, 1)
# # time.sleep(1)
# # # # 夹爪半闭
# # robot.set_digital_output(1, 1, 1)
# # time.sleep(1)
# # robot.logout()

# # import struct
# # # ==========================================

# # # # 辅助函数：计算 Modbus CRC16 校验码

# # # # ==========================================

# # def calculate_crc16(data: bytearray) -> bytearray:
# #     crc = 0xFFFF
# #     for pos in data:
# #         crc ^= pos
# #         for i in range(8):
# #             if (crc & 1) != 0:
# #                 crc >>= 1
# #                 crc ^= 0xA001
# #             else:
# #                 crc >>= 1
# #                         # 交换高低字节 (Modbus 小端模式)   
# #     return struct.pack('<H', crc)


# # ret = robot.set_tool_485_param(115200, 8, 0, 1)

# # # 2. 【重要】开启末端 T485 电源
# # # 参数说明：0=0V, 1=12V, 2=24V (具体视控制柜版本而定，通常3或2是24V，建议查阅手册)
# # print("开启末端电源...")
# # robot.set_tool_voltage(3) 
# # time.sleep(2) # 等待从站设备启动

# # # 3. 设置通讯通道参数 (必须与您的从站设备一致)
# # # baud_rate: 115200 (常用: 9600, 19200, 38400, 115200)
# # # data_bits: 8
# # # parity: 0 (0:None, 1:Odd, 2:Even)
# # # stop_bits: 1
# # print("配置 RS485 通道...")
# # ret = robot.set_tool_data(115200, 8, 0, 1)
# # if ret[0] != 0:
# #     print(f"通道配置失败，错误码: {ret}")

# # # 4. 构造数据参数
# # # 您的目标指令: 01 (站号) 06 (写寄存器) 01 00 (寄存器地址) 00 01 (写入值)
# # raw_cmd = [0x01, 0x06, 0x01, 0x00, 0x00, 0x01]
# # byte_cmd = bytearray(raw_cmd)

# # # 自动追加 CRC 校验码 (结果变成 01 06 01 00 00 01 49 56)
# # crc = calculate_crc16(byte_cmd)
# # final_cmd = byte_cmd + crc 

# # # 转换为 list 格式供 SDK 使用seraial
# # send_data = list(final_cmd)

# # print(f"发送完整指令 (Hex): {[hex(x) for x in send_data]}")

# # # 5. 发送数据 (tool_serial_write)
# # # 参数：(数据列表, 数据长度)
# # ret = robot.tool_serial_write(send_data, len(send_data))

# # if ret[0] == 0:
# #     print(">>> 发送成功")  
# #     # 6. (可选) 读取设备返回的确认帧\n   # 假设设备会立即返回 8 个字节\n   
# #     time.sleep(0.1)    
# #     recv = robot.tool_serial_read(8) 
# #     if recv[0] == 0:
# #         print(f"<<< 收到反馈: {[hex(x) for x in recv[1]]}")
# #     else:
# #         print("未收到反馈或读取超时")
# # else:
# #    print(f"发送失败，错误码: {ret}")

# # robot.logout()
#!/usr/bin/env python3
"""Example: call the gripper helper from another Python program."""

import time

import serial

from utilfs.python_open_gripper import ensure_initialized, move_gripper,command_gripper


if __name__ == "__main__":
    # sample usage: open then close
    command_gripper(0, position=1000)
    time.sleep(1.0)
    command_gripper(0, position=100)
    time.sleep(1.0)
    # command_gripper(1, position=0)
