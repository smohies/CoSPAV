import os
import re
import csv
import subprocess
import platform

def validate_file(filename, description):
    while True:
        if not os.path.isfile(filename):
            print(f"{filename} not found, input the {description} CSV filename:")
            filename = input()
        else:
            break
    return filename

def ping(host):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    # will point to config
    ping_times = "1"
    command = ["ping", param, ping_times, host]
    ping_result = subprocess.run(command, capture_output=True)
    if ping_result.returncode == 0:
        result = re.search(r".*\((\d*% loss)\).*Average = (\d*ms).*", str(ping_result.stdout))
        return f"{result.group(1)} @ {result.group(2)}"
    else:
        return "FAIL"

def main():

    inv_csv_filename = validate_file("inv.csv", "EPN IAPISE Inventory")
    rvtools_csv_filename = validate_file("rvtools.csv", "RVTools")
  
    print(f"Files {inv_csv_filename} and {rvtools_csv_filename} found!")
    print(f"Loading data from {inv_csv_filename}")
    
    server_ips = {}
    server_names = {}
    # will point to config
    inv_csv_header = 1
    inv_csv_ip_col = 0
    inv_csv_name_col = 1
    inv_csv_hostname_col = 2
    inv_csv_os_col = 3
    
    # Import inv csv data
    with open(inv_csv_filename, "r") as inv_csv_file:
        inv_csv = csv.reader(inv_csv_file)
        line_count = 0
        while line_count <= inv_csv_header:
            next(inv_csv)
            line_count += 1
        for row in inv_csv:
            server_ips[row[inv_csv_ip_col].replace("Â", "").strip()] = [row[inv_csv_name_col].replace("Â", "").strip(), "", False, row[inv_csv_hostname_col].replace("Â", "").strip(), "", False, row[inv_csv_os_col].replace("Â", "").strip(), "", False]
            if row[inv_csv_name_col]:
                server_names[row[inv_csv_name_col].replace("Â", "").strip()] = [row[inv_csv_ip_col].replace("Â", "").strip(), "", False]
                
    print(f"Loading data from {rvtools_csv_filename}")
    
    # Import tool csv data
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
                    
    print(f"Loaded {len(server_ips)} entries for server_ips and {len(server_names)} entries for server_names")
    print("Searching for discrepancies")
    
    # Find discrepancies in server_ips
    for key in server_ips:
        if server_ips[key][0] != server_ips[key][1]:
            server_ips[key][2] = True
        if server_ips[key][3] != server_ips[key][4]:
            server_ips[key][5] = True
        if server_ips[key][6] != server_ips[key][7]:
            server_ips[key][8] = True
    
    # Find discrepancies in server_names
    for key in server_names:
        if server_names[key][0] != server_names[key][1]:
            server_names[key][2] = True
    
    # List discrepancies in server_ips
    server_ips_diffs = ["IP (INV), INV NAME, RVT NAME, INV HOSTNAME, RVT HOSTNAME, INV OS, RVT OS"]
    for key in server_ips:
        if server_ips[key][2] == True or server_ips[key][5] == True or server_ips[key][8] == True:
            server_ips_diffs.append(f"{key}, {server_ips[key][0]}, {server_ips[key][1]}, {server_ips[key][3]}, {server_ips[key][4]}, {server_ips[key][6]}, {server_ips[key][7]}")
    
    # List discrepancies in server_names
    server_names_diffs = ["NAME (INV), INV IP, RVT IP"]
    for key in server_names:
        if server_names[key][2] == True:
            server_names_diffs.append(f"{key}, {server_names[key][0]}, {server_names[key][1]}")
            
    print(f"Found discrepancies in {len(server_ips_diffs)}/{len(server_ips)} entries from server_ips")
    print(f"Found discrepancies in {len(server_names_diffs)}/{len(server_names)} entries from server_names")
    
    
    """for x in server_ips_diffs:
        print(x)
    for x in server_names_diffs:
        print(x)"""
    
if __name__ == "__main__":
    main()