import rclpy
from rclpy.node import Node
import threading
import socket
from std_msgs.msg import String  # 导入标准字符串消息类型
import time

class VrSocketServer(Node):

    def __init__(self):
        super().__init__('vr_socket_server')
        self.publisher_ = self.create_publisher(String, '/vr_raw_data', 10)  # 创建publisher
        self.declare_parameter('server_port', 8000)
        self.server_port = self.get_parameter('server_port').get_parameter_value().integer_value
        self.server_thread = None
        self.server_running = False

    def start_server(self, host='0.0.0.0', port=8000):
        self.server_running = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()
            self.get_logger().info(f"Server is listening on {host}:{port}")
            while self.server_running:
                try:
                    conn, addr = s.accept()
                    self.get_logger().info(f"Connected by {addr}")
                    # 设置接收超时(5秒)
                    conn.settimeout(5.0)  
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(conn, addr),
                        daemon=True
                    )
                    client_thread.start()
                except socket.timeout:
                    self.get_logger().info("Accept timeout, retrying...")
                    continue
                except Exception as e:
                    self.get_logger().info(f"Error accepting connection: {e}")

    def handle_client(self, conn, addr):
        buffer = ""
        packet_count = 0
        start_time = time.time()
        try:
            while self.server_running:
                data = conn.recv(1024)
                if not data:
                    self.get_logger().info(f"Client {addr} disconnected.")
                    break
                buffer += data.decode('utf-8')
                while '\n' in buffer:
                    index = buffer.index('\n') + 1
                    decoded_data = buffer[:index].strip()
                    buffer = buffer[index:]
                    # 发布消息到/vr_raw_data话题
                    msg = String()
                    msg.data = decoded_data
                    self.publisher_.publish(msg)
                    self.get_logger().info(f"Published to /vr_raw_data: '{msg.data}'")
        finally:
            conn.close()

    def start_server_thread(self):
        self.server_thread = threading.Thread(target=self.start_server, args=('0.0.0.0', self.server_port))
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop_server(self):
        self.server_running = False
        if self.server_thread:
            self.server_thread.join()
        self.get_logger().info("Server stopped.")

def main(args=None):
    rclpy.init(args=args)
    vr_socket_server = VrSocketServer()
    vr_socket_server.start_server_thread()

    try:
        rclpy.spin(vr_socket_server)
    except KeyboardInterrupt:
        vr_socket_server.get_logger().info("KeyboardInterrupt caught. Stopping server...")
    finally:
        vr_socket_server.stop_server()
        vr_socket_server.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()