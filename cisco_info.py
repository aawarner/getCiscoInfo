"""
Copyright (c) 2019 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
Filename: cisco_info.py
Version: Python 3.7.2
Authors: Aaron Warner (aawarner@cisco.com)
Description:    This program is designed to retrieve the serial number
                and license entitlement for Cisco Catalyst switches running
                IOS-XE 16.8 and below.
"""

from datetime import datetime
import csv
from multiprocessing.dummy import Pool as ThreadPool
import netmiko
import sys
import re


def getLoginInfo(csvFile):
    """
    Function to create list of dictionaries from CSV file.
    """
    with open(csvFile, "r") as swfile:
        reader = csv.DictReader(swfile)
        data = []
        for line in reader:
            data.append(line)
    return data


def convertLoginDict(data):
    """
    Converts list of dictionaries to list of lists
    """
    try:
        swlist = [[row["ipaddr"], row["username"], row["password"]] for row in data]
        return swlist
    except KeyError:
        print("\nInvalid header in CSV file. Please modify to the format below: "
              "\nipaddr,username,password"
              "\n10.10.10.10,admin,cisco"
              "\n10.10.10.11,admin,cisco\n"
              )
        sys.exit()


def getDevInfo(ip, user, pwd):
    """
    Function logs in to Cisco Switch and executes
    'show inventory' and 'show license right-to-use summary' on each device.
    Parses out serial number & technology package & writes them to CSV file
    device_info.csv.
    """
    session = {
        "device_type": "cisco_ios",
        "ip": ip,
        "username": user,
        "password": pwd,
        "verbose": False,
    }
    try:
        print("Connecting to switch {switch}".format(switch=ip))
        conn = netmiko.ConnectHandler(**session)
        info = conn.send_command("show version")
        sn = re.search(r"(?=.*\d{3})[A-Z]{3}[A-Za-z0-9]{8}", info)
        sn = sn.group(0)
        pid = re.search(r"C9[356]00.+?(?=\s)|[A-Z]{2}.[A-Z][0-9]{4}.+?(?=\s)", info)
        pid = pid.group(0)
        tech = re.search(r"network-.+?(?=\s)|ipservicesk9|ipbasek9|lanbasek9", info)
        tech = tech.group(0)

        devdata = [pid, sn, tech]

        print("Collection successful from switch {switch}".format(switch=ip))

        with open("device_info.csv", "a") as devFile:
            devwriter = csv.writer(devFile)
            devwriter.writerow(devdata)
            print(
                "Data for switch {switch} successfully written to device_info.csv".format(
                    switch=ip
                )
            )

    except (
        netmiko.NetMikoTimeoutException,
        netmiko.NetMikoAuthenticationException,
    ) as e:
        print(e)

    except AttributeError:
        print("Regex match error. Missing info for device {switch}".format(switch=ip))


def main(args):
    try:
        title = ["Product ID", "Serial Number", "License Entitlement"]
        with open("device_info.csv", "w+") as devFile:
            devwriter = csv.writer(devFile)
            devwriter.writerow(title)

        # Define start time
        start_time = datetime.now()

        # Define the number of threads
        num_threads = int(sys.argv[2])
        pool = ThreadPool(num_threads)

        # Import CSV file and generate list of dictionaries
        csvFile = sys.argv[1]
        data = getLoginInfo(csvFile)

        # Convert list of dictionaries to list of lists
        swlist = convertLoginDict(data)

        # Start threads
        pool.starmap(getDevInfo, swlist)
        pool.close()
        pool.join()

        print("\nReview collected information in device_info.csv")
        print("\nElapsed time: " + str(datetime.now() - start_time))

    except ValueError:
        print("Invalid entry for number of threads. Please enter an integer.")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv)
    else:
        print(
            "\nThis program is designed to retrieve the serial number\n"
            "and license entitlement for Cisco Catalyst switches running\n"
            "IOS-XE 16.8 and below.\n"
            "\nThe program accepts two arguments. The name of a CSV file and the number of desired threads.\n "
            "\nThe CSV should be in the format below:\n"
            "\nipaddr,username,password"
            "\n10.10.10.10,admin,cisco"
            "\n10.10.10.11,admin,cisco\n"
            "\nUsage: python get_info.py DeviceDetails.csv X\n"
            "\nThe 'X' represents the number of threads to execute"
        )
        sys.exit()
