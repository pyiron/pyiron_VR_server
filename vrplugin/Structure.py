import UnityManager
import Executor
import Formatter
from pyiron.project import Project
import json
import numpy


class Structure():
    structure = None

    def __init__(self):
        self.create_default_structure()

    def get_data(self):
        return self.format_structure()

    def create_default_structure(self):
        self.create("Fe", 1, True, False)

    def create(self, element, repeat, cubic, orthorhombic):
        try:
            Structure.structure = UnityManager.UnityManager.project.create_ase_bulk(
                element, cubic=cubic, orthorhombic=orthorhombic).repeat([repeat, repeat, repeat])
        except RuntimeError as e:
            return "Error: " + str(e)
        except ValueError as e:
            return "Error: " + str(e)
        return self.format_structure()

    def format_structure(self):
        formated_data = {}
        formated_data["elements"] = list(Structure.structure.get_chemical_symbols())
        formated_data["size"] = len(Structure.structure.positions)
        formated_data["frames"] = 1
        formated_data["formula"] = Structure.structure.get_chemical_formula()
        formated_data["positions"] = Formatter.array_to_vec3(Structure.structure.positions)
        formated_data["cell"] = Formatter.array_to_vec3(Structure.structure.cell)
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
