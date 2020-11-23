# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import traceback
import UnityManager
from Structure import Structure
import Formatter
import numpy as np


class Executor():
    job = None

    def __init__(self):
        # needed so that each new created job has a unique name. TODO: might be outdated
        self.job_id = 0

        # the current frame. Should be send before an order gets executed
        self.frame = 0
        self.sendForce = False
        self.sendTemperature = False

        # init the data of the structure
        self.all_positions = None
        self.all_cells = None
        self.all_temperatures = None
        self.all_elements = None

    def create_default_job(self, name):
        # Initialize the new job as a Lammps with the name of the structure
        # TODO: initialize it with the name of the structure (e.g. Fe2_md_shifted)
        if name == "":
            name = Structure.structure.get_chemical_formula()
        Executor.job = UnityManager.UnityManager.project.create_job(UnityManager.UnityManager.project.job_type.Lammps,
                                                       name)
        Executor.job.structure = Structure.structure
        if len(Executor.job.list_potentials()) > 0:
            Executor.job.potential = Executor.job.list_potentials()[0]

    def initialize_job(self):
        # signals whether this is the first time Python sends data to Unity or if it isn't
        self.firstSend = True
        # set all_forces to None because it is not yet known
        self.all_forces = None

        # set the temperature to a default value, might be overwritten if the job has a temperature
        self.temperature = 100
        # test if the structure has a given temperature
        if Executor.job.input.control["fix"]:
            if len(Executor.job.input.control["fix"].split()) > 4:
                # get the temperature with which the ham_lammps was initiated
                self.temperature = Executor.job.input.control["fix"].split()[4]

    def load_job(self, job, jobName=""):
        if job is None:
            # create a new job
            self.create_default_job(jobName)
            self.initialize_job()
        else:
            Executor.job = job
            Structure.structure = job.structure
            self.initialize_job()
            return self.format_job()

        # get the data about the structure, such as the positions and the forces
        # self.get_structure_data(True, True, True)
        # return self.formated_data

    def reset_job(self, name):

        UnityManager.UnityManager.project.remove_job(name)
        self.create_default_job(name)


    """
    Receive and handle input from Unity.
    """

    # def on_input(self, type, val, is_test=False):
    #     if type not in ("exec", "eval"):
    #         return "print Unknown type " + type
    #     self.frame = int(val.split()[0])
    #     val = val[len(str(self.frame)) + 1:]
    #     # execute the new order
    #     if type == "eval":
    #         val = eval(val)
    #     else:
    #         exec(val)
    #         val = None
    #     return val

    # # called from Unity
    # def send_all_forces(self):
    #     if self.all_forces is not None:
    #         forces = ""
    #         for atom_id in range(len(self.all_forces[self.frame])):
    #             new_forces = ""
    #             for i in range(3):
    #                 new_forces += " " + str(self.round_value(self.all_forces[self.frame][atom_id][i]))
    #             forces += "force{} {}%".format(new_forces, str(atom_id))
    #         forces = forces[:-1]
    #         res = forces
    #     else:
    #         res = "force empty"
    #     return res

    # # called from Unity
    # def set_temperature(self, tmp):
    #     self.temperature = tmp

    # called from Unity, currently not used
    def set_new_base_position(self, data):
        # data = "x y z atom_id"
        # set the atom with id atom_id to the defined new positions
        for i in range(3):
            Executor.job.structure.positions[int(data.split()[3]), i] = float(data.split()[i])

    # called from Unity, currently not used
    def destroy_atom(self, atom_id):
        # destroy an atom out of the basis. When creating the new lammps, the basis will be transmitted
        del Executor.job.structure[atom_id]
        self.get_structure_data(forces=True, shouldFormat=False)

    def prepare_structure(self, job_name, job_type, potential, frame=-1): # TODO: might be outdated


        # temp_base = Executor.job.get_structure(frame)

        # if job_type == "ham_lammps":
        #     job_type = self.job.job_type.Lammps
        # else:
        #     job_type = self.job.job_type.Vasp
        # self.job = self.job.create_job(job_type, job_name)
        # self.job.structure = temp_base
        # self.job.potential = potential


        # TODO: use job_name instead. Can be done when Unity deletes the old job before creating the new ones
        # argument snapshot seems to be the frame that should be used to calculate the new lammps
        # Executor.job = self.job.next(job_name="temp_job_" + str(self.job_id))
        # Executor.job.structure = temp_base
        self.job_id += 1

    def run_job(self, is_minimize):
        try:
            Executor.job.run()
        except Exception as e:
            print(e)
            traceback.print_exc()
            return "Error: Check that all atoms have enough distance to each other. Mind periodic boundaries!"

        if is_minimize:
            Executor.job.structure.center_coordinates_in_unit_cell()

        return self.format_job()
        # return self.get_structure_data(True, forces=True)

    # called from Unity
    def calculate_md(self, temperature, n_ionic_steps, n_print, job_type, job_name, potential):
        self.prepare_structure(job_name, job_type, potential)
        Executor.job.calc_md(temperature=temperature, n_ionic_steps=n_ionic_steps, n_print=n_print)
        return self.run_job(False)

    # called from Unity
    def calculate_minimize(self, force_conv, max_iterations, n_print, job_type, job_name, potential):
        self.prepare_structure(job_name, job_type, potential)
        # f_tol might be the wrong attribute
        Executor.job.calc_minimize(f_tol=force_conv, max_iter=max_iterations, n_print=n_print)
        return self.run_job(False)

    # # called from Unity, outdated
    # def create_new_lammps(self, calculation, temperature=10, n_ionic_steps=100, n_print=1):
    #     self.prepare_structure("")
    #
    #     if calculation == "md":
    #         Executor.job.calc_md(temperature=temperature, n_ionic_steps=n_ionic_steps, n_print=n_print)
    #     else:
    #         Executor.job.calc_minimize(n_print=n_print)
    #
    #     try:
    #         Executor.job.run()
    #     except Exception as e:
    #         print(e)
    #         traceback.print_exc()
    #         return "Error: Check that all atoms have enough distance to each other. Mind periodic boundaries!"
    #
    #     if calculation == "minimize":
    #         Executor.job.structure.center_coordinates_in_unit_cell()
    #
    #     # if eval("self.run_" + calculation + "(" + n_ionic_steps)") == -1:
    #     #     return "error: Check that all atoms have enough distance to each other. Mind periodic boundaries!"
    #     # self.all_positions = self.job['output/generic/positions']
    #     return self.get_structure_data(True, forces=True)

    # def run_md(self): # outdated
    #     self.pr.calc_md(temperature=self.temperature, n_print=1, n_ionic_steps=self.n_ionic_steps)
    #     # self.job.server.run_mode.non_modal=True
    #     try:
    #         self.pr.run()
    #     except Exception as e:
    #         print(e)
    #         traceback.print_exc()
    #         return -1
    #     return 0
    #     # self.job.project.wait_for_job(self.job)
    #
    # def run_minimize(self): # outdated
    #     self.pr.calc_minimize(n_print=1)
    #     try:
    #         self.pr.run()
    #     except Exception as e:
    #         print(e)
    #         traceback.print_exc()
    #         return -1
    #     self.pr.structure.center_coordinates_in_unit_cell()
    #     return 0

    # called from Unity, currently not in use
    def add_new_atom(self, element):
        # todo: find a good position for the new atom
        Executor.job.structure += Executor.job.project.create_atoms([element], [(2, 0, 0)])
        # self.pr.structure.set_absolute()
        return self.get_structure_data()

    # called from Unity, outdated
    # TODO: frame is not needed anymore and should be removed, but therefore it has to be removed on the Unity side too
    # def create_new_struc(self, frame, elm, cubic):
    #     # self.frame = frame
    #     # TODO: show possible Arguments of create_ase_bulk in Unity and use the input
    #     bulk = Executor.job.project.create_ase_bulk(name=elm, cubic=cubic)
    #     bulk.positions[0, 0] += 2
    #     bulk.positions[1, 0] += 4
    #     # self.pr.structure = self.pr.get_structure(self.frame)
    #     Executor.job.structure += bulk
    #     # self.pr.structure.set_absolute()
    #     return self.get_structure_data(forces=True)

    # not fully implemented, might not be implemented at all
    def send_args_create_ase_bulk(self):
        # (todo: this argument is optional -> add default)
        args = self.format_args("crystalstructure", "str", "auto sc fcc bcc hcp diamond zincblende rocksalt"
                                                           " cesiumchloride fluorite wurtzite")
        args = self.format_args("a", "float", options="None")
        args += self.format_args("c", "float", options="None", desc="Lattice constant")
        args += self.format_args("c", "float", options="None", desc="Lattice constant")
        args += self.format_args("c_over_a", "float", options="None", desc="c/a ratio used for hcp. "
                                                                           "Default is ideal ratio: sqrt(8/3).")
        args += self.format_args("u", "float", "None", desc="Internal coordinate for Wurtzite structure.")
        args += self.format_args("orthorhombic", "bool", "Construct orthorhombic unit cell instead of primitive cell "
                                                         "which is the default.")
        args += self.format_args("cubic", "bool", options="False")
        return args[:-1] + " end"

    def format_args(self, name, type, options="empty", desc="empty"):
        return "arg name {} type {} options {} desc {}%".format(name, type, options, desc)

    """
    Get data of the structure
    """

    # get all important data of the current structure
    # Warning: might need 1/10s, so this method should not be called each frame
    def get_structure_data(self, all_frames=False, temperature=False, forces=False, shouldFormat=True):
        # might throw an error when self.pr is a base
        self.all_elements = Executor.job.get_structure(0).get_chemical_symbols()
        if all_frames:
            if Executor.job['output']:
                self.all_positions = Executor.job.output.positions
                self.all_cells = Executor.job.output.cells
                if temperature:
                    self.all_temperatures = Executor.job.output.temperature
                if forces:
                    self.all_forces = Executor.job.output.forces
            else:
                print("print Warning in Executor line 145")
                self.all_positions = [Executor.job.structure.positions]
                self.all_cells = [Executor.job.structure.cell]
        else:
            self.all_positions = [Executor.job.structure.positions]
            self.all_cells = [Executor.job.structure.cell]

        if shouldFormat:
            self.format_data()
        return self.formated_data

    def get_atom_positions(self, frame=0):
        positions = self.all_positions[frame]
        # if self.editedBasisSize < len(positions):
        #     positions = positions[:int(self.editedBasisSize)]

        for atomNr in range(len(positions)):
            positions[atomNr] = (self.round_value(positions[atomNr][0]),
                                 self.round_value(positions[atomNr][1]),
                                 self.round_value(positions[atomNr][2]))

        return positions

    def get_generic_inp(self):
        j_dic = Executor.job['input/generic/data_dict']
        if j_dic is None:
            return None
        return {k:v for k, v in zip(j_dic['Parameter'], j_dic['Value'])}

    """
    Format the data that should be send to Unity.
    """

    def set_attribute(self, data, name, default):
        generic_par = self.get_generic_inp()
        if generic_par is None or name not in generic_par:
            data[name] = default
        else:
            data[name] = generic_par[name]

    def format_general_settings(self, data):
        self.set_attribute(data, "calc_mode", "md")

        # generic_par = self.get_generic_inp()
        # if generic_par is None:
        #     # set default value
        #     data["calculation_type"] = "md"
        # else:
        #     data["calculation_type"] = self.get_generic_inp()["calc_mode"]
        if Executor.job["TYPE"] is None:
            data["job_type"] = "lammps"
        else:
            data["job_type"] = Executor.job["TYPE"].split("'")[1].split(".")[-1]
        # data["job_name"] = Structure.structure.get_chemical_formula()
        data["currentPotential"] = Executor.job.potential['Name'].values[0]
        data["potentials"] = list(Executor.job.list_potentials())
        return data

    def format_job(self):
        data = {"elements": list(Structure.structure.get_chemical_symbols()),
                "size": len(Structure.structure.positions)}

        positions = Executor.job["output/generic/positions"]
        if positions is None:
            data["frames"] = 1
            data["positions"] = Formatter.array_to_vec3(Structure.structure.positions)
        else:
            data["frames"] = len(positions)
            data["positions"] = Formatter.array_to_vec3(np.reshape(positions, (-1, 3)))
        # formated_data["positions"] = Formatter.array_to_vec3(positions[0])
        data["cell"] = Formatter.array_to_vec3(Structure.structure.cell)
        return data

    def format_md_settings(self, data):
        self.set_attribute(data, "temperature", 100)
        self.set_attribute(data, "n_ionic_steps", 1000)
        self.set_attribute(data, "n_print", 1)
        return data

    def format_minimize_settings(self, data):
        self.set_attribute(data, "f_eps", 1e-8)
        self.set_attribute(data, "max_iterations", 100000)
        self.set_attribute(data, "n_print", 100)
        return data

    def format_job_settings(self):
        formated_data = {}
        formated_data = self.format_general_settings(formated_data)
        formated_data = self.format_md_settings(formated_data)
        formated_data = self.format_minimize_settings(formated_data)
        return Formatter.dict_to_json(formated_data)

    def format_data(self): #outdated
        # if self.temporaryBasis:  # not sure if this is needed
        #     self.frame = 0

        # format each frame
        self.formated_data = ""
        for frame in range(len(self.all_positions)):
            self.format_first_line(frame)
            self.format_main_part(frame)
            self.format_last_line(frame)
        # remove the last '%' to show this was the last frame
        self.formated_data = self.formated_data[:-1]

    def format_first_line(self, frame): #outdated
        size = str(len(self.all_positions[frame]))

        if self.firstSend:
            temperature = int(float(self.temperature))
            self.firstSend = False
        else:
            temperature = "empty"

        anim_frames = len(self.all_positions) - 1

        self.formated_data += "SDS {} {} {} {}%".format(size, temperature, frame, anim_frames)

    def format_main_part(self, frame=0): #outdated
        positions = self.get_atom_positions(frame)

        # elements = self.pr.get_structure(self.frame).get_chemical_symbols()
        # elements = self.editedBasis.get_chemical_symbols()

        for atomNr in range(len(positions)):
            position = positions[atomNr]
            self.formated_data += "SDM {} {} {} {}%".format(position[0], position[1], position[2],
                                                                         self.all_elements[atomNr])

    def format_last_line(self, frame): #outdated
        self.formated_data += "SDE "
        cell = self.all_cells[frame]
        for ci in cell.flatten():
            self.formated_data += "{0:.4g} ".format(ci)
        # remove the last ' ' and append a '%'
        self.formated_data = self.formated_data[:-1] + "%"

    def round_value(self, position):
        return "{0:.4g}".format(position)


""" mainly outdated:
self.set_new_base_position('x y z atomNr, frame') - set x, y and z koordinate for the atom with id atomNr in the
    given frame" 
self.calculate('md || minimize', frame) - calculate ham_lammps for the given structure in the given frame.
    Write md or minimze to choose which calculation should be done" 
self.temperature = t - Set the current temperature to value t
self.destroy_atom(atom_id, frame) - destroy the atom with the given atom_id and reload the lammps with the data from
    the current frame
stop - Stops this script." """

# TODO: list_potentials()[0]
# nbrs = get_neighbours
# nbrs.distances[atom_id]
