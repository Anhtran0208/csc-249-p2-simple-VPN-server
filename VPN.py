#!/usr/bin/env python3

import socket
import arguments
import argparse
from datetime import datetime
import pytz

# Run 'python3 VPN.py --help' to see what these lines do
parser = argparse.ArgumentParser('Send a message to a server at the given address and prints the response')
parser.add_argument('--VPN_IP', help='IP address at which to host the VPN', **arguments.ip_addr_arg)
parser.add_argument('--VPN_port', help='Port number at which to host the VPN', **arguments.vpn_port_arg)
args = parser.parse_args()

VPN_IP = args.VPN_IP  # Address to listen on
VPN_PORT = args.VPN_port  # Port to listen on (non-privileged ports are > 1023)

def parse_message(message):
    try:
        message_arr = message.split(' ', 1)
        if len(message_arr) < 2:
            raise ValueError("Invalid message format")
        
        operation, mess = message_arr[0], message_arr[1]
        if operation.lower() != 'convert_timezone' and operation.lower() != 'shift_right':
            raise ValueError('Unsupported operation. We only support convert_timezone or shift_right')
        return operation, mess
    except Exception as e:
        print(f"Error parsing message: {e}")
        return None, None

def convert_timezone(input_time, from_tz, to_tz):
    """
    Convert the input time at the current from_tz timezone to to_tz timezone
    """
    try:
        #format of date time
        time_format = "%Y-%m-%d %H:%M:%S"
        curr_time_format = datetime.strptime(input_time, time_format)
        
        # get the from_timezone
        from_tz = pytz.timezone(from_tz)
        # format from_timezone
        local_time = from_tz.localize(curr_time_format)
        
        # get the to_timezone
        to_tz = pytz.timezone(to_tz)
        # convert to_timezone
        convert_time = local_time.astimezone(to_tz)
        
        return convert_time.strftime(time_format)
    except Exception as e:
        return f"Error converting time zone: {str(e)}"

def shift_right(input):
    """
    Take input and shift each character to the next one in the ASCII table
    """
    try:
        result = ''.join(chr(ord(char) + 1) for char in input)
        return result
    except Exception as e:
        return f"Error shifting string: {e}" 
    
def start_vpn_server():
    print("VPN starting - listening for connections at IP", VPN_IP, "and port", VPN_PORT)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((VPN_IP, VPN_PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected established with {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                print(f"Received client message: {message}")
                
                operation, mess = parse_message(message)
                if operation.lower() == 'convert_timezone':
                    mess_arr = mess.split()
                    if len(mess_arr) != 4:
                        response = 'Invalid format for converting time zone'
                    else:
                        input_time = f"{mess_arr[0]} {mess_arr[1]}"
                        from_tz, to_tz = mess_arr[2], mess_arr[3]
                        response = convert_timezone(input_time, from_tz, to_tz)
                
                elif operation.lower() == 'shift_right':
                    response = shift_right(mess)
                
                conn.sendall(response.encode('utf-8'))
                print(f"Sent {response} back to client")

        print('Server is done')
if __name__ == '__main__':
    start_vpn_server()        
