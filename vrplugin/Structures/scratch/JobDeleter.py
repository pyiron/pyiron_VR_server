# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from pyiron.project import Project

"""
Create a simple job, which gets saved in the save folder. If there is no save folder, it will create it.
"""

pr = Project()

# go to the save folder
element = 'Fe'
pr = Project('Structures')
pr.create_group("Examples")
pr = pr["Examples"]
pr.remove_jobs()

strucs = ["small", "medium", "big", "minimize", "md"]
for i in range(len(strucs)):
    # create the new job
    basis = pr.create_ase_bulk(element, cubic=True)
    basis = basis.repeat([(i % 3 + 1) , 1, 1])
    basis.set_absolute()
    basis.positions[1, 0] += 2

    ham_lammps = pr.create_job(pr.job_type.Lammps, 'ham_lammps_' + strucs[i])
    ham_lammps.structure = basis
    ham_lammps.potential = 'Fe_C_Becquart_eam'

    if strucs[i] == "minimize":
        ham_lammps.calc_minimize(n_print=1)
        ham_lammps.run()
    if strucs[i] == "md":
        ham_lammps.calc_md(temperature=30, n_ionic_steps=50, n_print=1)
        ham_lammps.run()
