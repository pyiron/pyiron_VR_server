import UnityManager
import Executor
from pyiron.project import Project


class Structure():
    structure = None

    def __init__(self):
        pass

    def get_data(self):
        if self.structure is None:
            self.create_default_structure()
        return str(self.structure)

    # def load_structure(self):
    #     job = Executor.Executor.job
    #     if job is None:
    #         # Default parameters can be set here
    #
    #     else:
    #         self.structure = job.get_str

    def create_default_structure(self):
        self.create("Fe", 2, True, False)

    def create(self, element, repeat, cubic, orthorhombic):
        try:
            self.structure = UnityManager.UnityManager.project.create_ase_bulk(
                element, cubic=cubic, orthorhombic=orthorhombic).repeat([repeat, repeat, repeat])
        except RuntimeError as e:
            return "Error: " + str(e)
        return str(self.structure)
        # self.structure.

    #
    # if no structure loaded: create default struc and send to Unity
    # if structure is loaded: return the structure

# UnityManager.UnityManager()
# myStruc = Structure()
# myStruc.create_default_structure()
# # print(myStruc.structure.cubic)
# # print(myStruc.structure.orthorhombic)
# print(myStruc.get_data())
# myStruc.structure.name = "Mg"
# myStruc.structure = myStruc.structure.repeat([2 , 2, 2])
# myStruc.structure.cubic = True
# myStruc.structure.orthorhombic = True
# print(myStruc.get_data())
