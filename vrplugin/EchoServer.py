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
# import asyncio
import threading

"""
This script starts a server, which will use pyiron to for physics calculation and send the result to the Unity program.
"""

# cwd = os.getcwd().replace("\\", "/").split("/")
# Add the path to PYTHONPATH. This way the other scripts (e.g. Executor) can be called
# um_path = os.getcwd()[:- len(cwd[-1]) - len(cwd[-2]) - 2]
um_path = os.getcwd()
print("umpath: " + um_path)
sys.path.append(um_path)
# import UnityManager as UM
# import Structure
# import Executor

BLOCKSIZE = 4096
# IP Addresses that may connect to the server. Each new computer has to be registered here
WHITELIST = ['192.168.0.198', '192.168.0.196', '127.0.0.1', '192.168.178.152', '130.183.212.66']


# Needed for asynchronous input
class KeyboardThread(threading.Thread):
    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input()) # waits to get input + Return


# Gets called when the user enters anything in the command line
def on_input(inp):
    # evaluate the keyboard input
    print('Exiting the server')
    exit()


# start the asynchronous input thread
print("Press enter to stop the server")
input_thread = KeyboardThread(on_input)


class EchoServer:
    def __init__(self):
        # Standard loopback interface address. Should be the ip address of the server computer.
        # HOST = '192.168.0.196'  # '127.0.0.1' for localhost
        self.PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

        # set to true if the connection should be restricted to localhost
        self.useLocalhost = False

        self.t_run = True
        self.checkWhitelist = False  # set to True to use Whitelist
        self.ip_addr = self.get_ip()
        # could be used to ask new clients for a PW, determined at the start of the server
        # pwd = input("Insert the password for the server...")
        print("Waiting for connections with IP Address " + self.ip_addr)

        # a buffer for the received data
        self.data_buffer = ""

    # tries to receive some data through the socket. Returns if the socket is still connected
    def try_receive(self, connection):
        newData = connection.recv(BLOCKSIZE).decode('ASCII')
        # check if the client has disconnected
        if newData == "":
            print("Client disconnected!")
            connection.close()
            self.data_buffer = ""
            return False
        self.data_buffer += newData
        return True

    def receive_next_message(self, connection, unityManager, executor, structure):
        # if self.checkWhitelist:
        #     print('Connected by', addr)
        #     if addr[0] not in WHITELIST:
        #         print(
        #             "Address rejected: Add " + str(addr) + " to the Whitelist if it is allowed to connect")
        #         connection.close()
        #         continue
        #     self.checkWhitelist = False

        while True:
            # Message protocol: len_of_message;messagelen_of_next_message;next_message
            # Example: 20;exec_l:print("test")
            # One message will be read per loop
            while ';' not in self.data_buffer:
                if not self.try_receive(connection):
                    return
            data_split = self.data_buffer.split(';', 1)
            message_len = int(data_split[0])
            self.data_buffer = data_split[1]

            while len(self.data_buffer) < message_len:
                if not self.try_receive(connection):
                    return
            data = self.data_buffer[:message_len]
            # store the data from the next message
            self.data_buffer = self.data_buffer[message_len:]

            print('data: {}'.format(self.data_buffer))
            if data.__contains__('end server'):
                print('server will be stopped')
                # unity_manager.delete_scratch()
                # self.t_run = False
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
                    data = unityManager.on_input(data_new)
                else:
                    try:
                        data = eval(data_new)
                    except:
                        traceback.print_exc()
                        data = "error: Invalid Action\nLook at the server log for more information"

                if data is None:
                    data = "done"

                # report back to Unity of the operation could be evaluated successfully
                self.send_data(data, connection)
            elif d_lst[0] in ('exec_l', 'exec'):
                print('exec: {}'.format(data_new))
                if d_lst[0] == 'exec':
                    unityManager.on_input(data_new)
                else:
                    try:
                        exec(data_new)
                    except:
                        traceback.print_exc()
                        self.send_data("error: Invalid Action\nLook at the server log for more information",
                                       connection)
                        break
                print('exec: done')

                # report back to Unity of the operation could be executed successfully
                self.send_data('done', connection)
            else:
                self.send_data('unknown command', connection)

    # @asyncio.coroutine
    # def get_cmdline_input(loop):
    #


    def run_server(self, unityManager, executor, structure):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2.0)
            try:
                s.bind((self.ip_addr, self.PORT))
            except:
                traceback.print_exc()
                print("Look at the Troubleshoot section in the Readme for more information")
                return
                
            s.listen()
            while self.t_run:
            # while input_thread.is_alive():
                print("Timeout: ", s.gettimeout())
                print("Waiting for a client...")
                while True:
                    try:
                        connection, addr = s.accept()
                        break # TODO: comment this line in, as it crashes both programs!
                    except socket.timeout:
                        pass

                    if not input_thread.is_alive():
                        return
                # Next line crashes the program. Use it to test how the client reacts (it should not crash, but does so atm)
                print("Successfully connected! ") #  + connection
                with connection:
                    self.receive_next_message(connection, unityManager, executor, structure)

            # t_run = False

    def chunk_string(self, string, length):
        return [string[0 + i:length + i] for i in range(0, len(string), length)]

    # get the ip-address of this computer
    def get_ip(self):
        if self.useLocalhost:
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

    def send_data(self, data, conn):
        # numpy arrays an't be serialized, so they have to be converted to  list
        if isinstance(data, np.ndarray):
            data = data.tolist()
        # Unitys JsonUtility can't deserialize primitive data types, so they get send directly
        if type(data) == str or type(data) == int or type(data) == float or type(data) == bool:
            my_data = str(data)
        else:
            my_data = json.dumps(data)
        data_lst = self.chunk_string(my_data, BLOCKSIZE)
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



