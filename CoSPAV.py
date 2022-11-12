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
    ping_times = "1"
    command = ["ping", param, ping_times, host]
    ping_result = subprocess.run(command, capture_output=True)
    if ping_result.returncode == 0:
        result = re.search(r".*\((\d*% loss)\).*Average = (\d*ms).*", str(ping_result.stdout))
        return f"{result.group(1)} @ {result.group(2)}"
    else:
        return "FAIL"

def main():

    inv_csv = validate_file("inv.csv", "EPN IAPISE Inventory")
    rvtools_csv = validate_file("rvtools.csv", "RVTools")
  
    print(f"Files {inv_csv} and {rvtools_csv} found!")
    # Test
    print(ping("www.google.com"))
    print(ping("www.amazon.com"))
    print(ping("www.wawaxuxu.mex"))
    
if __name__ == "__main__":
    main()