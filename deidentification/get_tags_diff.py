import difflib
import pydicom
import os
import argparse

def get_tag_diff(path_raw, path_ano):
    """
    Return diff.txt file in the sam directory as path_raw which
    contain the tag difference between the 2 dcm 

    Args:
        path_dcm1 (str): path of the first dcm
        path_dcm2 (str): path of the second dcm
    """
    print(f"Check difference between :\n{path_raw} and\n{path_ano}\n")
    dcm1 = pydicom.read_file(path_raw)
    dcm2 = pydicom.read_file(path_ano)
    diff = difflib.ndiff(str(dcm1).splitlines(keepends=True),
                         str(dcm2).splitlines(keepends=True))
    
    diff1 = []
    diff2= []
    modif = []
    l = None
    readed_tags = []

    for i in diff:
        if ")" not in i or ")" not in i:
            continue
        tag = i[i.index('('): i.index(')')+1]
        txt = ""
        if tag not in readed_tags:
            readed_tags.append(tag)
            
            if i[0] == "-":
                txt = "Dcm1 only:"
                l = diff1
            elif i[0] == "+":
                txt = "Dcm2 only:"
                l = diff2
            i = txt + i[1:]
        elif tag in readed_tags and i[0]== "+":
            txt = "Value modification (dcm1 -> dcm2): "
            previous_value = l.pop(-1).split(': ')[-1].replace('\n', '')
            i = txt + tag + " " + previous_value + " -----> " + i.split(': ')[-1].replace('\n', '') + '\n'
            l = modif
        if txt != "":
            l.append(i)

    with open(os.path.join(os.path.dirname(path_raw), "diff.txt"), "w") as f:
        f.write(f'dcm1 = {path_raw}\n')
        f.write(f'dcm2 = {path_ano}\n\n\n')
        f.writelines(diff1)
        f.write('\n\n')
        f.writelines(diff2)
        f.write('\n\n')
        f.writelines(modif)
    
    print("Done\n")
    print("Output file : " + os.path.join(os.path.dirname(path_raw), "diff.txt"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-dcm1', required=True)
    parser.add_argument('-dcm2', default=True)
    args = parser.parse_args()
    get_tag_diff(args.dcm1, args.dcm2)

