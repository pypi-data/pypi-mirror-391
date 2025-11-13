#!/usr/bin/env python3

import os
import toml
import shutil
import argparse
from .find_dirs import *
from .jobs import *


'''

In this script, first we will read in input directory, output directory, and control file location. 
Then copy the input directory, regenerating the work directory.
Then according to the job type in control file, sub the task one by one to lsf.

'''






def main():
    parser = argparse.ArgumentParser(description='An embedding calculation tool from GGA@PBC to embedded hybrids')
    parser.add_argument('--input', type=str, dest='input_dir', required=True, help='Input directory location')
    parser.add_argument('--output', type=str, dest='output_dir', required=True, help='Output directory location')
    #parser.add_argument('-R', action='store_true', help='If set, will recursively search for input dirs in the input dir. Default is a single dir for calculation.')
    parser.add_argument('-f', type=str, dest='control_file', required=True, help='control file location, must set')
    parser.add_argument('-q', dest='Queue',
                        type = str,
                        default = 'xp72mc10',
                        help = "Queue names. 'xp72mc10' is default."
                        )
    parser.add_argument('-p', dest='Core_Number',
                        type = int,
                        default = 36,
                        help = "Core number used per node: 1/2/3/4/8/28...; 36 is default." 
                        )
    parser.add_argument('--xc', dest='xc_functional', 
                        type = str,
                        default = 'b3lyp',
                        help = "Set xc if REST input generation is needed; b3lyp is default."
                        )
    parser.add_argument('--basis', dest='basis_set',
                        type = str,
                        default = 'def2-SVP',
                        help = "Set basis if REST input generation is needed; def2-SVP is default."
                        )
    args = parser.parse_args()

    # resolve xc for maybe-existing empirical dispersion
    if '-' in args.xc_functional:
        if args.xc_functional == "r-xdh7-scc15":
            functional = "r-xdh7"
            vdw = "scc15"
        func_split = args.xc_functional.split('-')
        if func_split[-1] in ['d3', 'd3bj', 'd4']:
            functional = '-'.join(func_split[:-1])
            vdw = func_split[-1]
        else:
            functional = args.xc_functional
            vdw = None
    else:
        functional = args.xc_functional
        vdw = None

    if args.Queue == "amd9654":
        sub_queue = "AMD9654"
    elif args.Queue == "amd":
        sub_queue = "AMD"
    elif args.Queue == "gaussian":
        sub_queue = "Gaussian"
    elif args.Queue == "igor":
        sub_queue = "Igor"
    else:
        sub_queue = args.Queue

    #first load in the control file
    file_control = toml.load(args.control_file)
    #fill the unset parameters with default values
    if 'jobtype' not in file_control:
        raise ValueError('jobtype not set in control file')
    else:
        file_control['jobtype'] = round(file_control['jobtype'],1)
    if "force_xyz_output" not in file_control:
        #file_control['force_xyz_output'] = False
        # As DMET calculation is not available now, turn this default to be true.
        file_control['force_xyz_output'] = True
    if "check_base_num_consistant" not in file_control:
        file_control['check_base_num_consistant'] = False
    if 'separation_method' not in file_control:
        file_control['separation_method'] = 1
    if 'absorbate_atoms_num' not in file_control:
        file_control['absorbate_atoms_num'] = 0
    if 'cluster_cutting_major_method' not in file_control:
        raise ValueError('cluster_cutting_major_method not set in control file')
    elif type(file_control['cluster_cutting_major_method']) is not int:
        raise ValueError('cluster_cutting_major_method should be an integer in control file')
    if 'cluster_cutting_minor_method' not in file_control:
        raise ValueError('cluster_cutting_minor_method not set in control file')
    elif type(file_control['cluster_cutting_minor_method']) is not int:
        raise ValueError('cluster_cutting_minor_method should be an integer in control file')
    if 'cluster_radius' not in file_control:
        file_control['cluster_radius'] = 1000.0
    if 'cluster_height' not in file_control:
        file_control['cluster_height'] = 1000.0
    if 'cluster_layers' not in file_control:
        file_control['cluster_layers'] = 1000
    if 'cluster_expand_num' not in file_control:
        file_control['cluster_expand_num'] = 1000
    if 'cluster_ori_point' not in file_control:
        file_control['cluster_ori_point'] = [1000.0,1000.0,1000.0]
    if 'pseudo_cutting' not in file_control:
        file_control['pseudo_cutting'] = False
    if 'pseudo_cutting_sub_method' not in file_control and file_control['pseudo_cutting'] == True and \
        (int(file_control['jobtype']) == 2 or file_control['jobtype'] == 1.2):
        raise ValueError('pseudo_cutting_sub_method not set in control file')
    if type(file_control['pseudo_cutting_sub_method']) is not int and file_control['pseudo_cutting'] == True and \
        (int(file_control['jobtype']) == 2 or file_control['jobtype'] == 1.2):
        raise ValueError('pseudo_cutting_sub_method should be an integer in control file')
    if 'pseudo_radius' not in file_control and (int(file_control['jobtype']) == 2 or file_control['jobtype'] == 1.3 or file_control['jobtype'] == 1.4):
        file_control['pseudo_radius'] = 1000.0
    if 'pseudo_height' not in file_control and (int(file_control['jobtype']) == 2 or file_control['jobtype'] == 1.3 or file_control['jobtype'] == 1.4):
        file_control['pseudo_height'] = 1000.0
    if 'pseudo_layers' not in file_control and (int(file_control['jobtype']) == 2 or file_control['jobtype'] == 1.3 or file_control['jobtype'] == 1.4):
        file_control['pseudo_layers'] = 1000
    if 'pseudo_expand_num' not in file_control and (int(file_control['jobtype']) == 2 or file_control['jobtype'] == 1.3 or file_control['jobtype'] == 1.4):
        file_control['pseudo_expand_num'] = 1000
    if 'charge_cutting_sub_method' not in file_control and (int(file_control['jobtype']) == 2 or file_control['jobtype'] == 1.3 or file_control['jobtype'] == 1.4):
        raise ValueError('charge_cutting_sub_method not set in control file')
    if type(file_control['charge_cutting_sub_method']) is not int and (int(file_control['jobtype']) == 2 or file_control['jobtype'] == 1.3 or file_control['jobtype'] == 1.4):
        raise ValueError('charge_cutting_sub_method should be an integer in control file')
    if 'charge_radius' not in file_control and (int(file_control['jobtype']) == 2 or file_control['jobtype'] == 1.3 or file_control['jobtype'] == 1.4):
        file_control['charge_radius'] = 1000.0
    if 'charge_height' not in file_control and (int(file_control['jobtype']) == 2 or file_control['jobtype'] == 1.3 or file_control['jobtype'] == 1.4):
        file_control['charge_height'] = 1000.0
    if 'charge_layers' not in file_control and (int(file_control['jobtype']) == 2 or file_control['jobtype'] == 1.3 or file_control['jobtype'] == 1.4):
        file_control['charge_layers'] = 1000

    if 'ctrl_template' not in file_control and (file_control['jobtype'] == 1.2 or file_control['jobtype'] == 1.4):
        print("Warning: ctrl_template not set in control file, all other settings will be default values.")
        file_control['ctrl_template'] = ""


    #check if the input directory exists
    if not os.path.exists(args.input_dir):
        raise ValueError('Input directory does not exist')
    #create the output directory if not exists
    if os.path.exists(args.output_dir):
        #os.system('rm -rf ' + args.output_dir)
        shutil.rmtree(args.output_dir)
    os.makedirs(args.output_dir)
    regenerate_dirs(args.input_dir, args.output_dir)
    work_dirs = find_work_dirs(args.output_dir)
    # put dir with "clean" in front of others
    work_dirs.sort(key = lambda x: ("clean" not in x, x))
    global control_base_num
    if file_control['jobtype'] == 1.1 or file_control['jobtype'] == 1.3:
        for dir in work_dirs:
            job_1_1(dir, file_control)
    elif file_control['jobtype'] == 1.2:
        for dir in work_dirs:
            job_1_2(dir, file_control, args.Core_Number, functional=functional, basis=args.basis_set, vdw=vdw, pseudo_calc=False)
    elif file_control['jobtype'] == 1.4:
        for dir in work_dirs:
            job_1_2(dir, file_control, args.Core_Number, functional=functional, basis=args.basis_set, vdw=vdw, pseudo_calc=True)

    else:
        print("maybe this jobtype has not been implemented yet.")
        exit(0)


if __name__ == '__main__':
    main()
            


    

    
