# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from pyiron_vrplugin.Formatter import array_to_vec3, dict_to_json
from pyiron_atomistics import Project


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
            Structure.structure = Project('.').create.structure.ase.bulk(
                element, cubic=cubic, orthorhombic=orthorhombic).repeat([repeat, repeat, repeat])
        except RuntimeError as e:
            return "Error: " + str(e)
        except ValueError as e:
            return "Error: " + str(e)
        return self.format_structure()

    @staticmethod
    def format_structure():
        formatted_data = {"elements": list(Structure.structure.get_chemical_symbols()),
                          "size": len(Structure.structure.positions), "frames": 1,
                          "formula": Structure.structure.get_chemical_formula(),
                          "cell": array_to_vec3(Structure.structure.cell),
                          "positions": array_to_vec3(Structure.structure.positions)}
        return dict_to_json(formatted_data)

