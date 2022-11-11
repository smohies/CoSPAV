import os
import csv
import subprocess

def main():

    epn_iapise_inv_csv = "1.csv"
    rvtools_csv = "2.csv"

    while True:
        if not os.path.isfile(epn_iapise_inv_csv):
            print(f"{epn_iapise_inv_csv} not found, input the EPN IAPISE Inventory CSV filename:")
            epn_iapise_inv_csv = input()
        else:
            break
        
    while True:
        if not os.path.isfile(rvtools_csv):
            print(f"{rvtools_csv} not found, input the RVTools CSV filename:")
            rvtools_csv = input()
        else:
            break
        
    print("Files found!")
    
if __name__ == "__main__":
    main()