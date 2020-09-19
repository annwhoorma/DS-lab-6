"""
author: Anna Boronina
email: a.boronina@innopolis.university
telegram: @whoorma
group: DS-01
TO RUN: python client.py <full/path/to/file> <public_ip> 8080
"""

import socket
import sys
import os
import time
import tqdm

# open the file in a binary reading mode that must be specified after the script name
file = open(sys.argv[1], 'rb')
# get file's name without its path
file_name = os.path.basename(file.name)
# get file's size
file_size = os.path.getsize(sys.argv[1])

# get host and port number
host = sys.argv[2]
port = int(sys.argv[3])
# initialize a TCP socket with IPv4
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connect to the server
sock.connect((host, port))

# specify buffer size for sending the file
BUFFER_SIZE = 4096
# specify the separator. must be the same as for the server
SEPARATOR = '<SEP>'


try:
    # send file info - name and size
    sock.send(f"{file_name}{SEPARATOR}{file_size}".encode('utf-8'))
    progress = tqdm.tqdm(range(file_size), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
    reading_finished = False
    # start sending the file itself and show the progress bar
    for _ in progress:
        while True and not reading_finished:
            # read BUFFER_SIZE bytes from the file 
            bytes_read = file.read(BUFFER_SIZE)
            if not bytes_read:
                # file has been transmitted
                reading_finished = True
            
            # use sendall to assure that all the bytes will be transmitted
            sock.sendall(bytes_read)

            # update the progress bar
            progress.update(len(bytes_read))

    # close the file
    file.close()

finally:
    # close the socket
    sock.close()

