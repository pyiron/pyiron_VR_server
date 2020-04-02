import UnityManager
import Executor

# myStruc = Structure()
# print(myStruc.get_data())

class Structure():
    structure = None
    def __init__(self):
        pass

    def get_data(self):
        return self.structure

    def load_structure(self):
        job = Executor.Executor.job
        if job is None:
            # Default parameters can be set here
            self.create_new_structure("Fe", True, False)
        else:
            self.structure = job.get_str

    def create_new_structure(self, element, cubic, orthorhombic):
        self.structure = UnityManager.UnityManager.project.create_ase_bulk(element=element, cubic=True, orthorhombic=orthorhombic)
        # self.structure.

    #
    # if no structure loaded: create default struc and send to Unity
    # if structure is loaded: return the structure