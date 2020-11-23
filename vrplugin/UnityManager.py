# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.
import os
import sys
import time
import traceback
from pyiron.project import Project

# get the path to this script C:\Users\<usr>\...\vrplugin\pyiron_mpie\vrplugin\pyiron_mpie\vrplugin
# remove \pyiron_mpie\vrplugin
cwd = os.getcwd().replace("\\", "/").split("/")
# Add the path to PYTHONPATH. This way the other scripts (e.g. Executor) can be called
sys.path.append(os.getcwd()[:- len(cwd[-1]) - len(cwd[-2]) - 2])
from Executor import Executor


class UnityManager:
    project = None

    def __init__(self, start_path=os.path.join('.', 'Structures')):
        # self.ProjectExplorer = ProjectExplorer(self)
        # print("abspath: " + os.path.abspath('.'))
        self.startPath = start_path  # os.path.join('.', 'Structures')
        UnityManager.project = Project(self.startPath)

        self.Executor = None
        self.empty = "empty"
        self.is_test = False
        self.test_output = ""

    # not used when using the server
    def start(self):
        while True:
            # wait for input from Unity. This is the idle state. When received handle it.
            out = self.on_input(input())

            # send data to Unity
            if out is not None:
                print(out + "\nOrder executed")
            else:
                print("Order executed")

    """
    Receive data from Unity
    """

    # def on_input(self, complete_order): outdated
    #     try:
    #         if complete_order == "stop":
    #             self.delete_scratch()
    #             sys.exit()
    #         elif complete_order == "return":
    #             self.delete_scratch()
    #             return None
    #
    #         if len(complete_order.split()) < 3:
    #             return "print At least 3 Arguments are needed"
    #
    #         receiver = complete_order.split()[0]
    #         of_type = complete_order.split()[1]
    #         order = complete_order[len(receiver) + len(of_type) + 2:]
    #
    #         res = ""
    #         if receiver == 'Executor':
    #             res = self.Executor.on_input(of_type, order)
    #         elif receiver == "None":
    #             if of_type == 'exec':
    #                 exec(order)
    #             elif of_type == 'eval':
    #                 res = eval(order)
    #                 return res
    #             else:
    #                 res = "print Unknown type " + of_type
    #         else:
    #             res = "print Unknown script to send message to"
    #     except Exception as e:
    #         print(e)
    #         traceback.print_exc()
    #         return "error: Unknown error. Look at the output log of the server for more information."
    #     return res

    # def delete_scratch(self): outdated
    #     if self.Executor is not None:
    #         # pr = self.Executor.pr.project
    #         if "save" not in UnityManager.project.path:
    #             UnityManager.project.remove_jobs(True)
    #             UnityManager.project = UnityManager.project[".."]
    #             UnityManager.project.removedirs("scratch")

    """
    Called from the Unity program. Creates a new Folder in which the structure gets edited, loads the structure and 
    returns the data of the structure.
    """

    # def send_job(self):
    #     # self.create_folder_with_job(self.project, "scratch")
    #     # self.Executor = Executor(self, self.project)
    #
    #     return self.Executor.formated_data

    """
    Create the scratch folder which is the workspace and which will be deleted when the program gets stopped.
    """

    def create_folder_with_job(self, job, name):
        pr = Project(self.startPath)
        pr.create_group(name)
        pr = pr[name]
        pr.remove_jobs(True)

        # todo: has a long loading time (~5s)
        # TODO: if name already exists, this throws an error. Fixed by try catch, but another solution would be better
        # self.project = job.copy_to(pr)


# if __name__ == '__main__': outdated
#     UnityManager().start()

# ProjectExplorer pr_input save
# ProjectExplorer pr_input ham_lammps
# Executor exec 0 self.set_new_base_position('1.435 4.305 4.305 11')
# Executor exec 0 self.create_new_lammps('md')
# Executor exec 0 self.create_new_lammps('minimize')
