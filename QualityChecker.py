import ROOT
import os
import time
import argparse
import sys
import pandas as pd
import tqdm
import numpy as np
import uproot
import glob
import shutil
from distutils.dir_util import copy_tree


def graphtime(x,y, y_string,x_string, color=4, markerstyle=22, markersize=1, write=True, name=None):
    if len(x)==0: plot=ROOT.TGraph()
    else: plot = ROOT.TGraph(len(x),  np.array(x  ,dtype="d")  ,   np.array(y  ,dtype="d"))
    if name is None: plot.SetNameTitle(y_string+" vs "+x_string,y_string+" vs "+x_string)
    else: plot.SetNameTitle(name, name)
    plot.GetXaxis().SetTitle(x_string)
    plot.GetYaxis().SetTitle(y_string)
    plot.SetMarkerColor(color)#blue
    plot.SetMarkerStyle(markerstyle)
    plot.SetMarkerSize(markersize)
    plot.GetXaxis().SetTimeDisplay(1)
    plot.GetXaxis().SetTimeFormat("#splitline{%y-%m-%d}{%H:%M:%S}%F1970-01-01 00:00:00")
    plot.GetXaxis().SetLabelSize(0.015)
    plot.GetXaxis().SetLabelOffset(0.015)
    if write==True: plot.Write()
    return plot

def nparr(list):
    return np.array(list,dtype="d")

def canvas(x,y,y_string,x_string,mean, std,xmin,xmax, size=800, color=4, markerstyle=22, markersize=1, leftmargin=0.15, rightmargin=0.05, name=None, savepath=None,write=True,writecan=False):
    if name is None: canname=y_string+" vs "+x_string
    else: canname=name
    can1=ROOT.TCanvas(canname, canname, size, size)    
    can1.SetFillColor(0);
    can1.SetBorderMode(0);
    can1.SetBorderSize(2);
    can1.SetLeftMargin(leftmargin);
    can1.SetRightMargin(rightmargin);
    can1.SetTopMargin(0.1);
    can1.SetBottomMargin(0.1);
    can1.SetFrameBorderMode(0);
    can1.SetFrameBorderMode(0);
    can1.SetFixedAspectRatio();
    #xmax=np.max(x)
    #xmin=np.min(x)
    
    print(xmax,xmin)
    
    pad=ROOT.TPad()
    histpad=pad.DrawFrame(xmin, mean-5*std, xmax, mean+5*std)
    histpad.GetXaxis().SetTitle(x_string)
    histpad.GetYaxis().SetTitle(y_string)
    histpad.GetXaxis().SetTimeDisplay(1)
    histpad.GetXaxis().SetTimeFormat("#splitline{%y-%m-%d}{%H:%M:%S}%F1970-01-01 00:00:00")
    histpad.GetXaxis().SetLabelSize(0.015)
    histpad.GetXaxis().SetLabelOffset(0.015)
    
    if len(x)==0: plot=ROOT.TGraph()
    else: plot = ROOT.TGraph(len(x),  np.array(x  ,dtype="d")  ,   np.array(y  ,dtype="d"))
    if name is None: plot.SetNameTitle(y_string+" vs "+x_string,y_string+" vs "+x_string)
    else: plot.SetNameTitle(name, name)
    plot.GetXaxis().SetTitle(x_string)
    plot.GetYaxis().SetTitle(y_string)
    plot.SetMarkerColor(color)#blue
    plot.SetMarkerStyle(markerstyle)
    plot.SetMarkerSize(markersize)
    plot.GetXaxis().SetTimeDisplay(1)
    plot.GetXaxis().SetTimeFormat("#splitline{%y-%m-%d}{%H:%M:%S}%F1970-01-01 00:00:00")
    plot.GetXaxis().SetLabelSize(0.015)
    plot.GetXaxis().SetLabelOffset(0.015)
    if write==True: plot.Write()

    #plot.GetYaxis.SetRangeUser(mean-2*std,mean+2*std)
    plot.Draw("SAME LP")
    
    #get min and max
    #ymax=ROOT.gPad.GetUymax()
    #ymin=ROOT.gPad.GetUymin()


    #print(xmin,xmax)

    can1.Update()
    #draw lines
    linem=ROOT.TLine(xmin,mean,xmax,mean)
    linem.SetLineColor(4)
    linem.SetLineWidth(2)
    linem.Draw("SAME")
    
    can1.Update()
    lineps=ROOT.TLine(xmin,mean+std,xmax,mean+std)
    lineps.SetLineColor(2)
    lineps.SetLineWidth(2)
    lineps.Draw("SAME")
    
    can1.Update()
    linens=ROOT.TLine(xmin,mean-std,xmax,mean-std)
    linens.SetLineColor(2)
    linens.SetLineWidth(2)
    linens.Draw("SAME")
    
    can1.Update()
    line3ps=ROOT.TLine(xmin,mean+3*std,xmax,mean+3*std)
    line3ps.SetLineColor(3)
    line3ps.SetLineWidth(2)
    line3ps.Draw("SAME")
    
    can1.Update()
    line3ns=ROOT.TLine(xmin,mean-3*std,xmax,mean-3*std)
    line3ns.SetLineColor(3)
    line3ns.SetLineWidth(2)
    line3ns.Draw("SAME")
    
    p=ROOT.TPaveText(.6,.8,.95,.9,"NDC")
    p.AddText("Blue: Baseline average")
    p.AddText("Red: 1 #sigma baseline")
    p.AddText("Green: 3 #sigma baseline")
    t1=ROOT.TText = p.GetLineWith("Blue")
    t1.SetTextColor(4)
    t2=ROOT.TText = p.GetLineWith("Red")
    t2.SetTextColor(2)
    t3=ROOT.TText = p.GetLineWith("Green")
    t3.SetTextColor(3)
    p.SetFillStyle(0)
    p.Draw("SAME")
    
    p1=ROOT.TPaveText(.15,.85,.6,.9,"NDC")
    p1.AddText(name)
    p1.SetFillStyle(0)
    p1.Draw("SAME")
    
    if writecan==True: can1.Write()
    if savepath is not None: can1.SaveAs(savepath+canname+".png")
    return can1

parser = argparse.ArgumentParser(description='Get a dataset and see if the values are outside nominal values contained in selected baseline configuration', epilog='Version: 1.0')
parser.add_argument('-bf','--baselinefile',help='give only the name of the input .csv file, it should be stored in the OutputBaselines/ folder', action='store', default="results_Baseline2023.csv")
parser.add_argument('-if','--inputfile',help='give only the name of the input .root file, it should be stored in the UnSyncro/ folder. If None the latest run will be used', action='store', default=None)
parser.add_argument('-v','--verb',help='Enable verbose', action='store', default=None)
args = parser.parse_args()


if args.verb is None:
    #ROOT.gSystem.RedirectOutput("/dev/null")
    ROOT.gErrorIgnoreLevel = 6001
    #redirect root ooutput lines to log file
    ROOT.gSystem.RedirectOutput("/afs/cern.ch/user/d/dfiorina/gasmonitoring/QualityCheckerlog.txt", "a")



#select input file
#if file is not passed as an argument the script will take the most recent one (exepted Baseline*)
if args.inputfile is not None:
    inFile="UnSyncro/"+args.inputfile
else:
    # absolute path to search all text files inside a specific folder
    path = '/afs/cern.ch/user/d/dfiorina/gasmonitoring/UnSyncro/*.root'
    files = glob.glob(path)
    #remove element that have baseline in the name
    files=[x for x in files if "Baseline" not in x]
    ModTimes=[]
    for f in files: ModTimes.append(os.path.getmtime(f))
    inFile=files[np.argmax(ModTimes)]

if args.verb is not None: print("input file is:", inFile)

#open and read baseline
names, means, stds=[],[],[]
bf=open("/afs/cern.ch/user/d/dfiorina/gasmonitoring/OutputBaselines/"+args.baselinefile,"r")
for x in bf:
    a=x.split(";")
    names.append(a[0])
    means.append(float(a[1]))
    stds.append(float(a[2].strip()))   
bf.close()
#print(names, means, stds)

#get arrays from input root
file = uproot.open(inFile)
trees=file.keys()
timearrs,arrays=[],[]
for t in trees:
    timearrs.append(file[t].values()[0].array(library="np"))
    arrays.append(file[t].values()[1].array(library="np"))


#check create fodlers
latestPath="/afs/cern.ch/user/d/dfiorina/gasmonitoring/QuickAnalysed/latest/"
thispath="/afs/cern.ch/user/d/dfiorina/gasmonitoring/QuickAnalysed/"+inFile[52:-5]+"/"
print(thispath)

#check is lastest exists if not create it if yes empty it
isExist = os.path.exists(latestPath)
if not isExist:
   os.makedirs(latestPath)
else:
    files =  os.listdir(latestPath)
    #print(files)
    for f in files:
        os.remove(latestPath+f)

#print(inFile[52:])

#open output root
main=ROOT.TFile(latestPath+"Anal_"+inFile[52:],"RECREATE")
f=open(latestPath+"log.txt","w")
f.write("DPID\tFractions 1sigma out\tFractions 3sigma out\n")
#find xmax and xmin
xmins,xmaxs=[],[]
for times in timearrs:
    if len(times)!=0:
        xmins.append(np.min(times))
        xmaxs.append(np.max(times))
xmin,xmax=np.min(xmins)*1E-9,np.amax(xmaxs)*1E-9
#print(xmin,xmax)
for i in range(len(names)):
    arrlen=len(nparr(timearrs[i]))
    if arrlen!=0: 
        canvas( nparr(timearrs[i])*1E-9,nparr(arrays[i]),names[i],"UTC time (YY-mm-dd HH:MM:SS)",means[i],stds[i],xmin,xmax,savepath=latestPath,name=names[i]+inFile[52:-5],writecan=True)
        
        out1=np.sum(np.abs(arrays[i]-means[i])>+stds[i])/arrlen
        out3=np.sum(np.abs(arrays[i]-means[i])>3*stds[i])/arrlen
        #print(out1,out3)
        
        f.write(names[i]+"\t"+str(out1)+"\t"+str(out3)+"\n")

isExist = os.path.exists(thispath)
if not isExist:
    shutil.copytree(latestPath, thispath)
else:
    print("Folder",thispath, "already exists, not updated")

#read webseite path
f=open("/afs/cern.ch/user/d/dfiorina/gasmonitoring/websitePath.txt","r")
webFolder=f.readline()
#remove everything from eos path
files = glob.glob(webFolder+'/*')
for f in files:
    os.remove(f)

#copy altes in here
copy_tree(latestPath, webFolder)
shutil.copy("/afs/cern.ch/user/d/dfiorina/gasmonitoring/index.php", webFolder)

print("DONE!!!")
