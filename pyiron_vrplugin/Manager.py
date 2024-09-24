#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from UnityManager import UnityManager
from pyiron_vrplugin.Executor import Executor
from pyiron_vrplugin.Structure import Structure
from pyiron_vrplugin.EchoServer import EchoServer, KeyboardThread


class Manager:
    def __init__(self, input_thread):
        unityManager = UnityManager()
        executor = Executor()
        structure = Structure()
        if structure.structure is None:
            return
        echoServer = EchoServer()

        echoServer.run_server(input_thread)


input_thread = KeyboardThread()
manager = Manager(input_thread)
