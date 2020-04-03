#!/usr/bin/env python3

# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import socket
import json

import numpy as np
import os
import sys
import traceback
from pyiron.project import Project

"""
This script starts a server, which will use pyiron to for physics calculation and send the result to the Unity program.
"""

cwd = os.getcwd().replace("\\", "/").split("/")
# Add the path to PYTHONPATH. This way the other scripts (e.g. Executor) can be called
# um_path = os.getcwd()[:- len(cwd[-1]) - len(cwd[-2]) - 2]
um_path = os.getcwd()
print("umpath: " + um_path)
sys.path.append(um_path)
import UnityManager as UM
import Structure
import Executor
# import pyiron_mpie.vrplugin.UnityManager as UM

# Standard loopback interface address. Should be the ip address of the server computer.
# HOST = '192.168.0.196'  # '127.0.0.1' for localhost
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
BLOCKSIZE = 1024
# IP Addresses that may connect to the server. Each new computer has to be registered here
WHITELIST = ['192.168.0.198', '192.168.0.196', '127.0.0.1', '192.168.178.152', '130.183.212.66']
# set to true if the connection should be restricted to localhost
useLocalhost = False
# print(os.path.abspath('.'))
# startPath = os.path.join('.', '/Structures')
# print(startPath)
# pr = Project(startPath)
                            

def chunk_string(string, length):
    return [string[0 + i:length + i] for i in range(0, len(string), length)]

# get the ip-address of this computer
def get_ip():
    if useLocalhost:
        return '127.0.0.1'

    ip_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        ip_sock.connect(('10.255.255.255', 10000))
        ip = ip_sock.getsockname()[0]
    except:
        # Use localhost if the server can't connect to the internet
        ip = '127.0.0.1'
    finally:
        ip_sock.close()
    return ip


def send_data(data):
    # numpy arrays an't be serialized, so they have to be converted to  list
    if isinstance(data, np.ndarray):
        data = data.tolist()
    # Unitys JsonUtility can't deserialize primitive data types, so they get send directly
    if type(data) == str or type(data) == int or type(data) == float or type(data) == bool:
        my_data = str(data)
    else:
        my_data = json.dumps(data)
    data_lst = chunk_string(my_data, BLOCKSIZE)
    num_str = "" + str(len(my_data)) + ";"

    # send the length of the message, then the message itself
    conn.sendall(num_str.encode('ASCII'))
    for block in data_lst:
        conn.sendall(block.encode('ASCII'))

    # show the first 100 characters of the send message for debug purposes
    if len(my_data) > 100:
        print("Sending: {}{}...".format(num_str, my_data[:100]))
    else:
        print("Sending: {}{}".format(num_str, my_data))


t_run = True
checkWhitelist = False  # set to True to use Whitelist
ip_addr = get_ip()
# could be used to ask new clients for a PW, determined at the start of the server
# pwd = input("Insert the password for the server...")
print("Waiting for connections with IP Address " + ip_addr)
unity_manager = UM.UnityManager()
structureManager = Structure.Structure()
executor = Executor.Executor()
# a buffervor the received data
data_buf = ""
while t_run:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip_addr, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            if checkWhitelist:
                print('Connected by', addr)
                if addr[0] not in WHITELIST:
                    print("Address rejected: Add " + str(addr) + " to the Whitelist if it is allowed to connect")
                    conn.close()
                    continue
                checkWhitelist = False
            while True:
                # Message protocol: len_of_message;messagelen_of_next_message;next_message
                # Example: 20;exec_l:print("test")
                # One message will be read per loop
                while ';' not in data_buf:
                    data_buf += conn.recv(BLOCKSIZE).decode('ASCII')
                data_split = data_buf.split(';', 1)
                message_len = int(data_split[0])
                data_buf = data_split[1]

                while len(data_buf) < message_len:
                    data_buf += conn.recv(BLOCKSIZE).decode('ASCII')
                data = data_buf[:message_len]
                # store the data from the next message
                data_buf = data_buf[message_len:]

                print('data: {}'.format(data_buf))
                if data.__contains__('end server'):
                    print('server will be stopped')
                    # unity_manager.delete_scratch()
                    t_run = False
                    break

                # for data in data.split('%'):
                if data == "":
                    continue
                d_lst = data.split(':')
                data_new = data
                if len(d_lst) > 0:
                    data_new = ':'.join(d_lst[1:]).strip()

                if d_lst[0] in ('eval_l', 'eval'):
                    print(d_lst[0], ': {}'.format(data_new))
                    if d_lst[0] == 'eval':
                        data = unity_manager.on_input(data_new)
                    else:
                        try:
                            data = eval(data_new)
                        except:
                            traceback.print_exc()
                            data = "error: Unknown error during eval"

                    if data is None:
                        data = "done"

                    # report back to Unity of the operation could be evaluated successfully
                    send_data(data)
                elif d_lst[0] in ('exec_l', 'exec'):
                    print('exec: {}'.format(data_new))
                    if d_lst[0] == 'exec':
                        unity_manager.on_input(data_new)
                    else:
                        try:
                            exec(data_new)
                        except:
                            traceback.print_exc()
                            send_data("error: Unknown error during exec")
                            break
                    print('exec: done')

                    # report back to Unity of the operation could be executed successfully
                    send_data('done')
                else:
                    send_data('unknown command')
    # t_run = False
