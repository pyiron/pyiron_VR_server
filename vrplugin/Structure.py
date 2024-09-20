# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import UnityManager
import Executor
import Formatter
from pyiron.project import Project
import json
import numpy


class Structure:
    structure = None

    def __init__(self):
        self.create_default_structure()

    def get_data(self):
        return self.format_structure()

    def create_default_structure(self):
        res = self.create("Fe", 1, True, False)
        if res.startswith("Error: "):
            print(res)

    def create(self, element, repeat, cubic, orthorhombic):
        try:
            Structure.structure = UnityManager.UnityManager.project.create.structure.ase.bulk(
                element, cubic=cubic, orthorhombic=orthorhombic).repeat([repeat, repeat, repeat])
        except RuntimeError as e:
            return "Error: " + str(e)
        except ValueError as e:
            return "Error: " + str(e)
        return self.format_structure()

    def format_structure(self):
        print("Formatting structure...")
        formated_data = {"elements": list(Structure.structure.get_chemical_symbols()),
                         "size": len(Structure.structure.positions), "frames": 1,
                         "formula": Structure.structure.get_chemical_formula(),
                         "cell": Formatter.array_to_vec3(Structure.structure.cell),
                         "positions": Formatter.array_to_vec3(Structure.structure.positions)}
        return Formatter.dict_to_json(formated_data)


    #
    # if no structure loaded: create default struc and send to Unity
    # if structure is loaded: return the structure

# UnityManager.UnityManager()
# myStruc = Structure()
# myStruc.create_default_structure()
# # print(myStruc.structure.cubic)
# # print(myStruc.structure.orthorhombic)
# # print(myStruc.get_data())
# # myStruc.structure.name = "Mg"
# # myStruc.structure = myStruc.structure.repeat([2 , 2, 2])
# # myStruc.structure.cubic = True
# # myStruc.structure.orthorhombic = True
# # print(myStruc.get_data())
# print(myStruc.format())
