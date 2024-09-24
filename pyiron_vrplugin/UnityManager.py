# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import os
import sys
from pyiron_atomistics import Project


class UnityManager:
    project = None

    def __init__(self, start_path=os.path.join('.', 'Structures')):
        UnityManager.project = Project(start_path)

    def GetJobSizes(self):
        sizes = []
        for name in UnityManager.project.list_all()['nodes']:
            positions = UnityManager.project[name + "/output/generic/positions"]
            if positions is None:
                total_n_atoms = 0
            else:
                total_n_atoms = len(positions)
                #  ToDo: Assumes uniform trajectory! Might be ok for 'just' job sizes
                if total_n_atoms > 0:
                    total_n_atoms *= len(positions[0])
            sizes.append(total_n_atoms)
        return {"jobSizes": sizes}
