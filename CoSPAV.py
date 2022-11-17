import os
import os.path
import re
import csv
import subprocess
import platform
from configparser import ConfigParser

config = ConfigParser()

def validate_file(filename, description):
    folder = "./input/"
    filepath = os.path.join(folder, filename)
    while True:
        if not os.path.isdir(folder):
            os.mkdir(folder)
        if not os.path.isfile(filepath):
            print(f"{filename} not found in ./input/, enter the {description} CSV filename:")
            filename = input()
        else:
            break
    return filepath

def ping(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    ping_times = config.get("DEFAULT", "PingTimes")
    command = ["ping", param, ping_times, host]
    ping_result = subprocess.run(command, capture_output=True)
    if ping_result.returncode == 0:
        try:
            result = re.search(r".*\((\d*% loss)\).*Average = (\d*ms).*", str(ping_result.stdout))
            return f"{result.group(1)} @ {result.group(2)}"
        except:
            result = re.search(r".*(Reply from [0-9.]*:[a-zA-Z 0-9]*.).*",str(ping_result.stdout))
            return result.group(1)
    else:
        return "FAIL"
    
def write_csv(filename, tgt_list):
    folder = "./output/"
    filepath = os.path.join(folder, filename)
    if not os.path.isdir(folder):
        os.mkdir(folder)
    with open(filepath, "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        for row in tgt_list:
            writer.writerow(row)
            
def write_txt(filename, tgt_list):
    folder = "./output/"
    filepath = os.path.join(folder, filename)
    if not os.path.isdir(folder):
        os.mkdir(folder)
    with open(filepath, "w") as dups:
        for item in tgt_list:
            dups.write(f"{item}\n")

def clear_output_folder():
    files = ["duplicates.txt", "hostname.csv", "ip.csv", "name.csv", "os.csv", "pings.csv", "rvtoolsSummary.csv", "rvtoolsSummaryFailedPings.csv"]
    folder = "./output/"
    if os.path.isdir(folder):
        for file in files:
            filepath = os.path.join(folder, file)
            if os.path.isfile(filepath):
                print(f"Deleting old file {filepath}")
                os.remove(filepath)
        
def main():
    clear_output_folder()
    print(f"Loading config.ini")
    config.read("config.ini")
    inv_csv_filename = validate_file(config.get("DEFAULT", "InvFile"), "EPN IAPISE Inventory")
    rvtools_csv_filename = validate_file(config.get("DEFAULT", "RVToolsFile"), "RVTools")
  
    print(f"Files {inv_csv_filename} and {rvtools_csv_filename} found!")
    
    server_ips = {}
    server_names = {}
    duplicates = []
    rvtools_summary = []
    inv_csv_header = config.getint("DEFAULT", "InvCSVHeader")
    inv_csv_ip_col = config.getint("DEFAULT", "InvCSVIPCol")
    inv_csv_name_col = config.getint("DEFAULT", "InvCSVNameCol")
    inv_csv_hostname_col = config.getint("DEFAULT", "InvCSVHostnameCol")
    inv_csv_os_col = config.getint("DEFAULT", "InvCSVOSCol")
    
    # Import inv csv data
    print(f"Loading {inv_csv_filename} data")
    with open(inv_csv_filename, "r") as inv_csv_file:
        inv_csv = csv.reader(inv_csv_file)
        line_count = 0
        while line_count <= inv_csv_header:
            next(inv_csv)
            line_count += 1
        for row in inv_csv:
            replaced_row_ip = row[inv_csv_ip_col].replace("Â", "").strip()
            if replaced_row_ip in server_ips:
                if not replaced_row_ip in duplicates:
                    duplicates.append(replaced_row_ip)
            else:
                server_ips[replaced_row_ip] = [row[inv_csv_name_col].replace("Â", "").strip(), "", False, row[inv_csv_hostname_col].replace("Â", "").strip(), "", False, row[inv_csv_os_col].replace("Â", "").strip(), "", False]
            if row[inv_csv_name_col]:
                replaced_row_name = row[inv_csv_name_col].replace("Â", "").strip()
                if replaced_row_name in server_names:
                    if not replaced_row_name in duplicates:
                        duplicates.append(replaced_row_name)
                else:
                    server_names[replaced_row_name] = [row[inv_csv_ip_col].replace("Â", "").strip(), "", False]
    
    # Import tool csv data
    print(f"Loading {rvtools_csv_filename} data")
    with open(rvtools_csv_filename, "r") as rvtools_csv_file:
        rvtools_csv = csv.DictReader(rvtools_csv_file)
        for row in rvtools_csv:
            if row["Primary IP Address"] in server_ips:
                server_ips[row["Primary IP Address"]][1] = row["VM"]
                server_ips[row["Primary IP Address"]][4] = row["DNS Name"]
                if row["OS according to the VMware Tools"]:
                    server_ips[row["Primary IP Address"]][7] = row["OS according to the VMware Tools"]
                else:
                    server_ips[row["Primary IP Address"]][7] = row["OS according to the configuration file"]
            if row["VM"] in server_names:
                server_names[row["VM"]][1] = row["Primary IP Address"]
            if row["Primary IP Address"] in server_ips or row["VM"] in server_names:
                rvtools_summary.append([row["Primary IP Address"], row["VM"], row["DNS Name"], row["OS according to the VMware Tools"], row["OS according to the configuration file"], row["Powerstate"], row["Heartbeat"]])
    if config.getboolean("DEFAULT", "CreateRVToolsSummary"):
        print("Exporting rvtools-summary.csv")
        rvtools_summary = sorted(rvtools_summary, key=lambda x: x[0])
        rvtools_summary.insert(0, ["IP", "VM Name", "DNS Name", "OS according VMWare", "OS according config", "Powerstate", "Heartbeat"])
        write_csv("rvtoolsSummary.csv", rvtools_summary)
                    
    print(f"Loaded {len(server_ips)} entries for server_ips and {len(server_names)} entries for server_names")
    print("Searching for discrepancies")
    
    # Find discrepancies in server_ips
    if config.getboolean("DEFAULT", "EmptyCountsAsDiscrepancy"):
        for key in server_ips:
            if server_ips[key][0] != server_ips[key][1]:
                server_ips[key][2] = True
            if server_ips[key][3] != server_ips[key][4]:
                server_ips[key][5] = True
            if server_ips[key][6] != server_ips[key][7]:
                server_ips[key][8] = True
    else:
        for key in server_ips:
            if server_ips[key][0] != server_ips[key][1] and server_ips[key][0] and server_ips[key][1]:
                server_ips[key][2] = True
            if server_ips[key][3] != server_ips[key][4] and server_ips[key][3] and server_ips[key][4]:
                server_ips[key][5] = True
            if server_ips[key][6] != server_ips[key][7] and server_ips[key][6] and server_ips[key][7]:
                server_ips[key][8] = True
    
    # Find discrepancies in server_names
    if config.getboolean("DEFAULT", "EmptyCountsAsDiscrepancy"):
        for key in server_names:
            if server_names[key][0] != server_names[key][1]:
                server_names[key][2] = True
    else:
        for key in server_names:
            if server_names[key][0] != server_names[key][1] and server_names[key][0] and server_names[key][1]:
                server_names[key][2] = True
    
    # List discrepancies in names
    name_diffs = [["IP (INV)", "INV NAME", "RVT NAME"]]
    for key in server_ips:
        if server_ips[key][2] == True:
            name_diffs.append([key, server_ips[key][0], server_ips[key][1]])
            
    # List discrepancies in hostnames
    hostname_diffs = [["IP (INV)", "INV HOSTNAME", "RVT HOSTNAME"]]
    for key in server_ips:
        if server_ips[key][5] == True:
            hostname_diffs.append([key, server_ips[key][3], server_ips[key][4]])
            
    # List discrepancies in os
    os_diffs = [["IP (INV)", "INV OS", "RVT OS"]]
    for key in server_ips:
        if server_ips[key][8] == True:
            os_diffs.append([key, server_ips[key][6], server_ips[key][7]])
    
    # List discrepancies in ips
    ip_diffs = [["NAME (INV)", "INV IP", "RVT IP"]]
    for key in server_names:
        if server_names[key][2] == True:
            ip_diffs.append([key, server_names[key][0], server_names[key][1]])
            
    print(f"{len(name_diffs)}/{len(server_ips)} server name mismatches")
    print(f"{len(hostname_diffs)}/{len(server_ips)} server hostname mismatches")
    print(f"{len(os_diffs)}/{len(server_ips)} server OS mismatches")
    print(f"{len(ip_diffs)}/{len(server_names)} server IP mismatches")
    if duplicates:
        print(f"{len(duplicates)} duplicates found in inv.csv")
    print("Exporting mismatched data (name.csv, hostname.csv, os.csv, ip.csv)")
    write_csv("name.csv", name_diffs)
    write_csv("hostname.csv", hostname_diffs)
    write_csv("os.csv", os_diffs)
    write_csv("ip.csv", ip_diffs)
    print("Exporting duplicates.txt")
    write_txt("duplicates.txt", sorted(duplicates))
    print("Creating servers IP dataset")
    
    ip_dataset = set()
    for key in server_ips:
        ip_dataset.add(key)
    for key in server_names:
        ip_dataset.add(server_names[key][0])
        ip_dataset.add(server_names[key][1])
    ip_dataset = list(ip_dataset)
    ip_dataset.sort()
    
    hostname_dataset = set()
    for key in server_names:
        hostname_dataset.add(key)
    for key in server_ips:
        hostname_dataset.add(server_ips[key][3])
        hostname_dataset.add(server_ips[key][4])
    hostname_dataset = list(hostname_dataset)
    hostname_dataset.sort()
    
    if config.getboolean("DEFAULT", "PingServers"):
        print("Pinging IP dataset")
        ip_pinged = [["IP", "PING", "INV NAME"]]
        for ip in ip_dataset:
            if ip:
                result = ping(ip)
                print(ip, result)
                if config.getboolean("DEFAULT", "OnlyShowFailedPings"):
                    if result == "FAIL":
                        try:
                            ip_pinged.append([ip, result, server_ips[ip][0]])
                        except:
                            ip_pinged.append([ip, result, "N/A"])
                else:
                    try:
                        ip_pinged.append([ip, result, server_ips[ip][0]])
                    except:
                        ip_pinged.append([ip, result, "N/A"])
        print("Exporting ping results to pings.csv")
        write_csv("pings.csv", ip_pinged)
        if config.getboolean("DEFAULT", "CreateRVToolsSummary"):
            failed_pings = [x[0] for x in ip_pinged if x[1] == "FAIL"]
            rvtools_summary_failedpings = [rvtools_summary[0]]
            for row in rvtools_summary:
                if row[0] in failed_pings:
                    rvtools_summary_failedpings.append(row)
                    failed_pings.remove(row[0])
            for ip in failed_pings:
                try:
                    rvtools_summary_failedpings.append([ip, f"N/A (INV NAME: {server_ips[ip][0]})", "N/A", "N/A", "N/A", "N/A", "N/A"])
                except:
                    rvtools_summary_failedpings.append([ip, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"])
            write_csv("rvtoolsSummaryFailedPings.csv", rvtools_summary_failedpings)
                    
    else:
        print("Skipping server pinging (PingServers = False)")
    print("Tasks complete! See ./output/ for exported data")

if __name__ == "__main__":
    main()