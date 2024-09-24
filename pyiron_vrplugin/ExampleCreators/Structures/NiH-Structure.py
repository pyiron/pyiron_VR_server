from pyiron.project import Project
import vrplugin.Sender as Sender


pr = Project('VR_tests')
# pr.remove_jobs(recursive=True)

# basis_Ni = pr.create_structure(element="Ni", bravais_basis='fcc', lattice_constant=3.52)
#
# ham_vasp = pr.create_job(pr.job_type.Vasp, 'cell_Ni_dft')
# ham_vasp.structure = basis_Ni
# ham_vasp.set_encut(400)
# ham_vasp.input.incar['LWAVE'] = True
# ham_vasp.calc_minimize(max_iter=10000, pressure=0)
# ham_vasp.run()
#
# ham_lammps = pr.create_job(pr.job_type.Lammps, 'cell_Ni_md')
# ham_lammps.structure = basis_Ni
# ham_lammps.potential = 'Ni_Al_H_eam.lmp'
# ham_lammps.calc_minimize(max_iter=10000, pressure=0)
# ham_lammps.run()

lattice = 3.52
basis_Ni = pr.create_structure(element="Ni", bravais_basis='fcc', lattice_constant=lattice)
basis_Ni_large = basis_Ni.repeat([3, 3, 8])

basis_H = pr.create_structure(element="H", bravais_basis='fcc', lattice_constant=lattice)
basis_H.positions += [1./2., 0, 0]
basis_H.set_repeat([3, 3, 8])

basis_full = basis_Ni_large + basis_H[[1, 2, 45, 90]]
basis_full.set_absolute()
basis_full.cell[0, 0] += 20
basis_full.cell[1, 1] += 20

ham = pr.create_job(pr.job_type.Lammps, 'deform_Ni_H')
ham.potential = 'Al_H_Ni_Angelo_eam'
ham.structure = basis_full
ham.calc_md(temperature=30, n_ionic_steps=3000, n_print=10)
ham.run()
# try:
#     ham.input.control['fix 2'] = "all deform 1 z trate -0.01"
# except:
#     pass
# ham.run()

# Sender.init_struc(ham, temperature=30, n_ionic_steps=300, structure_name="NiH-Structure")
# Sender.init_struc(ham)
# Sender.run_loop()
