#!/usr/bin/env python3

import difflib
import pydicom
import os, re
import argparse

def get_tag_diff(path_raw, path_ano, outpath=None):
    """
    Return diff.txt file in the sam directory as path_raw which
    contain the tag difference between the 2 dcm 

    Args:
        path_dcm1 (str): path of the first dcm (ref)
        path_dcm2 (str): path of the second dcm (current)
        outpath (str): path of the diff_file
    """
    print(f"Check difference between :\n{path_raw} and\n{path_ano}\n")
    dcm_ref = pydicom.read_file(path_raw)
    dcm_current = pydicom.read_file(path_ano)
    diff = difflib.ndiff(str(dcm_ref).splitlines(keepends=True),
                         str(dcm_current).splitlines(keepends=True))
    
    diff_from_dcm1 = []
    diff_from_dcm2 = []
    global_modif = []
    current_line_diff = None
    previous_tag = None
    previous_sign =  None

    for i in diff:
        if "(" not in i or ")" not in i:
            continue
        tag = i[i.index('('): i.index(')')+1]
        txt = ""

        # tag present in only one dcm
        if tag != previous_tag:
            if i[0] == "-":
                txt = "Dcm1 only:"
                current_line_diff = diff_from_dcm1
            elif i[0] == "+":
                txt = "Dcm2 only:"
                current_line_diff = diff_from_dcm2
            line = txt + i[1:]
        # between 2 diff lines : same tag + remove from first line and add to second -> value modification
        elif tag == previous_tag and i[0] != previous_sign:
            line = ""
            txt = f"Modification (dcm1 -> dcm2): {tag}"
            previous_elem = current_line_diff.pop(-1)
            # check tag name
            pattern = "\) [A-Z|[].* [A-Z]{2}:"
            previous_name = re.search(pattern, previous_elem).group()[2:-3].replace('  ', '')
            current_name = re.search(pattern, i).group()[2:-3].replace('  ', '')
            if current_name != previous_name:
                line += txt + f'\tName modification\t {previous_name} ---> {current_name}\n'

            # check tag value
            previous_value = previous_elem.split(': ')[-1].replace('\n', '')
            current_value = i.split(': ')[-1].replace('\n', '') 
            if previous_value != current_value:
                line += txt + f'\tValue modification\t {previous_value}  --->  {current_value}\n'
            current_line_diff = global_modif

        if txt != "":
            previous_tag = tag
            previous_sign = i[0]
            current_line_diff.append(line)

    if not outpath:
        outpath = os.path.join(os.path.dirname(path_raw), "diff.txt")
    with open(outpath, "w") as f:
        f.write(f'dcm1 = {path_raw}\n')
        f.write(f'dcm2 = {path_ano}\n\n\n')
        f.writelines(diff_from_dcm1)
        f.write('\n\n')
        f.writelines(diff_from_dcm2)
        f.write('\n\n')
        f.writelines(global_modif)
    
    print("Done\n")
    print(f"Output file : {outpath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--first', required=True)
    parser.add_argument('-s', '--second', required=True)
    parser.add_argument('-o', '--outpath', required=False)
    args = parser.parse_args()
    get_tag_diff(args.first, args.second, args.outpath)
