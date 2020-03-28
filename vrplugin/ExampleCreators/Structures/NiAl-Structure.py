from pyiron_atomistics.structure.atoms import Atoms
import numpy as np
from pyiron.project import Project
import vrplugin.Sender as Sender

element = 'Fe'
pr = Project('Virtual_Atoms_Structure')
# pr.remove_jobs(recursive=True)


# cell = 32.73 * np.eye(3) # Specifying the cell dimension
cell = np.array([5.2905+1.7635, 5.2905+1.7635, 32.73])
positions = [[0.0,0.0,0.0], [1.7635,1.7635,0.0], [1.7635,0.0,2.04566], [0.0,1.7635,2.04566], [3.527,0.0,0.0], [5.2905,1.7635,0.0], [5.2905,0.0,2.04566], [3.527,1.7635,2.04566], [0.0,3.527,0.0], [1.7635,5.2905,0.0], [1.7635,3.527,2.04566], [0.0,5.2905,2.04566], [3.527,3.527,0.0], [5.2905,5.2905,0.0], [5.2905,3.527,2.04566], [3.527,5.2905,2.04566], [0.0,0.0,4.09132], [1.7635,1.7635,4.09132], [1.7635,0.0,6.13698], [0.0,1.7635,6.13698], [3.527,0.0,4.09132], [5.2905,1.7635,4.09132], [5.2905,0.0,6.13698], [3.527,1.7635,6.13698], [0.0,3.527,4.09132], [1.7635,5.2905,4.09132], [1.7635,3.527,6.13698], [0.0,5.2905,6.13698], [3.527,3.527,4.09132], [5.2905,5.2905,4.09132], [5.2905,3.527,6.13698], [3.527,5.2905,6.13698], [0.0,0.0,8.18264], [1.7635,1.7635,8.18264], [1.7635,0.0,10.2283], [0.0,1.7635,10.2283], [3.527,0.0,8.18264], [5.2905,1.7635,8.18264], [5.2905,0.0,10.2283], [3.527,1.7635,10.2283], [0.0,3.527,8.18264], [1.7635,5.2905,8.18264], [1.7635,3.527,10.2283], [0.0,5.2905,10.2283], [3.527,3.527,8.18264], [5.2905,5.2905,8.18264], [5.2905,3.527,10.2283], [3.527,5.2905,10.2283], [0.0,0.0,12.27396], [1.7635,1.7635,12.27396], [1.7635,0.0,14.31962], [0.0,1.7635,14.31962], [3.527,0.0,12.27396], [5.2905,1.7635,12.27396], [5.2905,0.0,14.31962], [3.527,1.7635,14.31962], [0.0,3.527,12.27396], [1.7635,5.2905,12.27396], [1.7635,3.527,14.31962], [0.0,5.2905,14.31962], [3.527,3.527,12.27396], [5.2905,5.2905,12.27396], [5.2905,3.527,14.31962], [3.527,5.2905,14.31962], [0.0,0.0,16.36528], [0.0,1.7635,18.41094], [1.7635,0.0,18.41094], [1.7635,1.7635,16.36528], [3.527,0.0,16.36528], [3.527,1.7635,18.41094], [5.2905,0.0,18.41094], [5.2905,1.7635,16.36528], [0.0,3.527,16.36528], [0.0,5.2905,18.41094], [1.7635,3.527,18.41094], [1.7635,5.2905,16.36528], [3.527,3.527,16.36528], [3.527,5.2905,18.41094], [5.2905,3.527,18.41094], [5.2905,5.2905,16.36528], [0.0,0.0,20.4566], [0.0,1.7635,22.50226], [1.7635,0.0,22.50226], [1.7635,1.7635,20.4566], [3.527,0.0,20.4566], [3.527,1.7635,22.50226], [5.2905,0.0,22.50226], [5.2905,1.7635,20.4566], [0.0,3.527,20.4566], [0.0,5.2905,22.50226], [1.7635,3.527,22.50226], [1.7635,5.2905,20.4566], [3.527,3.527,20.4566], [3.527,5.2905,22.50226], [5.2905,3.527,22.50226], [5.2905,5.2905,20.4566], [0.0,0.0,24.54792], [0.0,1.7635,26.59358], [1.7635,0.0,26.59358], [1.7635,1.7635,24.54792], [3.527,0.0,24.54792], [3.527,1.7635,26.59358], [5.2905,0.0,26.59358], [5.2905,1.7635,24.54792], [0.0,3.527,24.54792], [0.0,5.2905,26.59358], [1.7635,3.527,26.59358], [1.7635,5.2905,24.54792], [3.527,3.527,24.54792], [3.527,5.2905,26.59358], [5.2905,3.527,26.59358], [5.2905,5.2905,24.54792], [0.0,0.0,28.63924], [0.0,1.7635,30.6849], [1.7635,0.0,30.6849], [1.7635,1.7635,28.63924], [3.527,0.0,28.63924], [3.527,1.7635,30.6849], [5.2905,0.0,30.6849], [5.2905,1.7635,28.63924], [0.0,3.527,28.63924], [0.0,5.2905,30.6849], [1.7635,3.527,30.6849], [1.7635,5.2905,28.63924], [3.527,3.527,28.63924], [3.527,5.2905,30.6849], [5.2905,3.527,30.6849], [5.2905,5.2905,28.63924]]
positions += [[5.2905,5.2905,18.41094]]
elements = ['Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni', 'Al', 'Ni', 'Ni', 'Ni']
elements += ['H']
basis = Atoms(elements=elements, positions=positions, cell=cell, is_absolute=True, pbc=[True, True, True])
# basis.set_relative()
# basis.cell[2,2] -= 3
# basis.set_absolute()
'''
basis = pr.create_ase_bulk(element, cubic=True)
basis = basis.repeat([2, 2, 2])
basis.set_absolute()
basis.positions[3,0] += 2

[5.2905,5.2905,18.41094]
'''

ham_lammps = pr.create_job(pr.job_type.Lammps, 'ham_lammps')
ham_lammps.structure = basis
ham_lammps.potential = 'Al_H_Ni_Angelo_eam'
# ham_lammps.potential = 'LennardJones612_UniversalShifted__MO_959249795837_001'

#ham_lammps.calc_md(temperature=30, n_ionic_steps=300, n_print=1)
ham_lammps.calc_minimize()
ham_lammps.run()

# Sender.init_struc(ham_lammps, temperature=30, n_ionic_steps=300, structure_name="NiAl-Structure")
# Sender.run_loop()