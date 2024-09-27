#!/usr/bin/env python3

# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import socket
import json
from time import sleep

import numpy as np
import threading

"""
This script starts a server, which will use pyiron to for physics calculation and send the result to the Unity program.
"""

BLOCKSIZE = 4096
# IP Addresses that may connect to the server. Each new computer has to be registered here
WHITELIST = [
    "192.168.0.198",
    "192.168.0.196",
    "127.0.0.1",
    "192.168.178.152",
    "130.183.212.66",
]


# Needed for asynchronous input
class KeyboardThread(threading.Thread):
    def __init__(self, name="keyboard-input-thread"):
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        sleep(1)
        while True:
            self.input_cbk(
                input('write "q" to stop server:')
            )  # waits to get input + Return

    def input_cbk(self, inp):
        if inp in ["q", "quit", "exit"]:
            self._stop_application()

    @staticmethod
    def _stop_application():
        # The server will stop when no client is connected
        print("Exiting the server")
        exit()


class EvalSentMassages:
    def __init__(self, unity_manager, structure, executor):
        self.unity_manager = unity_manager
        self.structure = structure
        self.executor = executor
        self.eval_methods = {
            "structure.create": self.structure.create,
            "unityManager.project.path": self._getitem_project_path,
            "unityManager.project.list_all": self.unity_manager.project.list_all,
        }
        self._parse_args_for = {
            "structure.create": self._parse_structure_args,
            "unityManager.project.path": self._parse_project_path_getitem,
            "unityManager.project.list_all": self._parse_pr_list_all_args,
        }
        self.exec_methods = {
            "unityManager.project =": self._set_unity_manager_project
        }

    def _set_unity_manager_project(self, msg: str):
        if msg.strip().startswith("Project(") and msg.endswith(")"):
            self.unity_manager.project = self.unity_manager.project.__class__(
                msg.strip()[len("Project(") : -1]
            )

    def _getitem_project_path(self, slice_obj):
        return self.unity_manager.path[slice_obj]

    @staticmethod
    def _parse_pr_list_all_args(msg: str):
        if msg == "()":
            return []
        else:
            raise ValueError(msg)

    @staticmethod
    def _parse_project_path_getitem(item_str: str):
        slc = []
        if item_str.startswith("[") and item_str.endswith("]"):
            for item in item_str.split(":"):
                if item == "":
                    slc.append(None)
                else:
                    slc.append(int(item))
            return slice(*slc)
        else:
            raise ValueError(item_str)

    @staticmethod
    def _convert_str_bool_to_python_bool(str_bool: str):
        if str_bool.strip() == "True":
            return True
        elif str_bool.strip() == "False":
            return False
        else:
            raise ValueError(f"Expected a string with 'True' or 'False' not '{str_bool}'")

    def _parse_structure_args(self, msg: str):
        """parses the arguments for structure.create. Expects '(str, int, bool, bool)'"""
        if msg.startswith("(") and msg.endswith(")"):
            s = msg[1:-1].split(",")
            if len(s) != 4:
                raise ValueError(f"No valid msg={msg}, should have 4 members: {s}")
            s[0] = s[0][1:-1]
            s[1] = int(s[1])
            s[2] = self._convert_str_bool_to_python_bool(s[2])
            s[3] = self._convert_str_bool_to_python_bool(s[3])
            return s
        else:
            raise ValueError(msg)

    def eval(self, message: str):
        for method in self.eval_methods:
            if message.startswith(method):
                args = self._parse_args_for[method](message[len(method) :])
                return self.eval_methods[method](*args)
        raise ValueError(f"No such method {message}")

    def exec(self, message: str):
        for method in self.exec_methods:
            if message.startswith(method):
                self.exec_methods[method](message[len(method) :])
                return
        raise ValueError(f"No such method {message}")


class EchoServer:
    def __init__(
        self, unity_project, structure, executor, port=65432, use_localhost=True
    ):
        # Standard loopback interface address. Should be the ip address of the server computer.
        # HOST = '192.168.0.196'  # '127.0.0.1' for localhost
        self.PORT = port  # Port to listen on (non-privileged ports are > 1023)
        self._eval = EvalSentMassages(unity_project, structure, executor)

        # set to true if the connection should be restricted to localhost
        self.useLocalhost = use_localhost

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
        new_data = connection.recv(BLOCKSIZE).decode("ASCII")
        # check if the client has disconnected
        if new_data == "":
            print("Client disconnected!")
            connection.close()
            self.data_buffer = ""
            return False
        self.data_buffer += new_data
        return True

    def receive_next_message(self, connection):
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
            # Example: 20;exec:print("test")
            # One message will be read per loop
            while ";" not in self.data_buffer:
                if not self.try_receive(connection):
                    return
            data_split = self.data_buffer.split(";", 1)
            message_len = int(data_split[0])
            self.data_buffer = data_split[1]

            while len(self.data_buffer) < message_len:
                if not self.try_receive(connection):
                    return
            data = self.data_buffer[:message_len]
            # store the data from the next message
            self.data_buffer = self.data_buffer[message_len:]

            print("data: {}".format(self.data_buffer))
            if data.__contains__("end server"):
                print("server will be stopped")
                break

            if data == "":
                continue
            d_lst = data.split(":")
            data_new = data
            if len(d_lst) > 0:
                data_new = ":".join(d_lst[1:]).strip()

            if d_lst[0] == "eval":
                print(d_lst[0], ": {}".format(data_new))
                try:
                    with open("eval_data.log", "a") as f:
                        f.write(data_new)
                    data = self._eval.eval(data_new)
                except Exception as err:
                    print(err)
                    data = "error: Invalid Action\nLook at the server log for more information"

                if data is None:
                    data = "done"

                # report back to Unity of the operation could be evaluated successfully
                self.send_data(data, connection)
            elif d_lst[0] == "exec":
                print("exec: {}".format(data_new))
                try:
                    with open("exec_data.log", "a") as f:
                        f.write(data_new)
                    self._eval.exec(data_new)
                except Exception as err:
                    print(err)
                    self.send_data(
                        "error: Invalid Action\nLook at the server log for more information",
                        connection,
                    )
                    break
                print("exec: done")

                # report back to Unity of the operation could be executed successfully
                self.send_data("done", connection)
            else:
                self.send_data("unknown command", connection)

    def run_server(self, input_thread):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2.0)
            try:
                s.bind((self.ip_addr, self.PORT))
            except Exception as err:
                print(err)
                print(
                    "Look at the Troubleshoot section in the Readme for more information"
                )
                return

            s.listen()
            while self.t_run:
                print("Waiting for a client with IP Address " + self.ip_addr)
                while True:
                    try:
                        connection, addr = s.accept()
                        break  # TODO: comment this line in, as it crashes both programs!
                    except socket.timeout:
                        pass

                    if not input_thread.is_alive():
                        return
                # Next line crashes the program. Use it to test how the client reacts (it should not crash, but does so atm)
                print("Successfully connected! ")  #  + connection
                with connection:
                    self.receive_next_message(connection)

            # t_run = False

    @staticmethod
    def chunk_string(string, length):
        return [string[0 + i : length + i] for i in range(0, len(string), length)]

    # get the ip-address of this computer
    def get_ip(self):
        if self.useLocalhost:
            return "127.0.0.1"

        ip_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            ip_sock.connect(("10.255.255.255", 10000))
            ip = ip_sock.getsockname()[0]
        except:
            # Use localhost if the server can't connect to the internet
            ip = "127.0.0.1"
        finally:
            ip_sock.close()
        return ip

    def send_data(self, data, conn):
        # numpy arrays can't be serialized, so they have to be converted to  list
        if isinstance(data, np.ndarray):
            data = data.tolist()
        # Unitys JsonUtility can't deserialize primitive data types, so they get send directly
        bin_data = None
        if (
            type(data) == str
            or type(data) == int
            or type(data) == float
            or type(data) == bool
        ):
            my_data = str(data)
        else:
            if "positions" in data:
                bin_data = data["positions"].flatten()
                del data["positions"]
            my_data = json.dumps(data, separators=(",", ":"))
        data_lst = self.chunk_string(my_data, BLOCKSIZE)
        num_bytes = (len(my_data)).to_bytes(4, byteorder="little", signed=True)
        conn.sendall(num_bytes)
        num_str = "" + str(len(my_data)) + ";"

        for block in data_lst:
            conn.sendall(block.encode("ASCII"))

        if bin_data is not None:
            bin_data = np.float32(bin_data)
            bin_data = bin_data.tobytes()
            conn.sendall(bin_data)

        # show the first 100 characters of the send message for debug purposes
        if len(my_data) > 100:
            print("Sending: {}{}...".format(num_str, my_data[:100]))
        else:
            print("Sending: {}{}".format(num_str, my_data))
