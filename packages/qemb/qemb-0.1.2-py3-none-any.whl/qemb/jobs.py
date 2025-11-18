import os
import shutil
from .cut_cluster import *
from .tackle_poscar import *
from .write_inputs import write_rest_input

def count_mult(atoms):
    #define a dict, key is the atom symbol, value is the electron of the atom
    atom_dict = {
        "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
        "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18, "K": 19, "Ca": 20,
        "Sc": 21, "Ti": 22, "V": 23, "Cr": 24, "Mn": 25, "Fe": 26, "Co": 27, "Ni": 28, "Cu": 29, "Zn": 30,
        "Ga": 31, "Ge": 32, "As": 33, "Se": 34, "Br": 35, "Kr": 36, "Rb": 37, "Sr": 38, "Y": 39, "Zr": 40,
        "Nb": 41, "Mo": 42, "Tc": 43, "Ru": 44, "Rh": 45, "Pd": 46, "Ag": 47, "Cd": 48, "In": 49, "Sn": 50,
        "Sb": 51, "Te": 52, "I": 53, "Xe": 54, "Cs": 55, "Ba": 56, "La": 57, "Ce": 58, "Pr": 59, "Nd": 60,
        "Pm": 61, "Sm": 62, "Eu": 63, "Gd": 64, "Tb": 65, "Dy": 66, "Ho": 67, "Er": 68, "Tm": 69, "Yb": 70,
        "Lu": 71, "Hf": 72, "Ta": 73, "W": 74, "Re": 75, "Os": 76, "Ir": 77, "Pt": 78, "Au": 79, "Hg": 80,
        "Tl": 81, "Pb": 82, "Bi": 83, "Po": 84, "At": 85, "Rn": 86, "Fr": 87, "Ra": 88, "Ac": 89, "Th": 90,
        "Pa": 91, "U": 92, "Np": 93, "Pu": 94, "Am": 95, "Cm": 96, "Bk": 97, "Cf": 98, "Es": 99, "Fm": 100,
        "Md": 101, "No": 102, "Lr": 103, "Rf": 104, "Db": 105, "Sg": 106, "Bh": 107, "Hs": 108, "Mt": 109,
        "Ds": 110, "Rg": 111, "Cn": 112, "Nh": 113, "Fl": 114, "Mc": 115, "Lv": 116, "Ts": 117, "Og": 118
    }
    #count the electron number
    electron_num = 0
    for atom in atoms:
        #if the atom is not in the dict, return error and quit
        if atom not in atom_dict.keys():
            print("Error: atom {0} not in the dict".format(atom))
            quit()
        else:
            electron_num += atom_dict[atom]
    #if the electron number is odd, return 2, else return 1
    if electron_num % 2 == 0:
        return 0
    else:
        return 1


'''

This main.py will only accept one working directory, and do the processing.
Parallel dir processing should be implemented in qemb, which should also containing queueing system.

'''


def job_1_1(dir, file_control):
    global cluster_num, environ_num, control_base_num
    # job 1 is to cut the ref into cluster and environments
    # dir should be the top dir of ref
    curr_dir = os.getcwd()
    if "ref" in dir:
        os.chdir(dir)
    else:
        os.chdir(dir + '/ref')
    ref_atoms, ref_title, ref_scale_factor, ref_lattice = read_poscar('POSCAR')
    cluster_atoms, pseudo_atoms, environ_atoms, run_status, pure_cluster_num = cut_cluster(ref_atoms, ref_scale_factor, ref_lattice, file_control)
    if file_control['check_base_num_consistant']:
        if "clean" in dir:
            control_base_num = pure_cluster_num
        elif "absorb" in dir:
            if pure_cluster_num != control_base_num:
                #do a little more attempt for radius
                success_tag = False
                for i in range(5):
                    file_control_tmp = file_control.copy()
                    file_control_tmp['cluster_radius'] = file_control['cluster_radius'] + 0.1 * (i+1)
                    print("Trying to cut cluster with radius " + str(file_control_tmp['cluster_radius']))
                    cluster_atoms, pseudo_atoms, environ_atoms, run_status, pure_cluster_num = cut_cluster(ref_atoms, ref_scale_factor, ref_lattice, file_control_tmp)
                    if pure_cluster_num == control_base_num:
                        success_tag = True
                        break
                if not success_tag:
                    print("The number of atoms in dir " + dir + " is " + str(pure_cluster_num) + ", and the clean dir is " + str(control_base_num))
                    raise ValueError("The number of atoms in dir" + dir + " is not consistent with the clean dir.")
        #print("Cluster atoms number in " + dir + " is " + str(pure_cluster_num) + ", and the clean dir is " + str(control_base_num))
    #if int(file_control['jobtype']) == 1.2:
    if int(file_control['jobtype']) == 3:
        cluster_num = [atom[-1] for atom in cluster_atoms]
        environ_num = [atom[-1] for atom in environ_atoms]
    #os.system('mkdir -p cluster environ')
    if run_status == "Free":
        write_poscar(cluster_atoms, 'POSCAR.cluster', ref_scale_factor, ref_lattice)
        write_poscar(environ_atoms, 'POSCAR.environ', ref_scale_factor, ref_lattice)
        #print("Cutting cluster and environ done in " + dir)
    elif run_status == "XYZ":
        if not file_control['force_xyz_output']:
            print("The cluster of " + dir + " exceeds the boundary of the cell. Thus automatic cell expansion is invoked, thus only xyz could be written.")
        write_xyz(cluster_atoms, 'cluster.xyz', ref_scale_factor, ref_lattice)
        write_xyz(environ_atoms, 'environ.xyz', ref_scale_factor, ref_lattice)
    elif run_status == "Embedding":
        #print("Writing cluster and embedding atom xyzs in " + dir + "/ref")
        print("Writing cluster and embedding atom xyzs in " + dir)
        write_xyz(cluster_atoms, 'cluster.xyz', ref_scale_factor, ref_lattice)
        write_xyz(environ_atoms, 'charges.xyz', ref_scale_factor, ref_lattice)
        if len(pseudo_atoms) > 0:
            write_xyz(pseudo_atoms, 'pseudos.xyz', ref_scale_factor, ref_lattice)
    else:
        print("Unknown error in cutting. Please check.")
    os.chdir(curr_dir)
    return pure_cluster_num

def job_1_2(dir, file_control, cores, functional=None, basis=None, vdw=None, pseudo_calc=False):
    curr_dir = os.getcwd()
    pure_clutser_num = job_1_1(dir, file_control)
    if "ref" in dir:
        os.chdir(dir + '/..')
    else:
        os.chdir(dir)
    os.mkdir('run')
    os.chdir('run')
    with open("../ref/cluster.xyz", 'r') as f:
        lines = f.readlines()[2:]
    elements = [line.split()[0] for line in lines]
    element_merged = merge_elements(elements)
    #count and decide how to determine the spin of the cluster
    #if the cluster has no or little metal atoms, then decide it simply by the number of electrons
    #if the cluster has metal atoms and percentage is more than 50%, then split the cluster,
    #determine the spin of the metal and absorbant separately
    total_num = len(lines)
    split_flag = False
    #note this will only satisfy tmp types of nowadays.
    nowadays_metals = ['Cu', 'Ag', 'Au', 'Pt']
    for key in element_merged:
        if key in nowadays_metals:
            if element_merged[key] / total_num > 0.5 or pure_clutser_num / total_num > 0.6:
                split_flag = key
                break
    if split_flag != False:
        tmp_clu = [element for element in elements if element == split_flag]
        tmp_abs = [element for element in elements if element != split_flag]
        spin = count_mult(tmp_clu) + count_mult(tmp_abs) + 1
    else:
        spin = count_mult(elements) + 1
    #write ctrl.in
    write_rest_input(xyz="../ref/cluster.xyz", functional=functional, basis=basis, vdw=vdw, \
                    charge=0, mult=spin, proc=cores, pseudo_calc=pseudo_calc, \
                    ctrl_template=file_control["ctrl_template"], \
                    pseudo_xyz="../ref/pseudos.xyz" if os.path.exists("../ref/pseudos.xyz") else None, \
                    charge_xyz="../ref/charges.xyz" if os.path.exists("../ref/charges.xyz") else None)
    os.chdir(curr_dir)
    
