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
    
def import_inv_csv_data():
    pass

def main():

    inv_csv_filename = validate_file("inv.csv", "EPN IAPISE Inventory")
    rvtools_csv_filename = validate_file("tools.csv", "RVTools")
  
    print(f"Files {inv_csv_filename} and {rvtools_csv_filename} found!")
    print(f"Loading data from {inv_csv_filename}")
    
    servers_ip = {}
    server_names = {}
    # will point to config
    inv_csv_header = 1
    inv_csv_ip_col = 0
    inv_csv_name_col = 1
    inv_csv_hostname_col = 2
    inv_csv_os_col = 3
    
    with open(inv_csv_filename, "r") as inv_csv_file:
        inv_csv = csv.reader(inv_csv_file)
        line_count = 0
        while line_count <= inv_csv_header:
            next(inv_csv)
            line_count += 1
        for row in inv_csv:
            servers_ip[row[inv_csv_ip_col].replace("Â", "").strip()] = [row[inv_csv_name_col].replace("Â", "").strip(), "", False, row[inv_csv_hostname_col].replace("Â", "").strip(), "", False, row[inv_csv_os_col].replace("Â", "").strip(), "", False]
            if row[inv_csv_name_col]:
                server_names[row[inv_csv_name_col].replace("Â", "").strip()] = [row[inv_csv_ip_col].replace("Â", "").strip(), "", False]
        for key in servers_ip:
            print(f"{key} : {servers_ip[key]}")
        for key in server_names:
            print(f"{key} : {server_names[key]}")
    
if __name__ == "__main__":
    main()