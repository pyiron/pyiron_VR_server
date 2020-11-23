# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import os
import sys
from pyiron.project import Project

# get the path to this script C:\Users\<usr>\...\vrplugin\pyiron_mpie\vrplugin\pyiron_mpie\vrplugin
# remove \pyiron_mpie\vrplugin
cwd = os.getcwd().replace("\\", "/").split("/")
# Add the path to PYTHONPATH. This way the other scripts (e.g. Executor) can be called
sys.path.append(os.getcwd()[:- len(cwd[-1]) - len(cwd[-2]) - 2])
from Executor import Executor
# TODO: the block above might be outdated


class UnityManager:
    project = None

    def __init__(self, start_path=os.path.join('.', 'Structures')):
        UnityManager.project = Project(start_path)

