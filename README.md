# moo
Infoblox CLI lookup tool

```
usage: moo.py [-h] [-l] [-i {string,csv}] [-o {stdout,csv}] [-j J] inputstr

🐮 This cow will find stuff in your infoblox setup

positional arguments:
  inputstr         IP address or FQDN, comma separated for multiple, or CSV file (use together with '-i csv').

options:
  -h, --help       show this help message and exit
  -l               Print log
  -i {string,csv}  Input type, default to string
  -o {stdout,csv}  Output type, default to stdout
  -j J             Threads, defaults to 2

examples of use:

  moo switch01.somesite.com      - Lookup single device by FQDN
  moo switch1                    - Lookup match switch1, switch10, switch11...
  moo switch1, switch2, router3  - Lookup multiple devices
  moo -i csv devicelist.csv      - Lookup multiple devices in CSV file, one per row
  moo sw1,sw2,sw3 -o csv         - Lookup multiple devices, output result to csv file
  moo sw1 -l                     - Debug logging, forces only one thread
  moo -i csv list.csv -j 4       - Lookup multiple devices in CSV file, set threads to 4. Be careful.
```

```
❯ python moo.py swi1,swi2,swi3,swi4,swi5,swi6
Input parsing complete, processing 6 entries using 2 threads, thats impressive.
Work unit: swi6  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Name            ┃ IPv4         ┃ MAC ┃ Subnet         ┃ Comment               ┃ Types ┃ Usage ┃ Network Type ┃ Owner        ┃ Automation ┃ VLAN ID ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━┩
│ swi1.domain.com │ 10.0.100.101 │     │ 10.0.100.0/25  │ Switch MGMT network   │ HOST  │ DNS   │ MGMT         │ Farmer Clive │ Disable    │ 250     │
│ swi2.domain.com │ 10.0.100.100 │     │ 10.0.100.0/25  │ Switch MGMT network   │ HOST  │ DNS   │ MGMT         │ Farmer Clive │ Disable    │ 250     │
│ swi3.domain.com │ 10.0.100.102 │     │ 10.0.100.0/25  │ Switch MGMT network   │ HOST  │ DNS   │ MGMT         │ Farmer Clive │ Disable    │ 250     │
│ swi4.domain.com │ 10.0.100.103 │     │ 10.0.100.0/25  │ Switch MGMT network   │ HOST  │ DNS   │ MGMT         │ Farmer Clive │ Disable    │ 250     │
│ swi5.domain.com │ 10.0.100.104 │     │ 10.0.100.0/25  │ Switch MGMT network   │ HOST  │ DNS   │ MGMT         │ Farmer Clive │ Disable    │ 250     │
│ swi6.domain.com │ 10.0.100.105 │     │ 10.0.100.0/25  │ Switch MGMT network   │ HOST  │ DNS   │ MGMT         │ Farmer Clive │ Disable    │ 250     │
└─────────────────┴──────────────┴─────┴────────────────┴───────────────────────┴───────┴───────┴──────────────┴──────────────┴────────────┴─────────┘
Number of rows in table: 6. Threads: 2. Execution time: 5.28 sec
```
Look up specific clients, get MAC address assuming Infoblox is DHCP Server
```
❯ moo 172.16.88.145
Input parsing complete, processing 1 entries using 2 threads, thats impressive.
Work unit: 172.16.88.145  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┓
┃ Name                               ┃ IPv4          ┃ MAC               ┃ Subnet         ┃ Comment        ┃ Types                  ┃ Usage    ┃ Network Type ┃ Owner          ┃ IPS    ┃ VLAN ID ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━┩
│ ly-afthg04.domain.com, LY-AFTHG04  │ 172.16.88.145 │ 28:c5:d2:44:00:a5 │ 172.16.88.0/24 │ Site C, London │ A,LEASE,PTR,DHCP_RANGE │ DNS,DHCP │ Production   │ Farmer Petsson │ Enable │ 35      │
└────────────────────────────────────┴───────────────┴───────────────────┴────────────────┴────────────────┴────────────────────────┴──────────┴──────────────┴────────────────┴────────┴─────────┘
Number of rows in table: 1. Threads: 2. Execution time: 2.67 sec
```
## Installation
Python 3.9 or later
1. Create venv `python -m venv /path/to/moo`
2. Download git repo to folder
3. Activate venv: `source /path/to/moo/bin/activate` or use bat file or ps1 file in scripts folder if you're on Windows
4. Install required packages `/path/to/moo/bin/pip install -r requirements.txt`
5. Run the script with any parameters to create a .env file. Then modify it.

## Infoblox access
API account needs read access to:
- DNS Permissions
- DHCP Permissions
- VLAN Permissions
