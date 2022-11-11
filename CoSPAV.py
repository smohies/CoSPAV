import os
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
    command = ["ping", param, "1", host]
    ping_result = subprocess.run(command)
    if ping_result.returncode == 0:
        return "Good Ping!"
    else:
        return "Bad Ping!"

def main():

    epn_iapise_inv_csv = validate_file("1.csv", "EPN IAPISE Inventory")
    rvtools_csv = validate_file("2.csv", "RVTools")
  
    print(f"Files {epn_iapise_inv_csv} and {rvtools_csv} found!")
    
if __name__ == "__main__":
    main()