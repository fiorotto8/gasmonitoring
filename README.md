# 0 General notes
Data fetching and Quality Checking have to be perfomed on a lxplus machine. Currently everything is automated on Davide lxplus

# 1 Data fetching from the database -WORKS ON LXPLUS ONLY-
### Configure GitLab on your machine
```
git config --global user.name <cern user>
git config --global user.email <cern mail>
```
clone the directory, user and pass are necessary
```
git clone https://gitlab.cern.ch/gemmonitoring/gasmonitoring.git
```
### Setup a cron job on LXPLUS 
in ~/.bashrc add:
```
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```
launch ```acrontab -e``` and write in format <minute hour day-of-month month day-of-week command>
example, run every Monday at midnight the FetchGas_NoSyncro.py script with option to fetch last week data:
```
00 00 * * 1 lxplus python3 /afs/cern.ch/user/d/dfiorina/gasmonitoring/FetchGas_NoSyncro.py -days 7
```
-minute hour day-of-month month day-of-week command-
This is currently implemented on Davide lxplus
To check the current cron job on your lxplus type ```acrontab -l```
NB--> if you use cronjob remember that:
 - [ ] the environmental variables cannot be fetched for example os.getenv() cannot be used and you need other ways to get them. However, I put on my lxplus the password.txt file with the credential for the database.
 - [ ] all the directories and files should be given their complete path e.g.:"/afs/cern.ch/user/d/dfiorina/gasmonitoring/..."
 
However, after recovering the data, they must be analyzed with the Quality Checker routine (QualityChecker.py) to have the possibility of publishing it on the web page. In this case the cronjob must be modified by adding the analysis part. Finally, you can optionally run the routine that analyzes the data synchronously (FetchGas_YesSyncro.py) for any further analysis.
To do all this just edit a (i.e. myacrontab) file with the following lines:

00 00 * * 1 lxplus python3 /afs/cern.ch/user/d/dfiorina/gasmonitoring/FetchGas_NoSyncro.py -days 7

00 00 * * 1 lxplus python3 /afs/cern.ch/user/d/dfiorina/gasmonitoring/FetchGas_YesSyncro.py -days 7

00 05 * * 1 lxplus python3 /afs/cern.ch/user/d/dfiorina/gasmonitoring/QualityChecker.py

(obviously you have to change the address directory with your name)

And then just:     “acrontab < myacrontab” to start the cronjob on lxplus


### Local mount a remote repository (DEPRECATED!!)

The data has to be fetched from lxplus. 
The usual option is to mount a remote directory on the local system with `sshfs`. However, this requires a passwordless and continuous login to lxplus to operate well.
However, CERN is not allowing ssh key usage for passwordless login. The only way is to use Kerberos but the token only lasts for a maximum of 7 days.
There are 2 remaining options to sync the lxplus folder:
- use `sshpass` package that reads the password that is written somewhere on the PC. **Illegal option and really not recommended since this is a shared workspace**
- Use `rync` every week to synchronize the data from lxplus manually
*Obviously we use the second one*


### ACCESS TO DATABASE 
To have access write on your ~/.bashrc these rows:
```
export GEM_P5_DB_REPLICA_NAME_OFFLINE_MONITOR=<ask>
export GEM_P5_DB_REPLICA_ACCOUNT_OFFLINE_MONITOR=<ask>
```
However, the automatic codes read the user and pass for the database from the `password.txt` file which is only present on personal lxplus machines.

### INSTALL REQUIREMENTS
run this on your LXPLUS
```
pip3 install --user -r requirements.txt
```

## DOWNLOAD THE DATA with `FetchGas_*.py`
Start and Stop dates are read from the file:  "setDate.txt"
First row is the start date and the last row is the end data
The format is YYYY-MM-DD HH24:MI:SS

You have 3 ways to select the DPID to fetch:
- [ ] pass no argument to the .py: this will read from the DPID.csv file. By default, this file contains already all the DPID related to GAS
- [ ] pass a custom .csv via the `-csv` argument. Note that the format should be the same as the DPID.csv
- [ ] pass custom DPID values by the `-dpid` argument. No support for DPID names

You also have 2 ways to save data:

- [ ] FetchGas_NoSyncro.py just queries the database and creates 2 output files with the results. One .csv file with the columns related to the time and value of the DPID and one .root file with one TTree for each DPID. The output files are stored in ./UnSyncro_data

- [ ] FetchGas_YesSyncro.py works in the same way but it synchronizes all the data among them. The outputs are stored in ./Syncro_data they are a .csv with one time columns (all the syncro times) and all the DPID columns, and a .root file with one TTree with the syncro time and all the DPID.

# 2 Generate Baseline data for future analysis

`GenerateBaselineInfo.py` gets as an argument a .root file (which has to be stored in `UnSyncro` folder) considered to be a good baseline for future analysis. Be careful to select a good dataset for such baseline calculation. For example today (12/04/2023) I found that the period *01/04/2022-->31/08/2022* is a good baseline. The output file is a `.csv` (in the folder `OutputBaselines`) file where every row contains the name of the DPID, the average value and the standard deviation; separated by a semicolumn.
For 2023 I found the period for Baseline to be *11/02/2023-->13/04/2023*.

(ex. python3 GenerateBaselineInfo.py -f allDPID_2023-07-01_00-00-00_2023-07-10_00-00-00.root)

# 3 Simple Quality Checker
The script `QualityChecker.py` takes as input a baseline `.csv` and a `.root` to be analyzed. The script works also without input argument since it takes the default baseline and as an input file, it takes the last modified `.root` file contained in the `UnSyncro/` folder (except the ones that contain Baseline in the name).
The output are stored in the `QuickAnlaysed` directory. Every analysed set has his own folder containing the `.root` files and the `.png`. Every DPID has a `.png` file where the points of the week are plotted along with a blue line (the baseline mean) two red lines (one signa out mean from baseline) and two green lines (three seigma out mean from baseline).
The output are also copied in a `/eos` directory used for storing file for a personal CERN webpage.

(ex. python3 QualityChecker.py -bf results_Baseline2024.csv -if allDPID_2023-07-01_00-00-00_2023-07-10_00-00-00.root )


## 3.1 Create web content folder for personal website
https://cernbox.docs.cern.ch/advanced/web-pages/personal_website_content/#create-web-content-folder-for-personal-website
-From cernbox --> Share your folder <fodler_name> with a:wwweos (wwweos is the service account).
-Ensure that the permission ‘can modify’ is not ticked.

Create with the wizard your site: https://webservices-portal.web.cern.ch/webeos

For this repository everything is setup on Davide lxplus, you can access the latest plot here https://gemgasweeklyplots.web.cern.ch/

