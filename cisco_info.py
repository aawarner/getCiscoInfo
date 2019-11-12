from datetime import datetime
import csv
from multiprocessing.dummy import Pool as ThreadPool
import netmiko
import sys


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
    swlist = [[row["ipaddr"], row["username"], row["password"]] for row in data]
    return swlist


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
        sn = conn.send_command("show inventory")
        sn = sn.split()
        sn = sn[13]

        tech = conn.send_command("show license right-to-use summary")
        tech = tech.split()
        tech = tech[-1]

        devdata = [sn, tech]

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


def main(args):
    try:
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
