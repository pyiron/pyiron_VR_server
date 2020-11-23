# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import traceback
import UnityManager
from Structure import Structure
import Formatter
import numpy as np


class Executor:
    job = None

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

    def load_job(self, job, jobName=""):
        if job is None:
            # create a new job
            self.create_default_job(jobName)
            # self.initialize_job() outdated
        else:
            Executor.job = job
            Structure.structure = job.structure
            # self.initialize_job() outdated
            return self.format_job()

    def reset_job(self, name):

        UnityManager.UnityManager.project.remove_job(name)
        self.create_default_job(name)

    """
    Receive and handle input from Unity.
    """

    # called from Unity, currently not used
    def set_new_base_position(self, data):
        # data = "x y z atom_id"
        # set the atom with id atom_id to the defined new positions
        for i in range(3):
            Executor.job.structure.positions[int(data.split()[3]), i] = float(data.split()[i])

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

    # called from Unity
    def calculate_md(self, temperature, n_ionic_steps, n_print, job_type, job_name, potential):
        # self.prepare_structure(job_name, job_type, potential) outdated
        Executor.job.calc_md(temperature=temperature, n_ionic_steps=n_ionic_steps, n_print=n_print)
        return self.run_job(False)

    # called from Unity
    def calculate_minimize(self, force_conv, max_iterations, n_print, job_type, job_name, potential):
        # self.prepare_structure(job_name, job_type, potential) outdated
        # f_tol might be the wrong attribute
        Executor.job.calc_minimize(f_tol=force_conv, max_iter=max_iterations, n_print=n_print)
        return self.run_job(False)

    # # called from Unity, currently not in use, last line is outdated
    # def add_new_atom(self, element):
    #     # todo: find a good position for the new atom
    #     Executor.job.structure += Executor.job.project.create_atoms([element], [(2, 0, 0)])
    #     # self.pr.structure.set_absolute()
    #     return self.get_structure_data()

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
    Format the data that should be send to Unity.
    """

    def get_generic_inp(self):
        j_dic = Executor.job['input/generic/data_dict']
        if j_dic is None:
            return None
        return {k:v for k, v in zip(j_dic['Parameter'], j_dic['Value'])}

    def set_attribute(self, data, name, default, generic_inp):
        if generic_inp is None or name not in generic_inp:
            data[name] = default
        else:
            data[name] = generic_inp[name]

    def format_general_settings(self, data, generic_inp):
        self.set_attribute(data, "calc_mode", "md", generic_inp)

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

    def format_md_settings(self, data, generic_inp):
        self.set_attribute(data, "temperature", 100, generic_inp)
        self.set_attribute(data, "n_ionic_steps", 1000, generic_inp)
        self.set_attribute(data, "n_print", 1, generic_inp)
        return data

    def format_minimize_settings(self, data, generic_inp):
        self.set_attribute(data, "f_eps", 1e-8, generic_inp)
        self.set_attribute(data, "max_iterations", 100000, generic_inp)
        self.set_attribute(data, "n_print", 100, generic_inp)
        return data

    def format_job_settings(self):
        generic_inp = self.get_generic_inp()
        formated_data = {}
        formated_data = self.format_general_settings(formated_data, generic_inp)
        formated_data = self.format_md_settings(formated_data, generic_inp)
        formated_data = self.format_minimize_settings(formated_data, generic_inp)
        return Formatter.dict_to_json(formated_data)




# TODO: list_potentials()[0]
# nbrs = get_neighbours
# nbrs.distances[atom_id]
