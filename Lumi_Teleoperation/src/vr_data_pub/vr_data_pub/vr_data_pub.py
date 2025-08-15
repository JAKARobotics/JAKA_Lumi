import rclpy
from rclpy.node import Node
import threading
import socket
from std_msgs.msg import String  # 导入标准字符串消息类型

class VrSocketServer(Node):

    def __init__(self):
        super().__init__('vr_socket_server')
        self.publisher_ = self.create_publisher(String, '/vr_raw_data', 10)  # 创建publisher
        self.declare_parameter('server_port', 8000)
        self.server_port = self.get_parameter('server_port').get_parameter_value().integer_value
        self.start_server_thread()

    def start_server(self, host='0.0.0.0', port=8000):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # 设置SO_REUSEADDR选项以快速重用地址和端口
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((host, port))
                s.listen(5)
                self.get_logger().info(f"Server started on {host}:{port}")
                while True:
                    conn, addr = s.accept()
                    with conn:
                        self.get_logger().info(f"Connected by {addr}")
                        while True:
                            data = conn.recv(1024)
                            if not data:
                                break
                            message = data.decode()
                            self.get_logger().info(f"Received: {message}")
                            
                            # 发布消息到/vr_data话题
                            msg = String()
                            msg.data = message
                            self.publisher_.publish(msg)
                            self.get_logger().info(f"Published to /vr_raw_data: '{msg.data}'")

                            # 回传给客户端（可选）
                            # conn.sendall(data)
            except KeyboardInterrupt:
                self.get_logger().info("Caught keyboard interrupt, exiting")
            finally:
                s.close()  # 确保在任何情况下都关闭socket

    def start_server_thread(self):
        server_thread = threading.Thread(target=self.start_server(port=self.server_port))
        server_thread.daemon = True
        server_thread.start()

def main(args=None):
    rclpy.init(args=args)
    vr_socket_server = VrSocketServer()

    try:
        rclpy.spin(vr_socket_server)
    except KeyboardInterrupt:
        pass
    finally:
        vr_socket_server.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()