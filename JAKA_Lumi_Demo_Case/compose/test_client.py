#!/usr/bin/env python3
# coding:UTF-8
'''
测试客户端
用于向socket服务器发送控制命令
'''
import socket
import sys

def send_command(command):
    """
    向服务器发送命令并获取响应
    """
    try:
        # 创建客户端套接字
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 连接到服务器
        host = '127.0.0.1'  # 本地服务器地址
        port = 9999
        client.connect((host, port))
        
        # 发送命令
        client.sendall(command.encode('utf-8'))
        
        # 接收响应
        response = client.recv(1024).decode('utf-8')
        print(f"服务器响应: {response}")
        
        # 关闭连接
        client.close()
        
        return response
        
    except Exception as e:
        print(f"客户端错误: {e}")
        return None

def main():
    """
    主函数
    """
    if len(sys.argv) < 2:
        print("用法: python test_client.py <命令>")
        print("可用命令:")
        print("  START_DEMO - 启动multi_station_demo.py")
        print("  STOP_DEMO - 停止multi_station_demo.py")
        print("  STATUS - 查询multi_station_demo.py运行状态")
        return
        
    command = sys.argv[1]
    send_command(command)

if __name__ == "__main__":
    main() 