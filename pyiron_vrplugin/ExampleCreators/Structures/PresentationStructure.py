import vrplugin.Sender as Sender
from pyiron.project import Project

element = 'Fe'
pr = Project('Virtual_Atoms_Structure')
# pr.remove_jobs(recursive=True)

basis = pr.create_ase_bulk(element, cubic=True)
basis = basis.repeat([2, 2, 2])
basis.set_absolute()
basis.positions[3,0] += 2

ham_lammps = pr.create_job(pr.job_type.Lammps, 'ham_lammps')
ham_lammps.structure = basis
ham_lammps.potential = 'Fe_C_Becquart_eam'

"""
i = 1
ham_new = ham_lammps.next(job_name='restart_{}'.format(i))
ham_new.structure.positions[3,0] += 2
ham_new.run()
"""
ham_lammps.calc_md(temperature=30, n_ionic_steps=300, n_print=1)
ham_lammps.run()

# Sender.init_struc(ham_lammps, temperature=1000, n_ionic_steps=300, structure_name="Fe-Structure")
# Sender.run_loop()
