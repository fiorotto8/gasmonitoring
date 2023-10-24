import cx_Oracle
import ROOT
import os
import time
import csv
from datetime import datetime
from datetime import timedelta
from array import array
import argparse
import sys
import pandas as pd
import tqdm
import numpy as np
import uproot
import awkward as ak
from itertools import zip_longest

def nparr(list):
    return np.array(list,dtype="d")

parser = argparse.ArgumentParser(description='Get DPID values in the selected time range for the selected DPID', epilog='Version: 1.0')
parser.add_argument('-deb','--debug',help='Enable some prints for debugging', action='store', default=None)
parser.add_argument('-dpid','--DPID',help='Bypass the DPID.csv file and tell the program the dpid of interest. Write the DPID separated only by a comma. No support for DPID names.', action='store', default=None)
parser.add_argument('-csv','--CSV',help='Set the input file for the DPID you want dafult is the DPID.csv file', action='store', default="DPID.csv")
parser.add_argument('-v','--verbose',help='Set verbose mode', action='store', default=None)
parser.add_argument('-days','--DAYS',help='indicate the number of DAYS in the past to fetch. Otherwise it uses setDate.txt file', action='store', default=None)
parser.add_argument('-n','--name',help='set a name to the output files', action='store', default=None)
parser.add_argument('-nc','--nocsv',help='enable it to ihnibit the csv writing', action='store', default=None)
args = parser.parse_args()

offsetpath="/afs/cern.ch/user/d/dfiorina/gasmonitoring/"
mainpath = offsetpath+"UnSyncro/"
# Check whether the specified path exists or not
isExist = os.path.exists(mainpath)
if not isExist:
   # Create a new directory because it does not exist
   os.makedirs(mainpath)


start_time=time.time()
if args.verbose is not None: print("Running Time:",time.time()-start_time)
#envirnemt variables in lxplus (?)
#in case put these in the bashrc
#export GEM_P5_DB_REPLICA_NAME_OFFLINE_MONITOR=cms_omds_adg
#export GEM_P5_DB_REPLICA_ACCOUNT_OFFLINE_MONITOR=CMS_COND_GENERAL_R/p3105rof@
dbName = os.getenv("GEM_P5_DB_REPLICA_NAME_OFFLINE_MONITOR")
dbAccount = os.getenv("GEM_P5_DB_REPLICA_ACCOUNT_OFFLINE_MONITOR")
#dbName, dbAccount=None, None
if dbName is None or dbAccount is None:
    passFile = open( offsetpath+"password.txt", "r" )
    dbName, dbAccount=passFile.read().splitlines()
#print(dbName, dbAccount)

#connect ot db and initialize cursor
db = cx_Oracle.connect( dbAccount+dbName )
cur = db.cursor()

#variables needed (?)
indOwner="CMS_GEM_PVSS_COND"
table="DIPSUBSCRIPTIONSFLOAT"
address=indOwner+"."+table

#get the start and stop date
if args.verbose is not None: print("Get Start and stop date")
if args.DAYS is None: 
    dateFile = open( offsetpath+"setDate.txt", "r" )
    dataStart, dataEnd=dateFile.read().splitlines()
else:
    dataEnd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dataStart = (datetime.now()- timedelta(days=int(args.DAYS))).strftime("%Y-%m-%d %H:%M:%S")
    #print(dataStart,dataEnd)
if args.debug is not None: print("Start date:",dataStart,"\nStop date",dataEnd)

"""
#get the DPID to read and their names
if args.verbose is not None: print("Get DPIDs list")
if args.DPID is None:
    DPIDfile=open( offsetpath+args.CSV, "r" )
    lines=DPIDfile.read().splitlines()
    DPIDnames, DPIDstring=lines[0].split(";"),lines[1].replace(";",",")
    DPIDlist=lines[1].split(";")
    DPIDlist=[int(x) for x in DPIDlist]
    if args.debug is not None: print("DPID Names:",DPIDnames,"\nDPID list",DPIDstring)
else:
    DPIDstring=args.DPID
    DPIDlist=args.DPID.split(",")
    DPIDlist=[int(x) for x in DPIDlist]
    DPIDnames=["test"+str(i) for i in range(len(DPIDstring))]
    if args.debug is not None: print("DPID Names:",DPIDnames,"\nDPID list:",DPIDstring)
"""

#get the DPID to read and their names
if args.verbose is not None: print("Get DPIDs list")
if args.DPID is None: 
    dfDPID=pd.read_csv(offsetpath+args.CSV,sep="\t")
    if args.debug is not None: print(dfDPID)
    DPIDnames=dfDPID[dfDPID.columns[2]].values
    DPIDlist=dfDPID[dfDPID.columns[1]].values
    #create the string tfor the query
    DPIDstring=str(DPIDlist[0])
    for i in range(len(DPIDlist)-1):
        DPIDstring=DPIDstring+","+str(DPIDlist[i-1])    
    if args.debug is not None: print("DPID Names:",DPIDnames,"\nDPID list",DPIDstring)
else:
    DPIDstring=args.DPID
    DPIDlist=args.DPID.split(",")
    DPIDlist=[int(x) for x in DPIDlist]
    DPIDnames=["test"+str(i) for i in range(len(DPIDstring))]
    if args.debug is not None: print("DPID Names:",DPIDnames,"\nDPID list:",DPIDstring)





#create the SQL query
query="SELECT CHANGE_DATE,DPID,VALUE FROM "+address
query=query + " WHERE DPID IN ("+DPIDstring+")"
query=query+" AND CHANGE_DATE >= "
query=query + "to_date( '"+dataStart+"', 'YYYY-MM-DD HH24:MI:SS')"
query=query+" AND CHANGE_DATE <= "
query=query + "to_date( '"+dataEnd+"', 'YYYY-MM-DD HH24:MI:SS')"
query=query+" ORDER BY CHANGE_DATE,DPID"
if args.debug is not None: print("Query is:", query)

#fetch all data from all the DPID you selected
if args.verbose is not None: print("Running Time:",time.time()-start_time,"\n","Performing Query")
result=cur.execute(query)
df=pd.DataFrame(result, columns=["time","DPID","value"])
#print(df)

#for the sake of saving the start and stop date spaces are replaced with underscores
dataStart,dataEnd=dataStart.replace(" ","_"),dataEnd.replace(" ","_")
dataStart,dataEnd=dataStart.replace(":","-"),dataEnd.replace(":","-")

#create file root
if args.verbose is not None: print("Running Time:",time.time()-start_time,"\n","Write ROOT")
if args.name is None:
    if args.DPID is None and args.CSV is "DPID.csv": file = uproot.recreate(mainpath+"allDPID_"+dataStart+"_"+dataEnd+'.root')
    elif args.DPID is None and args.CSV is not "DPID.csv": file = uproot.recreate(mainpath+"selectedDPID_"+dataStart+"_"+dataEnd+'.root')
    else: file = uproot.recreate(mainpath+"customDPID_"+dataStart+"_"+dataEnd+'.root')
else: file=uproot.recreate(mainpath+args.name+'.root')

cols,colsname=[],[]
#for i in tqdm.tqdm(range(len(DPIDlist))):  
for i in range(len(DPIDlist)):  
    if args.debug is not None: print("DPID:",DPIDlist[i])
    tempdf=df[df['DPID'] == DPIDlist[i]].reset_index()
    #print(len(tempdf))
    file[str(DPIDnames[i])] = {str(DPIDlist[i]): ak.zip({"time": nparr(tempdf["time"]), "value": nparr(tempdf["value"])})}
    cols.append(nparr(tempdf["time"]))    
    colsname.append("time_"+str(DPIDnames[i])+"_"+str(DPIDlist[i]))    
    cols.append(nparr(tempdf["value"]))    
    colsname.append("value_"+str(DPIDnames[i])+"_"+str(DPIDlist[i]))    

if args.nocsv is None:
    #create file csv
    if args.verbose is not None: print("Running Time:",time.time()-start_time,"\n","Write CSV")
    if args.name is None:
        if args.DPID is None and args.CSV is "DPID.csv": filecsv = mainpath+"allDPID_"+dataStart+"_"+dataEnd+'.csv'
        elif args.DPID is None and args.CSV is not "DPID.csv": filecsv = mainpath+"selectedDPID_"+dataStart+"_"+dataEnd+'.csv'
        else: filecsv = mainpath+"customDPID_"+dataStart+"_"+dataEnd+'.csv'
    else: filecsv = mainpath+args.name+'.csv'
        
    with open(filecsv,"w+") as f:
        writer = csv.writer(f)
        for values in zip_longest(*cols):
            writer.writerow(values)

    filec = pd.read_csv(filecsv)  
    filec.to_csv(filecsv, header=colsname, index=False)

    if args.verbose is not None: print("Running Time:",time.time()-start_time,"\n","Finished")
