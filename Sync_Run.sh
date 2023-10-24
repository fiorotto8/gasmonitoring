#!/bin/bash
#to be runned in some local machine to fetch the runs already done
rsync -azvP dfiorina@lxplus.cern.ch:~/gasmonitoring/Syncro dfiorina@lxplus.cern.ch:~/gasmonitoring/UnSyncro dfiorina@lxplus.cern.ch:~/gasmonitoring/OutputBaselines dfiorina@lxplus.cern.ch:~/gasmonitoring/QuickAnalysed .
