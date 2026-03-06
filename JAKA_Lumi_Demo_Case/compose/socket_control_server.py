#!/usr/bin/env python3
# coding:UTF-8
'''
Socket控制服务器
接收客户端命令，并根据命令运行multi_station_demo.py脚本
'''
import socket
import subprocess
import sys
import os
import signal

def start_multi_station_demo():
    """
    启动multi_station_demo.py脚本
    """
    try:
        # 使用subprocess模块运行脚本
        process = subprocess.Popen([sys.executable, "multi_station_demo.py"])
        print(f"启动multi_station_demo.py成功，进程ID: {process.pid}")
        return process
    except Exception as e:
        print(f"启动multi_station_demo.py失败: {e}")
        return None

def stop_process(process):
    """
    停止正在运行的进程
    """
    if process and process.poll() is None:
        try:
            # 发送终止信号
            process.terminate()
            print(f"已发送终止信号到进程 {process.pid}")
            return True
        except Exception as e:
            print(f"停止进程失败: {e}")
            return False
    return False

def main():
    """
    主函数 - 创建Socket服务器并处理连接
    """
    # 创建Socket服务器
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 允许端口复用
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # 绑定到本地地址和端口
    host = '0.0.0.0'  # 监听所有网络接口
    port = 9999
    
    try:
        server.bind((host, port))
        server.listen(1)
        print(f"服务器启动成功，监听 {host}:{port}")
        
        # 保存当前运行的进程实例
        current_process = None
        
        while True:
            print("等待连接...")
            client, addr = server.accept()
            print(f"收到来自 {addr} 的连接")
            
            # 接收数据
            data = client.recv(1024).decode('utf-8')
            print(f"收到命令: {data}")
            
            # 处理命令
            if data == "START_COLA_PROJECT":
                if current_process and current_process.poll() is None:
                    # 如果进程已在运行
                    response = "multi_station_demo.py 已经在运行中"
                    print(response)
                else:
                    # 启动新进程
                    current_process = start_multi_station_demo()
                    if current_process:
                        response = "multi_station_demo.py 启动成功"
                    else:
                        response = "multi_station_demo.py 启动失败"
            elif data == "STOP_DEMO":
                if current_process and stop_process(current_process):
                    response = "multi_station_demo.py 已停止"
                    current_process = None
                else:
                    response = "没有正在运行的multi_station_demo.py进程"
            elif data == "STATUS":
                if current_process and current_process.poll() is None:
                    response = "multi_station_demo.py 正在运行"
                else:
                    response = "multi_station_demo.py 未运行"
            else:
                response = f"未知命令: {data}"
            
            # 发送响应
            client.sendall(response.encode('utf-8'))
            
            # 关闭客户端连接
            client.close()
            
    except KeyboardInterrupt:
        print("\n用户中断服务器")
    except Exception as e:
        print(f"服务器错误: {e}")
    finally:
        # 关闭服务器
        server.close()
        
        # 确保所有子进程都被终止
        if current_process and current_process.poll() is None:
            stop_process(current_process)
            
        print("服务器已关闭")

if __name__ == "__main__":
    main() 