import socket
import json
import keyboard
import time
import os

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
# /api/move?marker=target_name&uuid=123456”
def on_key_event(key):
    v = 0.1
    r = 0.1
    if key == "up":
        return v,0 
    elif key == "down":
        return -v,0
    elif key == "left":
        return 0,r
    elif key == "right":
        return 0,-r
    elif key == "release":
        r = 0
        v=  0
        return f"angular_velocity={r}&linear_velocity={v}"
    return None

if __name__ == "__main__":
    HOST = "192.168.10.10"  # Replace with the server's IP address
    PORT = 31001        # Replace with the server's port number
    COMMAND = "/api/joy_control"

    print("Use arrow keys to control. Press ESC to exit.")
    os.system('stty -echo')  # Disable terminal echo
    while True:
        param_str = ""
        try:
            v = 0
            r = 0
            vrun = 0.5
            rrun = 0.3
            if keyboard.is_pressed("up"):
                v = vrun
            elif keyboard.is_pressed("down"):
                v = -vrun        

            if keyboard.is_pressed("left"):
                r = rrun
            elif keyboard.is_pressed("right"):
                r = -rrun

            param_str = f"angular_velocity={r}&linear_velocity={v}"

            time.sleep(0.1)
            # print("param_str:", param_str)
            # continue

            if param_str:
                cmd = COMMAND + "?" + param_str + "&uuid=123456"
                response = send_command_and_receive_response(cmd, HOST, PORT)
                if response:
                    print("Received response:")
                    print(json.dumps(response, indent=4))
                else:
                    print("Failed to get a valid response.")
        except KeyboardInterrupt:
            print("Exiting...")
            break

    # response = send_command_and_receive_response(COMMAND, HOST, PORT)
    # if response:
    #     print("Received response:")
    #     print(json.dumps(response, indent=4))
    # else:
    #     print("Failed to get a valid response.")
