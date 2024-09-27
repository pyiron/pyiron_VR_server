#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from UnityManager import UnityManager
from pyiron_vrplugin.Executor import Executor
from pyiron_vrplugin.Structure import Structure
from pyiron_vrplugin.EchoServer import EchoServer, KeyboardThread


class Manager:
    def __init__(self):

        unityManager = UnityManager()
        executor = Executor()
        structure = Structure()
        if structure.structure is None:
            return
        echoServer = EchoServer(unityManager, structure, executor)

        input_thread = KeyboardThread()
        echoServer.run_server(input_thread)


if __name__ == '__main__':
    Manager()
