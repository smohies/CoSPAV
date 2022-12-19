Compliance Server Pinger And Validator https://github.com/smohies/CoSPAV

# CoSPAV
## About:
This is a very simple Windows/Linux Python 3.11.0 script that receives 2 inputs, and has multiple configurable outputs. The main purpose is to compare a internal server inventory csv file against a csv file exported by RVTools and detecting discrepancies between them as well as pinging all servers and reporting failures.

This script requires no extra python libraries.

## Instructions:
1. Name the inventory csv as inv.csv and the rvtools csv as rvtools.csv.
2. Drop these csv files in the input folder.
3. Configure the config.ini as required. (config.ini details below)
4. Run the CoSPAV.py script. If there is a problem it will let you know, it may require input from you if this is the case.
5. Script should run without issues.
6. When finished, you can find the output in the output folder.

## Config.ini:
### InvFile
Set the default name for the inventory csv file. (Default = inv.csv)
### RVToolsFile
Set the default name for the RVTools csv file. (Default = rvtools.csv)
### CreateRVToolsSummary
This will create a csv file similar to rvtools.csv but only with data relevant to the inv.csv file (Data sharing IPs or Names), definetly a more human readable rvtools.csv.
### InvCSVHeader
Row number where the header is located on inv.csv (Starts at 0).
### InvCSVIPCol
Column number where the IPs are stored on inv.csv (Starts at 0).
### InvCSVNameCol
Column number where the server names are stored on inv.csv (Starts at 0).
### InvCSVHostNameCol
Column number where the server hostnames are stored on inv.csv (Starts at 0).
### InvCSVOSCol
Column number where the server OSs are located on inv.csv (Starts at 0).
### EmptyCountsAsDiscrepancy
Option to flag as a discrepancy a comparison where one of the inputs is empty. Can be True or False.
### PingServers
Option to run or not server pinging. Can be True or False.
### PingTimes
Set how many times to ping each server.
### OnlyShowFailedPings
Option to only show failed pings in the output, or also include succesfull ones with latency and success rate data.

## Output Files:
### duplicates.txt
Duplicate IPs or Hostnames found in inv.csv.
### hostname.csv
Server Hostname discrepancies between inv.csv and rvtools.csv.
### ip.csv
IP discrepancies between inv.csv and rvtools.csv.
### name.csv
Server Name discrepancies between inv.csv and rvtools.csv.
### os.csv
Server OS discrepancies between inv.csv and rvtools.csv.
### pings.csv
Server ping results.
### rvtoolsSummary.csv
A highly summarized version of the rvtools.csv file, only containing data relevant with the inv.csv file.
### rvtoolsSummaryFailedPings.csv
This is the same as rvtoolsSummary.csv but filtered as to only show data from failed pings.