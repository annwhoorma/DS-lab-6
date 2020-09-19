"""
author: Anna Boronina
email: a.boronina@innopolis.university
telegram: @whoorma
group: DS-01
TO RUN: python3 server.py
"""

import socket
import os
import re
import threading

# host and port information
HOST = '127.0.0.1'
PORT = 8080
# buffer size for the incoming files
BUFFER_SIZE = 4096
# create server TCP socket with IPv4 and bind it to host ip and port number
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
# start listerning for incoming connections
server_socket.listen(10)
# an array with all active clients
all_cli_socks = []
# append server itself
all_cli_socks.append(server_socket)
# separator that will be used to receive file name and file size together
SEPARATOR = '<SEP>'


# class responsible for handling name collisions
class NamesMap:
    def __init__(self):
        # dictionary with existing names and number of their occurences
        self.names_map = {}
        # regex to make sure that file(1) is treated as file
        self.catch_number = re.compile(r'\(.*?\)')
        # initial call to check existing files
        self.init_names_map()
    
    
    def init_names_map(self):
        # build initial dictionary for existing files
        for file_name in os.listdir(os.getcwd()):
            number = self.catch_number.search(file_name)
            original_file_name = re.sub(r'\(.*?\)', '', file_name)
            occurences = 0
            if number is not None:
                number = number.group()
                occurences = int(number[1:len(number)-1]) 
            else:
                occurences = 1
            
            self.add_file_to_names_map(original_file_name, occurences)

    
    def add_file_to_names_map(self, file_name, number):
        # add a new file to the dictionary
        if number:
            self.names_map[file_name] = max(number, (self.names_map.get(file_name) or 0))
            return

        self.names_map[file_name] = (self.names_map.get(file_name) or 0) + 1

        new_file_name = file_name
        if self.names_map.get(file_name) > 0:
            new_file_name = '(' + str(self.names_map.get(file_name)) + ')' + file_name
        
        return new_file_name


# class responsible for creating blocking sockets for each new client
class Dobby:
    def __init__(self, sock):
        # create a thread
        threading.Thread.__init__(self)
        self.sock = sock
        # append this client's socket to the list of active sockets
        all_cli_socks.append(self.sock)

    def receive(self):
        # receive file name and file size
        data = self.sock.recv(BUFFER_SIZE).decode()
        orig_file_name, file_size = data.split(SEPARATOR)
        file_size = int(file_size)
        
        # make sure file name doesn't case name collision
        file_name = names_map.add_file_to_names_map(orig_file_name, None)
        
        # open the new file
        new_file = open(file_name, 'wb')

        total = 0
        # receive file by parts until the file is received completely
        while total != file_size:
            bytes_read = self.sock.recv(BUFFER_SIZE)

            if total == file_size:
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            new_file.write(bytes_read)

            total += len(bytes_read)
        
        new_file.close()
        print(f'I received {orig_file_name} and saved it as {file_name} :)')

    def be_free(self):
        # call this function after receiving is over and the socket is not needed anymore
        all_cli_socks.remove(self.sock)


# create dictionary of names
names_map = NamesMap()
while 1:
    # accept a new client and create a thread
    cli_sock, cli_addr = server_socket.accept()
    newthread = Dobby(cli_sock)
    # receive the client's file
    newthread.receive()
    # let the client go
    newthread.be_free()