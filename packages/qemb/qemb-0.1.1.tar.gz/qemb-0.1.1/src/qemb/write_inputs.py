import os


def write_rest_input(xyz,functional,basis,vdw,charge=0,mult=1,proc=28,ctrl_template="",pseudo_calc=False, **kwargs):
    charge_dict = {
        "F": -1.0, "Cl": -1.0, "Br": -1.0, "I": -1.0, "O": -2.0, "S": -2.0, "Se": -2.0, "Te": -2.0, 
        "Li": 1.0, "Na": 1.0, "K": 1.0, "Rb": 1.0, "Cs": 1.0, "Be": 2.0, "Mg": 2.0, "Ca": 2.0, "Sr": 2.0, "Ba": 2.0
    }
    if pseudo_calc:
        pseudo_xyz = kwargs.get('pseudo_xyz')
        charge_xyz = kwargs.get('charge_xyz')
    # check if pseudo_xyz file exists, if not, set a flag to False
    if pseudo_calc and os.path.exists(pseudo_xyz):
        with_pseudo = True
    else:
        with_pseudo = False
    # Resolve the input template
    if len(ctrl_template) != 0:
        template_lines = ctrl_template.splitlines()

    with open("ctrl.in","w") as f:
        f.write('[ctrl]\n')
        if len(ctrl_template) != 0:
            for line in template_lines:
                f.write('\t' + line + '\n')
        f.write('\tnum_threads = ' + str(proc) + '\n')
        f.write('\txc = "'+ functional + '" \n')
        if functional == "r-xdh7" and vdw == "scc15":
            f.write('\tpost_ai_correction = "scc15" \n')
            f.write('\tfrozen_core_postscf = 21\n')
            f.write('\tfrequency_points= 100\n')
        elif vdw != None:
            f.write('\tempirical_dispersion = "' + vdw + '"\n')
        f.write('\tbasis_path = "/opt/rest_workspace/rest/basis-set-pool/'+ basis + '"\n')
        f.write('\tcharge = ' + str(float(charge)) + '\n')
        f.write('\tspin = ' + str(float(mult)) + '\n')
        if mult == 1:
            f.write('\tspin_polarization = false\n')
        else:
            f.write('\tspin_polarization = true\n')
        f.write("\n")
        f.write("\n")
        f.write('[geom]\n')
        with open(xyz,"r") as f2:
            #read from the third line to the last two line, and write to the toml file
            lines = f2.readlines()
            name_line = lines[1].strip()
            line1 = lines[2:]
        f.write('\tname = "' + name_line + '"\n')
        f.write('\tunit = "angstrom"\n')
        f.write("\tposition = '''\n")
        for line in line1:
            f.write("\t\t")
            f.write(line)
        f.write("\t'''\n")
        f.write("\n")
        
        if pseudo_calc:
            f.write("\tghost = \'\'\'\n")
            if with_pseudo:
                with open(pseudo_xyz, "r") as f2:
                    pseudo_lines = f2.readlines()[2:]
                tmp_pseudo_lines = []
                for line in pseudo_lines:
                    line = line.split()
                    tmp_pseudo_lines.append(["potential", str(line[0])+"_ghost.json", str(line[1]), str(line[2]), str(line[3])])
                for line in tmp_pseudo_lines:
                    f.write("\t\t")
                    f.write("    ".join(line))
                    f.write("\n")
            with open(charge_xyz, "r") as f2:
                charge_lines = f2.readlines()[2:]
            tmp_charge_lines = []
            for line in charge_lines:
                line = line.split()
                if line[0] in charge_dict.keys():
                    tmp_charge_lines.append(["point charge", str(charge_dict[line[0]]), str(line[1]), str(line[2]), str(line[3])])
            for line in tmp_charge_lines:
                f.write("\t\t")
                f.write("    ".join(line))
                f.write("\n")
            f.write("\t\'\'\'\n")
        f.write("\n")
            
