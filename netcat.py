import subprocess
import threading
import argparse
import socket
import sys

# run commands in host
def run_command(cmd):
    cmd = cmd.strip()
    try:
        # run command and return received output
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except Exception as e:
        print(e)
        print('[!] Failed to execute command: {}'.format(cmd))
        return 'Failed to execute command: {}\r\n'.format(cmd).encode()
    return output

# client side connection logic
def handle_client_connection(client_socket, client_address):

    print('Connected to client at {}.'.format(client_address))
    # check if we are supposed to write client input to a file (-o)
    if args.outfile:
        file_input = ""
        print('[!] Writing input from client at {} to {}.'.format(client_address, output_destination))
        # keep reading data until none is left
        with open(output_destination, 'w') as of:
            while True:
                data = client_socket.recv(1024)
                if not data or data.decode() == '\r\n' or data.decode() == '\n':
                    break
                # write data to file
                of.write(data.decode())
        # sending content
        client_socket.sendall('[!] Successfully saved file to {}.\r\n'.format(output_destination).encode())

    # check if we are supposed to execute a command (-e)
    if args.execute:
        output = run_command(execute)
        client_socket.sendall(output)

    # check if a command shell was requested (-c)
    if args.command:
        while True:
            client_socket.sendall('shell> '.encode())
            # receive data until we get a line feed pattern
            cmd_buffer = ''
            while '\n' not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()
            # run the command and send the output back to the client
            if cmd_buffer.strip() == 'exit':
                client_socket.sendall('[!] Exit code received, closing terminal.\r\n'.encode())
                break
            output = run_command(cmd_buffer)
            client_socket.sendall(output)

    # closing socket
    client_socket.close()

# socket definition
def start_server(listen_host, listen_port):

    # start listening
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((listen_host, listen_port))
    server.listen(5)

    # wait for inbound connections
    while True:
        client_socket, addr = server.accept()
        # start new thread to handle this connection
        client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, addr))
        client_thread.start()

# client connection logic
def client_send(target_host, target_port, data=None):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to target host
    try:
        client.connect((target_host, target_port))
        if data:
            client.sendall(data.encode())
        while True:
            # wait for response from target host
            recv_len = 1
            response = ''
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data.decode()
                if recv_len < 4096:
                    break
            print(response)
            # get further input from user
            print('[+] Enter further input or press CTRL-D for no input.')
            data = sys.stdin.readline()
            client.sendall(data.encode())
    except Exception as e:
        print(e)
        print('[*] Exiting program.')
        client.close()

if __name__ == '__main__':

    # define global variables
    output_destination = ""
    command = False
    verbose = False
    execute = ""

    # parse command line input arguments
    parser = argparse.ArgumentParser(description='Custom Netcat alternative.')
    parser.add_argument('-l', '--listen', action='store_true', help='Listen for incoming connections')
    parser.add_argument('-e', '--execute', help='Execute the given command after receiving a connection')
    parser.add_argument('-c', '--command', action='store_true', help='Initialize a command shell')
    parser.add_argument('-o', '--outfile', help='Write input data to the given file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print verbose messages')
    parser.add_argument('target_host', help='IP or hostname to connect to or listen on')
    parser.add_argument('port', type=int, help='Port to connect to or listen on')
    args = parser.parse_args()

    # assign input arguments
    output_destination = args.outfile
    target_host = args.target_host
    execute = args.execute
    command = args.command
    verbose = args.verbose
    listen = args.listen

    # casting the input port
    port = int(args.port)

    if listen:
        print('Listening for incoming connections on TCP {}:{}.'.format(target_host, port))
        start_server(target_host, port)
    else:
        print('Connecting to TCP {}:{}. Enter input or press CTRL-D for no input.'.format(target_host, port))
        # get input from STDIN if provided
        data = sys.stdin.readline()
        # connect to server
        client_send(target_host, port, data)
