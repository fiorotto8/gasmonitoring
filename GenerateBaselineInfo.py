import ROOT
import os
import time
import argparse
import sys
import pandas as pd
import tqdm
import numpy as np
import uproot

parser = argparse.ArgumentParser(description='From a baseline dataset generate the baseline file with average and std for every DPID', epilog='Version: 1.0')
parser.add_argument('-f','--file',help='give only the name of the input .root file. The file should be in the UnSyncro/ folder', action='store', default="Baseline2023.root")
args = parser.parse_args()

file = uproot.open("./UnSyncro/"+args.file)
trees=file.keys()
names, means, stds, lengs=[],[],[],[]
for t in trees:
    array=file[t].values()[1].array(library="np")
    lentemp=len(array)
    if lentemp!=0:
        names.append(t[:-2])
        means.append(np.mean(array))
        stds.append(np.std(array))
        lengs.append(len(array))

# Check whether the specified path exists or not
folder="OutputBaselines"
isExist = os.path.exists(folder)
if not isExist:
   # Create a new directory because it does not exist
   os.makedirs(folder)
###########################################################################################
f = open(folder+"/results_"+args.file[:-5]+".csv", "w")
for i in range(len(names)):
    #print(names[i], means[i], stds[i])
    f.write(names[i]+";"+ str(means[i])+";"+ str(stds[i])+"\n")
f.close()
############################################################################################
