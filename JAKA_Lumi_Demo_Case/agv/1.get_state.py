import socket
import json

def send_command_and_receive_response(command, host, port):
    try:
        # Create a TCP/IP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to the server
            sock.connect((host, port))
            
            # Send the command
            sock.sendall(command.encode('utf-8'))
            
            # Receive the response
            response = sock.recv(4096).decode('utf-8')
            
            # Parse the JSON response
            response_json = json.loads(response)
            return response_json
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    HOST = "192.168.10.10"  # Replace with the server's IP address
    PORT = 31001        # Replace with the server's port number
    COMMAND = "/api/robot_status"
    for i in range(10):
        response = send_command_and_receive_response(COMMAND, HOST, PORT)
        if response:
            print("Received response:")
            print(json.dumps(response, indent=4))
        else:
            print("Failed to get a valid response.")