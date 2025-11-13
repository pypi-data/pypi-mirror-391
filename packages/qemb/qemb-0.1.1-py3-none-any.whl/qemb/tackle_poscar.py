import numpy as np

def compress_elements(elements):
    #输入一个元素列表，返回一个相邻计数列表
    #比如输入['C','C','O','O','C','C','H']，返回[['C',2],['O',2],['C',2],['H',1]]
    if not elements:
        return []
    count = 1
    compressed_elements = []
    for i in range(1, len(elements)):
        if elements[i] == elements[i-1]:
            count += 1
        else:
            compressed_elements.append([elements[i-1], count])
            count = 1
    compressed_elements.append([elements[-1], count])
    return compressed_elements


def merge_elements(elements):
    if not elements:
        return {}

    merged_dict = {}
    for element in elements:
        if element in merged_dict:
            merged_dict[element] += 1
        else:
            merged_dict[element] = 1
    return merged_dict

def dict_to_compressed_string(d):
    #sort the dict by key
    #d = dict(sorted(d.items()))
    return ''.join(f'{key}{value}' for key, value in d.items())

def read_poscar(poscar):
    #read the POSCAR file,
    with open(poscar, 'r') as f:
        lines = f.readlines()
    #if a line is empty, remove everything after it
    #for i in range(len(lines)):
    #    if not lines[i].strip():
    #        lines = lines[0:i]
    #        break
    #check if selective dynamics is used, if so, delete the line
    if lines[7][0].lower() == 's':
        lines.pop(7)
    #check whether cartesian is used, if so, convert to direct
    if lines[7][0].lower() == 'c':
        lattice = np.array([list(map(float, lines[2].split())),
                            list(map(float, lines[3].split())),
                            list(map(float, lines[4].split()))])
        coord = np.array([list(map(float, line.split()[0:3])) for line in lines[8:]])
        #convert the cartesian coord to direct coord
        coord = np.dot(coord, np.linalg.inv(lattice))
    elif lines[7][0].lower() == 'd':
        coord = np.array([list(map(float, line.split()[0:3])) for line in lines[8:]])
    else:
        raise ValueError('Unknown coordinate system')
    #now compile atom type and coord into a new list
    count = 0
    atoms = []
    for i in range(len(lines[5].split())):
        for j in range(int(lines[6].split()[i])):
            #compile atom type and coord into a four element list, then append to atoms
            atom = list(map(float,coord[count]))
            atom.insert(0,lines[5].split()[i])
            atom.append(count)
            atoms.append(atom)
            count += 1
    title = lines[0]
    scale_factor = float(lines[1])
    lattice = lines[2:5]
    return atoms, title, scale_factor, lattice

def write_poscar(poscar_atoms, poscar_name, scale_factor, lattice):
    #count the merged elements
    element_compressed = compress_elements([atom[0] for atom in poscar_atoms])
    poscar_title = f'Cluster {dict_to_compressed_string(merge_elements([atom[0] for atom in poscar_atoms]))}'
    lattice_calc = np.array([list(map(float, line.split())) for line in lattice])
    coord = np.array([atom[1:4] for atom in poscar_atoms])
    coord = np.dot(coord, lattice_calc)
    coord = scale_factor * coord

    with open(poscar_name, 'w') as f:
        #write a title
        f.write(poscar_title + '\n')
        #write a scale factor
        f.write(f'  {scale_factor}\n')
        #write the lattice
        for line in lattice:
            f.write(line)
        #write the elements
        for key in element_compressed:
            f.write(f'    {key[0]}')
        f.write('\n')
        #write the number of each element
        for key in element_compressed:
            f.write(f'    {key[1]}')
        f.write('\n')
        #write the coord
        #f.write('Cartesian\n')
        f.write('Direct\n')
        for atom in poscar_atoms:
            f.write(f'{" ".join(f"{coord:20.15f}" for coord in atom[1:4])}\n')

def write_xyz(xyz_atoms, xyz_name, scale_factor, lattice):
    xyz_elements = merge_elements([atom[0] for atom in xyz_atoms])
    xyz_title = f'{dict_to_compressed_string(xyz_elements)}'
    #since xyz_atoms is in direct coord, convert it to cartesian coord
    lattice = np.array([list(map(float, line.split())) for line in lattice])
    coord = np.array([atom[1:4] for atom in xyz_atoms])
    coord = np.dot(coord, lattice)
    coord = scale_factor * coord
    with open(xyz_name, 'w') as f:
        f.write(f'{len(xyz_atoms)}\n')
        f.write(f'{xyz_title}\n')
        for i in range(len(xyz_atoms)):
            f.write(f'{xyz_atoms[i][0]:2} {" ".join(f"{coord[i][j]:20.15f}" for j in range(3))}\n') 




