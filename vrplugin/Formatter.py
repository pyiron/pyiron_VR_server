# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import traceback


class Formatter():
    formated_data = None

    def __init__(self):
        # needed so that each new created job has a unique name
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
        return Formatter.formated_data

    def get_atom_positions(self, frame=0):
        positions = self.all_positions[frame]
        # if self.editedBasisSize < len(positions):
        #     positions = positions[:int(self.editedBasisSize)]

        for atomNr in range(len(positions)):
            positions[atomNr] = (self.round_value(positions[atomNr][0]),
                                 self.round_value(positions[atomNr][1]),
                                 self.round_value(positions[atomNr][2]))

        return positions

    """
    Format the data that should be send to Unity.
    """

    def format_data(self):
        # format each frame
        Formatter.formated_data = ""
        for frame in range(len(self.all_positions)):
            self.format_first_line(frame)
            self.format_main_part(frame)
            self.format_last_line(frame)
        # remove the last '%' to show this was the last frame
        Formatter.formated_data = Formatter.formated_data[:-1]

    def format_first_line(self, frame):
        size = str(len(self.all_positions[frame]))

        if self.firstSend:
            temperature = int(float(self.temperature))
            self.firstSend = False
        else:
            temperature = "empty"

        anim_frames = len(self.all_positions) - 1

        Formatter.formated_data += "SDS {} {} {} {}%".format(size, temperature, frame, anim_frames)

    def format_main_part(self, frame=0):
        positions = self.get_atom_positions(frame)

        # elements = self.pr.get_structure(self.frame).get_chemical_symbols()
        # elements = self.editedBasis.get_chemical_symbols()

        for atomNr in range(len(positions)):
            position = positions[atomNr]
            Formatter.formated_data += "SDM {} {} {} {}%".format(position[0], position[1], position[2],
                                                                         self.all_elements[atomNr])

    def format_last_line(self, frame):
        Formatter.formated_data += "SDE "
        cell = self.all_cells[frame]
        for ci in cell.flatten():
            Formatter.formated_data += "{0:.4g} ".format(ci)
        # remove the last ' ' and append a '%'
            Formatter.formated_data = Formatter.formated_data[:-1] + "%"

    def round_value(self, position):
        return "{0:.4g}".format(position)




"""self.set_new_base_position('x y z atomNr, frame') - set x, y and z koordinate for the atom with id atomNr in the
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
