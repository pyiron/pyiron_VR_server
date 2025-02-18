#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from UnityManager import UnityManager
from Executor import Executor
import Formatter
from Structure import Structure


class Manager:
    def __init__(self, port=None):
        from EchoServer import EchoServer
        unityManager = UnityManager()
        executor = Executor()
        structure = Structure()
        if structure.structure is None:
            return
        echoServer = EchoServer(port)

        echoServer.run_server(unityManager, executor, structure)


try:
    port = int(input("Port for the server:"))
except:
    port = None

manager = Manager(port)
