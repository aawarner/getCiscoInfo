# getCiscoInfo

This program is designed to retrieve the serial number
and license entitlement for Cisco Catalyst switches.

  * [Supported platforms](#supported-platforms)
  * [Requirements](#requirements)
  * [Usage](#usage)

## Supported platforms
Cisco Catalyst Switches running IOS-XE. Tested on Catalyst 3850 and Catalyst 9300.

## Requirements
Relies on Netmiko library

```
pip install netmiko
```

## Usage
```
Usage: python get_info.py example.csv X
```
The program accepts two arguments. The name of a CSV file and the number of desired threads.
 
The CSV should be in the format below:

```
ipaddr,username,password
10.10.10.10,admin,cisco
10.10.10.11,admin,cisco
```

This can be seen in example.csv

The 'X' represents the number of threads to execute.
