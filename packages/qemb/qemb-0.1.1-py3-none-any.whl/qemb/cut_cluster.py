import math
import numpy as np
from collections import Counter
from shapely.geometry import Point, Polygon 
from .tackle_poscar import merge_elements

def clean_periodic_atoms(atoms):
    #since in this case, all coord is direct, thus we convert all z coord above 0.85 to below 0
    for atom in atoms:
        if atom[3] > 0.8:
            atom[3] -= 1
    return atoms

def check_if_slab_abs_mix(ref_elements, ref_num, elements, num):
    for key in ref_elements:
        if key not in elements:
            return 0
        if ref_elements[key] > elements[key]:
            return 0
    if ref_num > num:
        return 0
    return 1

def split_list(ori_list, n):
    k, m = divmod(len(ori_list), n)
    return [ori_list[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

def split_abs_n_slab(atoms, scale_factor, lattice):
    #avoid atoms escape the box
    atoms = clean_periodic_atoms(atoms)
    #get the length of c
    c = scale_factor * np.linalg.norm(np.array(list(map(float, lattice[2].split()))))
    #trying to split the system into layers with the threshold of 0.8 angstrom
    #first sort the atoms by z
    atoms.sort(key=lambda x: x[3])
    #then split the atoms into layers
    layers = []
    layer = []
    for atom in atoms:
        if not layer:
            layer.append(atom)
        else:
            if abs(atom[3] - layer[-1][3]) < (0.8 / c):
                layer.append(atom)
            else:
                layers.append(layer)
                layer = [atom]
    layers.append(layer)
    #for layer in layers:
    #    print(layer)
    #now we have the layers, we need to split the layers into abs and slab
    #slab layers should have a rather consistent element composition, thus we can use the first layer as the reference
    ref_elements = merge_elements(list(atom[0] for atom in layers[0]))
    #and a rather consistent number of atoms
    ref_num = len(layers[0])
    #now we can split the layers
    abs_atoms = []
    slab_atoms = []
    slab_num = 0
    for layer in layers:
        elements = merge_elements([atom[0] for atom in layer])
        num = len(layer)
        if elements == ref_elements and num == ref_num:
            for atom in layer:
                slab_atoms.append(atom)
            slab_num += 1
        #add a check for the slab layer, if the layer has all the elements in ref_elements, but has another number of atoms, then force to recut it
        elif check_if_slab_abs_mix(ref_elements, ref_num, elements, num):
            print("Seems some absorbant is too near to the slab, force to recut the slab layer for slab uniformity.")
            #force to cut the exact number of atoms as ref
            for atom in layer[0:ref_num]:
                slab_atoms.append(atom)
            slab_num += 1
            for atom in layer[ref_num:]:
                abs_atoms.append(atom)
        else:
            for atom in layer:
                abs_atoms.append(atom)
    #regenerate atoms_num by layers for slab atoms
    layered_slab_atoms = split_list(slab_atoms, slab_num)
    return slab_atoms, abs_atoms, layered_slab_atoms


def are_elements_equal_with_tolerance(element1, element2, tolerance=0.02):
    """
    判断两个元素是否相等，允许数值上的容忍度。
    """
    if element1[0] != element2[0]:  # 比较元素类型
        return False
    return all(abs(a - b) <= tolerance for a, b in zip(element1[1:], element2[1:]))


def are_lists_equal_with_tolerance(list1, list2, tolerance):
    """
    判断两个集合是否相等，允许数值上的容忍度。
    """
    if len(list1) != len(list2):
        return False
    for elem1 in list1:
        if not any(are_elements_equal_with_tolerance(elem1, elem2, tolerance) for elem2 in list2):
            return False
    return True


def expand_base(ori_base_atoms, ori_layered_base_atoms, tmp_expand_size, tmp_z_expand_size, tmp_z_expand_is_num):
    #expand the base_atoms
    base_atoms = []
    layered_base_atoms = []
    ori_base_atoms_tmp = ori_base_atoms.copy()
    ori_layered_base_atoms_tmp = ori_layered_base_atoms.copy()

    #for base atoms in z direction
    #if the tmp_z_expand_size equals to -1, then skip the z direction expansion
    if tmp_z_expand_size > 0:
        #get the mean layer distance
        bottom_z = np.mean([atom[3] for atom in ori_layered_base_atoms_tmp[0]])
        mean_layer_distance = np.mean([atom[3] for atom in ori_layered_base_atoms_tmp[1]]) - bottom_z
        if tmp_z_expand_is_num:
            add_layer_num = tmp_z_expand_size
        else:
            add_layer_num = int(tmp_z_expand_size / mean_layer_distance) + 1
        #construct a patterns to decide the what the next layer is like
        layered_pattern = []
        template_layer = []
        for layer in ori_layered_base_atoms_tmp:
            tmp_layer_atom = []
            tmp_template_atom = []
            for atom in layer:
                tmp_layer_atom.append((atom[0], round(atom[1], 2), round(atom[2], 2)))
                tmp_template_atom.append([atom[0], atom[1], atom[2], 0.0, atom[4]])
            template_layer.append(tmp_template_atom)
            layered_pattern.append(tmp_layer_atom)
        #clean in the layered_pattern, if any coord is 1.0, then convert it to 0.0
        for i in range(len(layered_pattern)):
            for j in range(len(layered_pattern[i])):
                if layered_pattern[i][j][1] == 1.0:
                    layered_pattern[i][j] = (layered_pattern[i][j][0], 0.0, layered_pattern[i][j][2])
                if layered_pattern[i][j][2] == 1.0:
                    layered_pattern[i][j] = (layered_pattern[i][j][0], layered_pattern[i][j][1], 0.0)
        #record the repeated pattern
        del_layer = []
        for i in range(len(layered_pattern)):
            for j in range(i + 1, len(layered_pattern)):
                if are_lists_equal_with_tolerance(layered_pattern[i], layered_pattern[j], tolerance=0.03):
                    del_layer.append(j)
        del_layer.reverse()
        for i in del_layer:
            layered_pattern.pop(i)
            template_layer.pop(i)
        template_layer.reverse()
        layered_pattern.reverse()
        #check the bottom layer is in which layer of the template
        tmp_bottom_layer_pattern = [(atom[0], round(atom[1], 2), round(atom[2], 2)) for atom in ori_layered_base_atoms_tmp[0]]
        #clean the bottom layer pattern
        for i in range(len(tmp_bottom_layer_pattern)):
            if tmp_bottom_layer_pattern[i][1] == 1.0:
                tmp_bottom_layer_pattern[i] = (tmp_bottom_layer_pattern[i][0], 0.0, tmp_bottom_layer_pattern[i][2])
            if tmp_bottom_layer_pattern[i][2] == 1.0:
                tmp_bottom_layer_pattern[i] = (tmp_bottom_layer_pattern[i][0], tmp_bottom_layer_pattern[i][1], 0.0)
        for i in range(len(layered_pattern)):
            if are_lists_equal_with_tolerance(layered_pattern[i], tmp_bottom_layer_pattern, tolerance=0.03):
                bottom_layer = i
                break
        #add the layers
        for i in range(1, add_layer_num + 1):
            tmp_new_layer = []
            for atom in template_layer[ (i + bottom_layer) % len(template_layer)]:
                tmp_new_layer.append([atom[0], atom[1], atom[2], float(bottom_z - i * mean_layer_distance), atom[4]])
            ori_layered_base_atoms_tmp.append(tmp_new_layer)
            ori_base_atoms_tmp += tmp_new_layer
    # for base atoms in x and y direction
    # if tmp_expand_size equals to -1, then skip the x and y direction expansion
    if tmp_expand_size > 0:
        for i in range(-tmp_expand_size, tmp_expand_size + 1):
            for j in range(-tmp_expand_size, tmp_expand_size + 1):
                for atom in ori_base_atoms_tmp:
                    base_atoms.append([atom[0], atom[1] + i, atom[2] + j, atom[3], atom[4]])
        #now for layered atoms
        for layer in ori_layered_base_atoms_tmp:
            tmp_layer = []
            for i in range(-tmp_expand_size, tmp_expand_size + 1):
                for j in range(-tmp_expand_size, tmp_expand_size + 1):
                    for atom in layer:
                        tmp_layer.append([atom[0], atom[1] + i, atom[2] + j, atom[3], atom[4]])
            layered_base_atoms.append(tmp_layer)
    else:
        #if tmp_expand_size is -1, then just copy the ori_base_atoms and ori_layered_base_atoms
        base_atoms = ori_base_atoms_tmp.copy()
        layered_base_atoms = ori_layered_base_atoms_tmp.copy()
    return base_atoms, layered_base_atoms


def direct_distance(atom1, atom2, a, b, c, periodic=False):
    """
    计算两点间的距离（支持周期性边界条件）
    
    参数:
    atom1, atom2: 原子的分数坐标 [u, v, w]
    a, b, c: 晶格向量（可以是列表或np.array）
    periodic: 是否使用周期性边界条件
    
    返回:
    两点间的最短距离（考虑周期性镜像）
    """
    # 确保晶格向量是numpy数组
    if isinstance(a, list):
        a = np.array(a)
    if isinstance(b, list):
        b = np.array(b)
    if isinstance(c, list):
        c = np.array(c)
    
    if periodic:
        # 计算分数坐标差值
        du, dv, dw = np.array(atom2) - np.array(atom1)
        
        # 对分数坐标进行周期性校正（确保差值在[-0.5, 0.5)范围内）
        du -= round(du)
        dv -= round(dv)
        dw -= round(dw)
        
        # 将校正后的分数坐标差值转换为笛卡尔向量
        delta_cart = du * a + dv * b + dw * c
        
        # 计算校正后的距离
        return np.linalg.norm(delta_cart)
    
    else:
        # 非周期性情况：直接转换坐标并计算距离
        atom1_cart = atom1[0]*a + atom1[1]*b + atom1[2]*c
        atom2_cart = atom2[0]*a + atom2[1]*b + atom2[2]*c
        return np.linalg.norm(atom1_cart - atom2_cart)
    
def assure_absorbate(absorbates, a, b, c):
    # First get the bonds in the absorbates
    suspicious_atoms = []
    for i in range(len(absorbates)):
        for j in range(i + 1, len(absorbates)):
            real_bond_length = round(direct_distance(absorbates[i][1:4], absorbates[j][1:4], a, b, c, periodic=True), 1)
            cart_bond_length = round(direct_distance(absorbates[i][1:4], absorbates[j][1:4], a, b, c, periodic=False), 1)
            if real_bond_length < 2.1 and real_bond_length != cart_bond_length:
                #means the two atoms are suspicious in periodic error, add them to the suspicious_atoms
                if absorbates[i] not in suspicious_atoms:
                    suspicious_atoms.append(absorbates[i])
                if absorbates[j] not in suspicious_atoms:
                    suspicious_atoms.append(absorbates[j])
    # Do cycle again, for those has equal bond length, remove the atoms in suspicious_atoms
    for i in range(len(absorbates)):
        for j in range(i + 1, len(absorbates)):
            real_bond_length = round(direct_distance(absorbates[i][1:4], absorbates[j][1:4], a, b, c, periodic=True), 1)
            cart_bond_length = round(direct_distance(absorbates[i][1:4], absorbates[j][1:4], a, b, c, periodic=False), 1)
            if real_bond_length < 2.1 and real_bond_length == cart_bond_length:
                if absorbates[i] in suspicious_atoms:
                    suspicious_atoms.remove(absorbates[i])
                if absorbates[j] in suspicious_atoms:
                    suspicious_atoms.remove(absorbates[j])

    # then for the suspicious_atoms, convert all big coord to small ones
    # first extract the atom number
    sus_num = [atom[-1] for atom in suspicious_atoms]
    # try converting x
    for i in range(len(absorbates)):
        if absorbates[i][-1] in sus_num:
            #means this atom is suspicious, convert it to the small coord
            if absorbates[i][1] > 0.89:
                absorbates[i][1] -= 1
            elif absorbates[i][1] < 0.11:
                absorbates[i][1] += 1
            if absorbates[i][2] > 0.89:
                absorbates[i][2] -= 1
            elif absorbates[i][2] < 0.11:
                absorbates[i][2] += 1
    return absorbates
        
            
    

'''
def get_atom_distance(atom1, atom2):
    return np.linalg.norm(np.array(atom1)-np.array(atom2))
def get_layers_num(base_atoms,absorbates):
    first_layer_num = []
    #init data
    raw_base_atoms = [[atom[0], atom[1], atom[2], round(atom[3], 0)] for atom in base_atoms]
    layers = sorted(list(set([round(atom.position[2], 0) for atom in base_atoms])), reverse=True)
    if absorbates[0][3] < layers[0]:
        layers = sorted(layers)
    layer_num = []
    layers_num = []
    #get the layers
    for layer in layers:
        for i in range(len(base_atoms)):
            if raw_base_atoms[i][3] == layers[layer]:
                layer_num.append(i)
        layers_num.append(layer_num)
    #check if layers collect works.
    #if all atoms' z coordinates' mse in one layer is less than 0.3, then the layers collect works
    #if not, print false and return nothing
    for i in range(len(layers_num)):
        z = [base_atoms[num][3] for num in layers_num[i]]
        mse = np.mean((z - np.mean(z))**2)
        if mse > 0.1:
            print(f'Layer {i} showing a mse of {mse}, which is not correct. Thus shutting down layer recognition.')
            return False
    return layers_num
'''

def get_hex_or_sq(base_atoms, layered_base_atoms, ori_point, expand_num, a,b,c, vitural_center=False):
    #check if the system is a metal slab or a NaCl-like system
    if len(set(atom[0] for atom in base_atoms)) != 1:
        element_dict = dict(Counter([atom[0] for atom in base_atoms]))
        if len(element_dict) != 2 or element_dict[list(element_dict.keys())[0]] != element_dict[list(element_dict.keys())[1]]:
            raise ValueError('This method should only be used in metal slab or a NaCl-like system.')
        else:
            system_type = 'nacl'
    else:
        system_type = 'metal'

    tmp_length = 1000
    for atom in layered_base_atoms[-1]:
        if 0.5 < direct_distance(atom[1:4], ori_point, a, b, c, periodic=False) < tmp_length:
            tmp_length = direct_distance(atom[1:4], ori_point, a, b, c, periodic=False)
    near_atoms = [
        atom
        for atom in layered_base_atoms[-1] 
        if round(direct_distance(atom[1:4], ori_point, a, b, c, periodic=False), 0) == round(tmp_length, 0)
    ]
    vectors = []
    for atom in near_atoms:
        vectors.append(np.array(atom[1:4]) - np.array(ori_point))
    #from copilot, sort the vectors by angle
    # Calculate the angles of each vector
    angles = [math.atan2(vector[1], vector[0]) for vector in vectors]
    # Combine vectors and angles
    vector_angle = list(zip(vectors, angles))
    # Sort by angle
    vector_angle.sort(key=lambda x: x[1])
    # Get the sorted vectors
    sorted_vectors = [va[0] for va in vector_angle]

    # By using this value, we have made a assumption that the first layer is a 2d packing metal
    if vitural_center:
        correct_first_cluster = (2*expand_num)**2
    elif system_type == 'metal':
        correct_first_cluster = 1 + int(6 * (expand_num + 1) * expand_num / 2)
    elif system_type == 'nacl':
        correct_first_cluster = 2 * expand_num**2 + 2 * expand_num + 1
    if vitural_center:
        num_cp = 2 * expand_num + 1
        nup_cp_max = 2 * expand_num + 5
    else:
        num_cp = expand_num
        nup_cp_max = expand_num + 5
    first_cluster = []
    tmp_expand_size = max(np.linalg.norm(a), np.linalg.norm(b)) * 0.01
    num_cp = num_cp - tmp_expand_size
    while len(first_cluster) != correct_first_cluster:
        if num_cp > nup_cp_max:
            return polygon_points, False
        num_cp = num_cp + tmp_expand_size
        first_cluster = []
        polygon_points= [tuple([(num_cp-1) * x + y for x, y in zip(vector[:2], ori_point)]) for vector in sorted_vectors]
        polygon = Polygon(polygon_points)
        for atom in layered_base_atoms[-1]:
            point = Point(tuple(atom[1:3]))
            if polygon.contains(point):
                first_cluster.append(atom)
    num_cp = num_cp + tmp_expand_size
    return polygon, True


def get_second_expand(base_atoms, layered_base_atoms, ori_point, expand_num, a, b, c):
    #check if the system is a NaCl-like system
    if len(dict(Counter([atom[0] for atom in base_atoms]))) != 2:
        raise ValueError('This method should only be used in NaCl-like system.')
    
    tmp_length = 1000
    for atom in layered_base_atoms[-1]:
        if 0.5 < direct_distance(atom[1:4], ori_point, a, b, c, periodic=False) < tmp_length:
            tmp_length = direct_distance(atom[1:4], ori_point, a, b, c, periodic=False)
    # search the second nearest atoms, that is about 1.5 times the first nearest atoms
    near_atoms = [
        atom
        for atom in layered_base_atoms[-1]
        if round(direct_distance(atom[1:4], ori_point, a, b, c, periodic=False), 0) == round(tmp_length * 1.5, 0)
    ]
    vectors = []
    for atom in near_atoms:
        vectors.append(np.array(atom[1:4]) - np.array(ori_point))
    #from copilot, sort the vectors by angle
    # Calculate the angles of each vector
    angles = [math.atan2(vector[1], vector[0]) for vector in vectors]
    # Combine vectors and angles
    vector_angle = list(zip(vectors, angles))
    # Sort by angle
    vector_angle.sort(key=lambda x: x[1])
    # Get the sorted vectors
    sorted_vectors = [va[0] for va in vector_angle]

    # By using this value, we have made a assumption that the first layer is a 2d packing metal
    correct_first_cluster = (2 * expand_num + 1) ** 2
    num_cp = expand_num
    nup_cp_max = expand_num + 5
    first_cluster = []
    tmp_expand_size = (np.linalg.norm(a) + np.linalg.norm(b)) / 40
    num_cp = num_cp - tmp_expand_size
    while len(first_cluster) != correct_first_cluster:
        if num_cp > nup_cp_max:
            return polygon_points, False
        num_cp = num_cp + tmp_expand_size
        first_cluster = []
        polygon_points= [tuple([(num_cp-1) * x + y for x, y in zip(vector[:2], ori_point)]) for vector in sorted_vectors]
        if len(polygon_points) < 4:
            continue
        polygon = Polygon(polygon_points)
        for atom in layered_base_atoms[-1]:
            point = Point(tuple(atom[1:3]))
            if polygon.contains(point):
                first_cluster.append(atom)
    #num_cp = num_cp + tmp_expand_size
    return polygon, True


def get_hollow_meshed(top_layer_atoms):
    ori_points = []
    for atom in top_layer_atoms:
        ori_points.append(atom[1:3])
    point_set = {(x, y) for x, y in ori_points}
    # 提取所有唯一的x和y坐标并排序
    x_coords = sorted({x for x, y in ori_points})
    y_coords = sorted({y for x, y in ori_points})
    
    centers = []
    
    # 遍历所有相邻的x坐标对
    for i in range(len(x_coords) - 1):
        x_left = x_coords[i]
        x_right = x_coords[i + 1]
        
        # 遍历所有相邻的y坐标对
        for j in range(len(y_coords) - 1):
            y_bottom = y_coords[j]
            y_top = y_coords[j + 1]
            
            # 检查四个顶点是否存在
            if ((x_left, y_bottom) in point_set and
                (x_right, y_bottom) in point_set and
                (x_left, y_top) in point_set and
                (x_right, y_top) in point_set):
                
                # 计算中心坐标
                center_x = (x_left + x_right) / 2
                center_y = (y_bottom + y_top) / 2
                centers.append([center_x, center_y])
    
    return centers        



def cut_cluster(atoms, scale_factor, lattice, file_control):
    jobtype = file_control['jobtype']
    separation_method = file_control['separation_method']
    absorbate_atoms_num = file_control['absorbate_atoms_num']
    #cut_method = file_control['cluster_cutting_method']
    cluster_major_method = file_control['cluster_cutting_major_method']
    cluster_minor_method = file_control['cluster_cutting_minor_method']
    radius = file_control['cluster_radius']
    height = file_control['cluster_height']
    layers = file_control['cluster_layers']
    expand_num = file_control['cluster_expand_num']
    ori_point = file_control['cluster_ori_point']

    #split thhe lattice into a,b,c
    a = np.array(list(map(float, lattice[0].split())))
    b = np.array(list(map(float, lattice[1].split())))
    c = np.array(list(map(float, lattice[2].split())))
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    norm_c = np.linalg.norm(c)

    only_xyz_output = False
    if file_control['force_xyz_output']:
        only_xyz_output = True

    #first spilt the poscar into base and absorbates
    if separation_method == 1:
        ori_base_atoms, absorbates, ori_layered_base_atoms = split_abs_n_slab(atoms, scale_factor, lattice)
        #print(ori_base_atoms)
        #print(absorbates)
        #print(ori_layered_base_atoms)

    elif separation_method == 2:
        if absorbate_atoms_num == 0:
            raise ValueError('If you use method 2, you should input the absorbate_atoms_num.')
        #sort the atoms, the highest abs_atoms_num atoms are absorbates
        atoms.sort(key=lambda x: x[3])
        base_num = len(atoms) - absorbate_atoms_num
        ori_base_atoms = atoms[:base_num]
        absorbates = atoms[base_num:]
        ori_base_atoms.sort(key=lambda x: x[4])
        absorbates.sort(key=lambda x: x[4])
    else:
        raise ValueError('Unknown method. Method should be 1 or 2')
    
    #check if periodic condition breaks the absorbates
    absorbates = assure_absorbate(absorbates, a, b, c)
            

    #consider various methods to cut the cluster
    #check input. if the method is not in the range, raise error
    if cluster_major_method < 1 or cluster_major_method > 5:
        raise ValueError('Unknown method. Major method should be in the range of 1 to 4')
    if cluster_minor_method < 1 or cluster_minor_method > 7:
        raise ValueError('Unknown method. Minor method should be in the range of 1 to 7')
    #1. decide the ori_point by the average center of the absorbates
    if cluster_major_method == 2 or cluster_major_method == 4:
        if len(absorbates) == 0:
            print('Warning: not a absorb system, reset ori_point to [0.5, 0.5, 0.5]')
            ori_point = [0.5, 0.5, 0.5]
        else:
            ori_point = np.mean([absorbate[1:4] for absorbate in absorbates], axis=0)
    #2. with a input ori_point
    #check if the ori_point is changed, if not should mean the user did not input the ori_point, raise error
    if cluster_major_method == 1 or cluster_major_method == 3:
        if ori_point == [1000,1000,1000]:
            raise ValueError('If you use method 1.x or 3.x, you should input the ori_point.')
    # search the nearest base atom to the ori_point
    if cluster_major_method == 1 or cluster_major_method == 2:
        min_dis = 1000
        for i in range(len(ori_base_atoms)):
            dis = direct_distance(ori_base_atoms[i][1:4], ori_point, a, b, c, periodic=False)
            if dis < min_dis:
                min_dis = dis
                min_atom = i
        #central_atom = base_atoms[min_atom]
        ori_point = ori_base_atoms[min_atom][1:4]
    #sear
    if cluster_major_method == 4:
        if separation_method != 1:
            raise ValueError('Method 4 can only be used with separation method 1.')
        top_layer_atoms = ori_layered_base_atoms[-1]
        centers = get_hollow_meshed(top_layer_atoms)
        min_dis = 1000
        for i in range(len(centers)):
            dis = direct_distance(centers[i], ori_point, a, b, c, periodic=False)
            if dis < min_dis:
                min_dis = dis
                min_center = i
        #central_atom = centers[min_center]
        ori_point = centers[min_center]
    
    cluster_atoms = []
    #with central atom set, several methods can be used to cut the cluster
    #this can be retrived from the method input
    #sub_method = int(cluster_minor_method)
    #check in the input radius or expand_num, the base_atoms has the sufficient range
    if cluster_minor_method == 1 or cluster_minor_method == 2 or cluster_minor_method == 4:
        if (radius / norm_a + ori_point[0]) > 1 or (radius / norm_b + ori_point[1]) > 1 or (ori_point[2] - radius / norm_c) < 0:
            if int(jobtype) == 3:
                raise ValueError('For DMET calculation, the cluster should not exceed the range of the base atoms.')
            #expand the base_atoms and layered_base_atoms
            #ori_base_atoms = base_atoms
            #ori_layered_base_atoms = layered_base_atoms
            tmp_z_expand_is_num = False
            tmp_expand_size = int(max(radius / norm_a + ori_point[0], radius / norm_b + ori_point[1]))
            if cluster_minor_method == 1:
                tmp_z_expand_size = abs(ori_point[2] - radius / norm_c)
            if cluster_minor_method == 2:
                tmp_z_expand_size = -1
            if cluster_minor_method == 4:
                if height == 1000 and layers == 1000:
                    raise ValueError('If you use method x.4 or x.5, you should input the height or layers.')
                if height != 1000 and layers != 1000:
                    raise ValueError('You should only input height or layers, not both.')
                if height != 1000:
                    tmp_z_expand_size = abs(ori_point[2] - height / norm_c)
                elif layers != 1000 and layers > len(ori_layered_base_atoms):
                    tmp_z_expand_size = layers - len(ori_layered_base_atoms)
                    tmp_z_expand_is_num = True
                elif layers != 1000 and layers <= len(ori_layered_base_atoms):
                    tmp_z_expand_size = -1
            base_atoms, layered_base_atoms = expand_base(ori_base_atoms, ori_layered_base_atoms, tmp_expand_size, tmp_z_expand_size, tmp_z_expand_is_num)
            #in this case, atom num will be useless, thus only output the xyz file
            only_xyz_output = True
        else:
            base_atoms = ori_base_atoms
            layered_base_atoms = ori_layered_base_atoms
    elif cluster_minor_method == 5 or cluster_minor_method == 7:
        if height == 1000 and layers == 1000:
            raise ValueError('If you use method x.4, x.5, or x.7, you should input the height or layers.')
        if height != 1000 and layers != 1000:
            raise ValueError('You should only input height or layers, not both.')
        if height != 1000 and (ori_point[2] - height / norm_c) < 0:
            tmp_z_expand_size = abs(ori_point[2] - height / norm_c)
            only_xyz_output = True
            base_atoms, layered_base_atoms = expand_base(ori_base_atoms, ori_layered_base_atoms, -1, tmp_z_expand_size, False)
        elif layers != 1000 and layers > len(ori_layered_base_atoms):
            tmp_z_expand_size = layers - len(ori_layered_base_atoms)
            tmp_z_expand_is_num = True
            only_xyz_output = True
            base_atoms, layered_base_atoms = expand_base(ori_base_atoms, ori_layered_base_atoms, -1, tmp_z_expand_size, tmp_z_expand_is_num)
        else:
            base_atoms = ori_base_atoms
            layered_base_atoms = ori_layered_base_atoms
    elif cluster_minor_method == 3 or cluster_minor_method == 6:
        tmp_z_expand_size = -1
        tmp_z_expand_is_num = False
        base_atoms = ori_base_atoms
        layered_base_atoms = ori_layered_base_atoms

    #now we can cut the cluster
    #1. cut the cluster spherically with a input radius
    if cluster_minor_method == 1:
        if radius == 1000:
            raise ValueError('If you use method x.1, you should input the radius.')
        for i in range(len(base_atoms)):
            dis = direct_distance(base_atoms[i][1:4], ori_point, a, b, c, periodic=False)
            if dis < radius:
                cluster_atoms.append(base_atoms[i])
    #2. cut the cluster into a cylinder with a input radius
    if cluster_minor_method == 2 or cluster_minor_method == 4:
        if radius == 1000:
            raise ValueError('If you use method x.2 or x.4, you should input the radius.')
        for i in range(len(base_atoms)):
            tmp_base_point = [base_atoms[i][1], base_atoms[i][2], 0.0]
            tmp_ori_point = [ori_point[0], ori_point[1], 0.0]
            dis = direct_distance(tmp_base_point, tmp_ori_point, a, b, c, periodic=False)
            if dis < radius:
                cluster_atoms.append(base_atoms[i])
    #3. cut the cluster as a expanding polygon with a expanding atom number
    if cluster_minor_method == 3 or cluster_minor_method == 5:
        if expand_num == 1000:
            raise ValueError('If you use method x.3 or x.5, you should input the expand_num.')
        if separation_method != 1:
            raise ValueError('Sub method 3 can only be used with separation method 1.')
        #print('Warning: ')
        #print('You should notice, as far as its design, this method should only be used in metal slab system.')
        #print('Odd cluster and results may occur if you use it in other systems.')
        #get the hexagon
        if cluster_major_method == 4:
            polygon, status = get_hex_or_sq(base_atoms, layered_base_atoms, ori_point, expand_num, a, b, c, True)
        else:
            polygon, status = get_hex_or_sq(base_atoms, layered_base_atoms, ori_point, expand_num, a, b, c, False)
        while not status:
            #means the surface may contains not sufficient atoms, expanding the base_atoms
            #if False, the return will be the polygon points, check the biggest one as a expand_num
            tmp_expand_size = 0
            for i in range(len(polygon)):
                if int(round(abs(polygon[i][0]),0)) > tmp_expand_size:
                    tmp_expand_size = int(round(abs(polygon[i][0]),0))
                if int(round(abs(polygon[i][1]),0)) > tmp_expand_size:
                    tmp_expand_size = int(round(abs(polygon[i][1]),0))
            base_atoms, layered_base_atoms = expand_base(ori_base_atoms, ori_layered_base_atoms, tmp_expand_size, -1, False)
            if cluster_major_method == 4:
                polygon, status = get_hex_or_sq(base_atoms, layered_base_atoms, ori_point, expand_num, a, b, c, True)
            else:
                polygon, status = get_hex_or_sq(base_atoms, layered_base_atoms, ori_point, expand_num, a, b, c, False)
            only_xyz_output = True
        for i in range(len(base_atoms)):
            point = Point(tuple(base_atoms[i][1:3]))
            if polygon.contains(point):
                cluster_atoms.append(base_atoms[i])
    #4. cut the cluster expand from the second nearest atoms in to a new square in NaCl-like system
    if cluster_minor_method == 6 or cluster_minor_method == 7:
        if expand_num == 1000:
            raise ValueError('If you use method x.6 or x.7, you should input the expand_num.')
        if separation_method != 1:
            raise ValueError('Sub method 6 can only be used with separation method 1.')
        #get the square
        polygon, status = get_second_expand(base_atoms, layered_base_atoms, ori_point, expand_num, a, b, c)
        while not status:
            #means the surface may contains not sufficient atoms, expanding the base_atoms
            #if False, the return will be the polygon points, check the biggest one as a expand_num
            tmp_expand_size = 0
            for i in range(len(polygon)):
                if int(round(abs(polygon[i][0]),0)) > tmp_expand_size:
                    tmp_expand_size = int(round(abs(polygon[i][0]),0))
                if int(round(abs(polygon[i][1]),0)) > tmp_expand_size:
                    tmp_expand_size = int(round(abs(polygon[i][1]),0))
            base_atoms, layered_base_atoms = expand_base(ori_base_atoms, ori_layered_base_atoms, tmp_expand_size, -1, False)
            polygon, status = get_second_expand(base_atoms, layered_base_atoms, ori_point, expand_num, a, b, c)
            only_xyz_output = True
        for i in range(len(base_atoms)):
            point = Point(tuple(base_atoms[i][1:3]))
            if polygon.contains(point):
                cluster_atoms.append(base_atoms[i])
    #5. fine-tuning of 2, cut the cylinder with input height ot layers
    if cluster_minor_method == 4 or cluster_minor_method == 5 or cluster_minor_method == 7:
        if height == 1000 and layers == 1000:
            raise ValueError('If you use method 4, 5, or 7, you should input the height or layers.')
        if height != 1000 and layers != 1000:
            raise ValueError('You should only input height or layers, not both.')
        if height != 1000:
            cluster_atoms = [atom for atom in cluster_atoms if abs(atom[3] - ori_point[2]) <= height]
        elif layers != 1000:
            layered_base_atoms.reverse()
            if layers <= 0:
                raise ValueError('The input layers should be larger than 0.')
            #remain the atom in selected layers
            target_layers_atoms = [atom for layer in layered_base_atoms[:layers] for atom in layer]
            cluster_atoms = [atom for atom in cluster_atoms if atom in target_layers_atoms]
            layered_base_atoms.reverse()

    #print(len(cluster_atoms))
    #print(len(absorbates))

    #now construct the final cluster and environ
    #first is to add the absorbates num to the cluster num, notice the num should be the same as in the atoms
    pure_cluster_num = len(cluster_atoms)
    cluster_atoms = [atom for atom in cluster_atoms] + [atom for atom in absorbates]
    if int(jobtype) != 2 and jobtype != 1.3 and jobtype != 1.4 :
        environ_atoms = [atom for atom in base_atoms if atom not in cluster_atoms]
        if not only_xyz_output:
            return cluster_atoms, [], environ_atoms, "Free", pure_cluster_num
        else:
            return cluster_atoms, [], environ_atoms, "XYZ", pure_cluster_num 
    
    
    pseudo_atoms = []
    #if the jobtype is 2 or 1.2, and the pseudo_cutting is True, we need to cut a pseudo cluster
    if (int(jobtype) == 2 or jobtype == 1.2) and file_control['pseudo_cutting']:
        #cut a pseudo cluster for the embedding, just as the cluster
        #the pseudo cluster will inherit the same ori_point as cluster
        pseudo_cut_method = file_control['pseudo_cutting_sub_method']
        pseudo_radius = file_control['pseudo_radius']
        pseudo_height = file_control['pseudo_height']
        pseudo_layers = file_control['pseudo_layers']
        pseudo_expand_num = file_control['pseudo_expand_num']
        
        # Using the same ori_point as the cluster, thus only cut method
        if pseudo_cut_method < 1 or pseudo_cut_method > 7:
            raise ValueError('Unknown method. Pseudo cutting method should be in the range of 1 to 7')
        #assure pseudo radius or height or layers is bigger than cluster
        if pseudo_cut_method == 1 or pseudo_cut_method == 2 or pseudo_cut_method == 4:
            if pseudo_radius == 1000:
                raise ValueError('Radius should be input for pseudo cluster.')
            if pseudo_radius < radius:
                raise ValueError('Radius of pseudo cluster should be larger than the cluster.')
        if pseudo_cut_method == 4 or pseudo_cut_method == 5 or pseudo_cut_method == 7:
            if pseudo_height == 1000 and pseudo_layers == 1000:
                raise ValueError('If you use method 4, 5, or 7, you should input the pseudo height or layers.')
            if pseudo_height != 1000 and pseudo_layers != 1000:
                raise ValueError('You should only input pseudo height or layers, not both.')
            if pseudo_height != 1000 and pseudo_height < height:
                raise ValueError('Height of pseudo cluster should be larger than the cluster.')
            if pseudo_layers != 1000 and pseudo_layers < layers:
                raise ValueError('Layers of pseudo cluster should be larger than the cluster.')
        if pseudo_cut_method == 3 or pseudo_cut_method == 5 \
            or pseudo_cut_method == 6 or pseudo_cut_method == 7:
            if expand_num == 1000:
                raise ValueError('If you use method 3, 5, 6, or 7, you should input the expand_num.')
        # then check if we need to expand the base_atoms and layered_base_atoms
        if pseudo_cut_method == 1 or pseudo_cut_method == 2 or pseudo_cut_method == 4:
            if (pseudo_radius / norm_a + ori_point[0]) > 1 or (pseudo_radius / norm_b + ori_point[1]) > 1 \
                or ((ori_point[2] - pseudo_radius / norm_c) < 0 and pseudo_cut_method == 1) \
                or ((pseudo_layers != 1000 and pseudo_layers > len(ori_layered_base_atoms)) and pseudo_cut_method == 4) \
                or ((pseudo_height != 1000 and (ori_point[2] - pseudo_height / norm_c) < 0) and pseudo_cut_method == 4):
                #expand the base_atoms and layered_base_atoms
                tmp_expand_size = int(max(pseudo_radius / norm_a + ori_point[0], pseudo_radius / norm_b + ori_point[1]))
                tmp_z_expand_is_num = False
                if pseudo_cut_method == 1:
                    tmp_z_expand_size = abs(ori_point[2] - pseudo_radius / norm_c)
                elif pseudo_cut_method == 2:
                    tmp_z_expand_size = -1
                elif pseudo_cut_method == 4:
                    if pseudo_height != 1000:
                        tmp_z_expand_size = abs(ori_point[2] - pseudo_height / norm_c)
                    elif pseudo_layers != 1000 and pseudo_layers > len(ori_layered_base_atoms):
                        tmp_z_expand_size = pseudo_layers - len(ori_layered_base_atoms)
                        tmp_z_expand_is_num = True
                    elif layers != 1000 and pseudo_layers <= len(ori_layered_base_atoms):
                        tmp_z_expand_size = -1
                base_atoms, layered_base_atoms = expand_base(ori_base_atoms, ori_layered_base_atoms, tmp_expand_size, tmp_z_expand_size, tmp_z_expand_is_num)
            else:
                base_atoms = ori_base_atoms
                layered_base_atoms = ori_layered_base_atoms
        elif pseudo_cut_method == 5 or pseudo_cut_method == 7:
            if pseudo_height == 1000 and pseudo_layers == 1000:
                raise ValueError('If you use method 5 or 7, you should input the pseudo height or layers.')
            if pseudo_height != 1000 and pseudo_layers != 1000:
                raise ValueError('You should only input pseudo height or layers, not both.')
            if pseudo_height != 1000 and (ori_point[2] - pseudo_height / norm_c) < 0:
                tmp_z_expand_size = abs(ori_point[2] - pseudo_height / norm_c)
                base_atoms, layered_base_atoms = expand_base(ori_base_atoms, ori_layered_base_atoms, -1, tmp_z_expand_size, False)
            elif pseudo_layers != 1000 and pseudo_layers > len(ori_layered_base_atoms):
                tmp_z_expand_size = pseudo_layers - len(ori_layered_base_atoms)
                tmp_z_expand_is_num = True
                base_atoms, layered_base_atoms = expand_base(ori_base_atoms, ori_layered_base_atoms, -1, tmp_z_expand_size, tmp_z_expand_is_num)
            else:
                base_atoms = ori_base_atoms
                layered_base_atoms = ori_layered_base_atoms
        elif pseudo_cut_method == 3 or pseudo_cut_method == 6:
            tmp_z_expand_size = -1
            tmp_z_expand_is_num = False
            base_atoms = ori_base_atoms
            layered_base_atoms = ori_layered_base_atoms

        #now we can cut the pseudo cluster
        #1. cut the pseudo cluster spherically with a input radius
        if pseudo_cut_method == 1:
            for i in range(len(base_atoms)):
                dis = direct_distance(base_atoms[i][1:4], ori_point, a, b, c, periodic=False)
                if dis < pseudo_radius:
                    pseudo_atoms.append(base_atoms[i])
        #2. cut the pseudo cluster into a cylinder with a input radius
        if pseudo_cut_method == 2 or pseudo_cut_method == 4:
            for i in range(len(base_atoms)):
                tmp_base_point = [base_atoms[i][1], base_atoms[i][2], 0.0]
                tmp_ori_point = [ori_point[0], ori_point[1], 0.0]
                dis = direct_distance(tmp_base_point, tmp_ori_point, a, b, c, periodic=False)
                if dis < pseudo_radius:
                    pseudo_atoms.append(base_atoms[i])
        #3. cut the pseudo cluster as a expanding polygon with a expanding atom number
        if pseudo_cut_method == 3 or pseudo_cut_method == 5:
            if pseudo_expand_num == 1000:
                raise ValueError('If you use method 3 or 5, you should input the pseudo_expand_num.')
            if cluster_major_method != 4:
                polygon, status = get_hex_or_sq(base_atoms, layered_base_atoms, ori_point, pseudo_expand_num, a, b, c, False)
            else:
                polygon, status = get_hex_or_sq(base_atoms, layered_base_atoms, ori_point, pseudo_expand_num, a, b, c, True)
            while not status:
                #means the surface may contains not sufficient atoms, expanding the base_atoms
                #if False, the return will be the polygon points, check the biggest one as a expand_num
                tmp_expand_size = 0
                for i in range(len(polygon)):
                    if int(round(abs(polygon[i][0]),0)) > tmp_expand_size:
                        tmp_expand_size = int(round(abs(polygon[i][0]),0))
                    if int(round(abs(polygon[i][1]),0)) > tmp_expand_size:
                        tmp_expand_size = int(round(abs(polygon[i][1]),0))
                base_atoms, layered_base_atoms = expand_base(ori_base_atoms, ori_layered_base_atoms, tmp_expand_size, -1, False)
                if cluster_major_method != 4:
                    polygon, status = get_hex_or_sq(base_atoms, layered_base_atoms, ori_point, pseudo_expand_num, a, b, c, False)
                else:
                    polygon, status = get_hex_or_sq(base_atoms, layered_base_atoms, ori_point, pseudo_expand_num, a, b, c, True)
            for i in range(len(base_atoms)):
                point = Point(tuple(base_atoms[i][1:3]))
                if polygon.contains(point):
                    pseudo_atoms.append(base_atoms[i])
        #4. cut the pseudo cluster expand from the second nearest atoms in to a new square in NaCl-like system
        if pseudo_cut_method == 6 or pseudo_cut_method == 7:
            if pseudo_expand_num == 1000:
                raise ValueError('If you use method 6 or 7, you should input the pseudo_expand_num.')
            polygon, status = get_second_expand(base_atoms, layered_base_atoms, ori_point, pseudo_expand_num, a, b, c)
            while not status:
                #means the surface may contains not sufficient atoms, expanding the base_atoms
                #if False, the return will be the polygon points, check the biggest one as a expand_num
                tmp_expand_size = 0
                for i in range(len(polygon)):
                    if int(round(abs(polygon[i][0]),0)) > tmp_expand_size:
                        tmp_expand_size = int(round(abs(polygon[i][0]),0))
                    if int(round(abs(polygon[i][1]),0)) > tmp_expand_size:
                        tmp_expand_size = int(round(abs(polygon[i][1]),0))
                base_atoms, layered_base_atoms = expand_base(ori_base_atoms, ori_layered_base_atoms, tmp_expand_size, -1, False)
                polygon, status = get_second_expand(base_atoms, layered_base_atoms, ori_point, pseudo_expand_num, a, b, c)
                only_xyz_output = True
            for i in range(len(base_atoms)):
                point = Point(tuple(base_atoms[i][1:3]))
                if polygon.contains(point):
                    pseudo_atoms.append(base_atoms[i])
        #5. fine-tuning of 2, cut the cylinder with input height ot layers
        if pseudo_cut_method == 4 or pseudo_cut_method == 5 or pseudo_cut_method == 7:
            if pseudo_height == 1000 and pseudo_layers == 1000:
                raise ValueError('If you use method 4, 5, or 7, you should input the pseudo height or layers.')
            if pseudo_height != 1000 and pseudo_layers != 1000:
                raise ValueError('You should only input pseudo height or layers, not both.')
            if pseudo_height != 1000:
                pseudo_atoms = [atom for atom in pseudo_atoms if abs(atom[3] - ori_point[2]) <= pseudo_height]
            elif pseudo_layers != 1000:
                layered_base_atoms.reverse()
                if pseudo_layers <= 0:
                    raise ValueError('The input layers should be larger than 0.')
                #remain the atom in selected layers
                target_layers_atoms = [atom for layer in layered_base_atoms[:pseudo_layers] for atom in layer]
                pseudo_atoms = [atom for atom in pseudo_atoms if atom in target_layers_atoms]
                layered_base_atoms.reverse()
        # now exclude the cluster atoms from the pseudo atoms
        pseudo_atoms = [atom for atom in pseudo_atoms if atom not in cluster_atoms]

    #cut a new charge cluster for the embedding, just as the cluster
    #the charge cluster will inherit the same ori_point as cluster
    charge_cut_method = file_control['charge_cutting_sub_method']
    charge_radius = file_control['charge_radius']
    charge_height = file_control['charge_height']
    charge_layers = file_control['charge_layers']

    charge_atoms = []
    if charge_cut_method != 1 and charge_cut_method != 4:
        raise ValueError('Charge cutting method only accept method 1 or 4')
    #assure charge radius or height or layers is bigger than cluster
    if charge_radius == 1000:
        raise ValueError('Radius should be input for charge cluster.')
    if charge_radius < radius:
        raise ValueError('Radius of charge cluster should be larger than the cluster.')
    if charge_cut_method == 4:
        if charge_height == 1000 and charge_layers == 1000:
            raise ValueError('If you use method 0.4, you should input the charge height or layers.')
        if charge_height != 1000 and charge_layers != 1000:
            raise ValueError('You should only input charge height or layers, not both.')
        if charge_height != 1000 and charge_height < height:
            raise ValueError('Height of charge cluster should be larger than the cluster.')
        if charge_layers != 1000 and charge_layers < layers:
            raise ValueError('Layers of charge cluster should be larger than the cluster.')
    

    if (charge_radius / norm_a + ori_point[0]) > 1 or (charge_radius / norm_b + ori_point[1]) > 1 \
        or ((ori_point[2] - charge_radius / norm_c) < 0 and charge_cut_method == 1) \
        or ((charge_layers != 1000 and charge_layers > len(ori_layered_base_atoms)) and charge_cut_method == 4) \
        or ((charge_height != 1000 and (ori_point[2] - charge_height / norm_c) < 0) and charge_cut_method == 4):
        #expand the base_atoms and layered_base_atoms
        tmp_expand_size = int(max(charge_radius / norm_a + ori_point[0], charge_radius / norm_b + ori_point[1]))
        tmp_z_expand_is_num = False
        if charge_cut_method == 1:
            tmp_z_expand_size = abs(ori_point[2] - charge_radius / norm_c)
        elif charge_cut_method == 4:
            if charge_height != 1000:
                tmp_z_expand_size = abs(ori_point[2] - charge_height / norm_c)
            elif charge_layers != 1000 and charge_layers > len(ori_layered_base_atoms):
                tmp_z_expand_size = charge_layers - len(ori_layered_base_atoms)
            elif layers != 1000 and charge_layers <= len(ori_layered_base_atoms):
                tmp_z_expand_size = -1
        base_atoms, layered_base_atoms = expand_base(ori_base_atoms, ori_layered_base_atoms, tmp_expand_size, tmp_z_expand_size, tmp_z_expand_is_num)
    else:
        base_atoms = ori_base_atoms
        layered_base_atoms = ori_layered_base_atoms
    #now we can cut the cluster
    #1. cut the cluster spherically with a input radius
    if charge_cut_method == 1:
        for i in range(len(base_atoms)):
            dis = direct_distance(base_atoms[i][1:4], ori_point, a, b, c, periodic=False)
            if dis < charge_radius:
                charge_atoms.append(base_atoms[i])
    #2. cut the cluster into a cylinder with a input radius
    if charge_cut_method == 4:
        for i in range(len(base_atoms)):
            tmp_base_point = [base_atoms[i][1], base_atoms[i][2], 0.0]
            tmp_ori_point = [ori_point[0], ori_point[1], 0.0]
            dis = direct_distance(tmp_base_point, tmp_ori_point, a, b, c, periodic=False)
            if dis < charge_radius:
                charge_atoms.append(base_atoms[i])
        if charge_height != 1000:
            charge_atoms = [atom for atom in charge_atoms if abs(atom[3] - ori_point[2]) <= height]
        elif charge_layers != 1000:
            if charge_layers <= 0:
                raise ValueError('The input layers should be larger than 0.')
            #remain the atom in selected layers
            target_layers_atoms = [atom for layer in layered_base_atoms[:charge_layers] for atom in layer]
            charge_atoms = [atom for atom in charge_atoms if atom in target_layers_atoms]

        #exclude the cluster atoms from the charge atoms
        charge_atoms = [atom for atom in charge_atoms if atom not in cluster_atoms]

        return cluster_atoms, pseudo_atoms, charge_atoms, "Embedding", pure_cluster_num

