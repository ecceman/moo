#!/usr/bin/env python

import argparse
from rich import print as rprint
from rich.progress import Progress
from rich.table import Table
from datetime import datetime
import logging
from rich.logging import RichHandler
from pprint import pformat
from ipaddress import IPv4Address
import csv
from rich.console import Console
from infoblox import Infoblox
from dotenv import find_dotenv
from argparse import RawTextHelpFormatter
from queue import Queue
from threading import Thread
import time
import pprint
import sys


def ipAddressCheck(input_str: str) -> bool:
    try:
        IPv4Address(input_str)
        return True
    except ValueError:
        return False

def hostRecordLookup(item: str):
    # status.update(f'Looking for HOST records...: ')
    if ipAddressCheck(item):
        sc, response = ib.getRecord(item, record_type='host', search_by='ipv4addr')
    else:
        sc, response = ib.getRecord(item, record_type='host', search_by='name')
    # status.update(f'Looking for HOST records...: {sc}')

    if sc == 200 and response:
        i = 1
        rowset = []
        for _ in response:
            # status.update(f'Processing API response: {i} of {len(response)}')
            row = ['','','','','','','','','','','']
            row[0] = _['ipv4addrs'][0].get('dns_name')
            row[0] = _['ipv4addrs'][0].get('host')
            row[1] = _['ipv4addrs'][0].get('ipv4addr')
            sc2, r2 = ib.getIpv4address(row[1])
            if sc2 == 200:
                for _2 in r2:
                    row[2] = _2.get('mac_address')
                    row[3] = _2.get('network')
                    row[5] = _2.get('types')
                    row[6] = _2.get('usage')
            sc3, r3 = ib.getNetwork(row[3])
            if sc3 == 200:
                for _3 in r3:
                    row[4] = _3.get('comment')
                    row[7] = _3.get('extattrs').get('Network Type')['value'] if 'Network Type' in _3.get('extattrs') else ''
                    row[8] = _3.get('extattrs').get('Subnet Owner')['value'] if 'Subnet Owner' in _3.get('extattrs') else ''
                    row[9] = _3.get('extattrs').get('ZPA On Lan')['value'] if 'ZPA On Lan' in _3.get('extattrs') else ''
                    row[10] = _3.get('extattrs').get('VLAN ID')['value'] if 'VLAN ID' in _3.get('extattrs') else ''
            sc4, r4 = ib.getDHCPLease(row[1])
            if sc4 == 200:
                for _4 in r4:
                    row[2] = _4.get('hardware') if not row[2] else row[2]
                    row[5] = _4.get('types') if not row[5] else row[5]
                    row[6] = _4.get('usage') if not row[6] else row[6]
            i += 1
            rowset.append(row)
        return rowset
    return False

def aRecordLookup(item: str):
    # status.update(f'Looking for A records...: ')
    if ipAddressCheck(item):
        sc, response = ib.getRecord(item, record_type='a', search_by='ipv4addr')
    else:
        sc, response = ib.getRecord(item, record_type='a', search_by='name')     
    # status.update(f'Looking for A records...: {sc}') 
    if sc == 200 and response:
        i = 1
        rowset = []
        for _ in response:
            # status.update(f'Processing API response: {i} of {len(response)}')
            row = ['','','','','','','','','','','']
            row[0] = _.get('name')
            row[1] = _.get('ipv4addr')
            if row[1]:
                sc2, r2 = ib.getIpv4address(row[1])
                if sc2 == 200 and r2:
                    row[2] = r2[0].get('mac_address')
                    row[3] = r2[0].get('network')
                    row[5] = r2[0].get('types')
                    row[6] = r2[0].get('usage')
                if row[3]:
                    sc3, r3 = ib.getNetwork(row[3])
                    if sc3 == 200 and r3:
                        row[4] = r3[0].get('comment')  
            rowset.append(row)
            i += 1
        return rowset
    return False

def IPLookup(item: str):
    sc, response = ib.getIpv4address(item)
    # log.info(f'Done IP Lookup: {sc, response}')
    if sc == 200 and response:
        rowset = []
        row = ['','','','','','','','','','','']
        for _ in response:
            row[1] = item
            row[0] = _.get('names')
            row[2] = _.get('mac_address')
            row[3] = _.get('network')
            row[5] = _.get('types')
            row[6] = _.get('usage')
            if row[3]:
                sc2, r2 = ib.getNetwork(row[3])
                log.info(pprint.pformat(r2[0]['extattrs'])) if args.l else ''
                if sc2 == 200 and r2:
                    row[4] = r2[0].get('comment')
                    row[7] = r2[0]['extattrs'].get('Network Type')['value'] if 'Network Type' in r2[0].get('extattrs') else ''
                    row[8] = r2[0]['extattrs'].get('Subnet Owner')['value'] if 'Subnet Owner' in r2[0].get('extattrs') else ''
                    row[9] = r2[0]['extattrs'].get('ZPA On Lan')['value'] if 'ZPA On Lan' in r2[0].get('extattrs') else ''
                    row[10] = r2[0]['extattrs'].get('VLAN ID')['value'] if 'VLAN ID' in r2[0].get('extattrs') else ''        
            rowset.append(row)
        return rowset
    return False
        
# Don't call return in this function, it breaks threading
def processItems(q):
    while True:
        log.info(f'Getting job from queue.') if args.l else ''
        try:
            item = q.get()
            log.info(f'Oh look, I found {item}') if args.l else ''
            progress.update(task, description=f'Work unit: {item} ')
        
            rowset = hostRecordLookup(item)
            if rowset:
                log.info(f'Host lookup done, found {len(rowset)} record(s)') if args.l else ''
                for row in rowset:
                    matrix.append(row)
                    log.info(f'{row}') if args.l else ''
            else:  
                log.info(f'No HOST records found, trying A records...') if args.l else ''
                rowset = aRecordLookup(item)
                if rowset:
                    log.info(f'A lookup done, found {len(rowset)} record(s)') if args.l else ''
                    for row in rowset:
                        matrix.append(row)
                else:
                    log.info(f'No A records found, trying IP lookup...') if args.l else ''
                    row = ['','','','','','','', '', '', '', '']
                    if ipAddressCheck(item):
                        rowset = IPLookup(item)
                        if rowset:
                            for row in rowset:
                                matrix.append(row)
        
            progress.advance(task)
        except Exception as e:
            print(str(e))
            
        q.task_done()    
                    
if __name__ == "__main__":
    epilog = 'examples of use:\r\n\r\n'
    epilog += '  moo switch01.somesite.com      - Lookup single device by FQDN\r\n'
    epilog += '  moo switch1                    - Lookup match switch1, switch10, switch11...\r\n'
    epilog += '  moo switch1, switch2, router3  - Lookup multiple devices\r\n'
    epilog += '  moo -i csv devicelist.csv      - Lookup multiple devices in CSV file, one per row\r\n'
    epilog += '  moo sw1,sw2,sw3 -o csv         - Lookup multiple devices, output result to csv file\r\n'
    epilog += '  moo sw1 -l                     - Debug logging, forces only one thread\r\n'
    epilog += '  moo -i csv list.csv -j 4       - Lookup multiple devices in CSV file, set threads to 4. Be careful.\r\n'
    
    parser = argparse.ArgumentParser(prog='moo.py', description='🐮 This cow will find stuff in your infoblox setup', epilog=epilog, formatter_class=RawTextHelpFormatter)
    parser.add_argument("inputstr", help="IP address or FQDN, comma separated for multiple, or CSV file (use together with '-i csv').")
    parser.add_argument("-l", help="Print log", action="store_true")
    parser.add_argument("-i", help="Input type, default to string", default="string", choices=['string', 'csv'])
    parser.add_argument("-o", help="Output type, default to stdout", default="stdout", choices=['stdout', 'csv'])
    parser.add_argument("-j", help="No of threads, defaults to 1, 2 or 4 depending on job list size", type=int)
    args = parser.parse_args()
    debug = True if args.l else False
    
    if not find_dotenv():
        with open('.env', 'w', newline='') as envfile:
            envfile.write('# Find the API version via /wapidoc on your infoblox server\r\n')
            envfile.write('#\r\n')
            envfile.write('INFOBLOX_USERNAME = "api-user"\r\n')
            envfile.write('INFOBLOX_PASSWORD = "secret"\r\n')
            envfile.write('INFOBLOX_URL = "https://infoblox.my.domain/wapi/v2.12.3/"\r\n')
        print('.env file not found, creating a new one. Edit it, then try again.')
        sys.exit()
        
    # Log initialize
    logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])
    log = logging.getLogger("rich")
    now = datetime.now()
        
    if args.l:
        log.info('\n\nStarting new log. ' + now.strftime("%Y-%m-%d %H:%M:%S") + '\n\n')
        log.info('Input string: ' + args.inputstr)
        
    q = Queue()
        
    # Split input string
    if args.i == 'string':
        inputstr = str(args.inputstr)
        input_list = inputstr.split(sep=',')
        for item in input_list:
            q.put(item)
    elif args.i == "csv":
        with open(args.inputstr, 'r') as input_csv:
            r = csv.reader(input_csv)
            input_list = []
            for row in r:
                input_list.extend(row)
    else:
        print('Invalid input, must be string or csv file.')
        parser.print_help()
        exit()
        
    if args.j:
        threads = int(args.j)
    else:
        if len(input_list) == 1:
            threads = 1
        elif len(input_list) > 1 and len(input_list) < 8:
            threads = 2
        else:
            threads = 4
        
    start_time = time.time()
    
    rprint(f'Input parsing complete, processing {len(input_list)} entries using {threads} threads, thats impressive.')
    
    t = Table()
    columns = ['Name', 'IPv4', 'MAC', 'Subnet', 'Comment', 'Types', 'Usage', 'Network Type', 'Owner', 'ZOL', 'VLAN ID']
    for _ in columns:
        t.add_column(_)
        
    matrix = []

    if args.l:    
        ib = Infoblox(log=log, debug=True)
    else:
        ib = Infoblox(log=log, debug=False)
        
    if not ib:
        print(f'Infoblox initialization failed, check .env file')
        sys.exit()
        
    console = Console()
        
    # with console.status("moo moo muthertrucker") as status:
    with Progress() as progress:
        task = progress.add_task("Processing... ", total=len(input_list))
        i = 0
        for i in range(threads):
            worker = Thread(target=processItems, args=(q,), daemon=True)
            worker.start()
            
        # Wait for threads to complete
        q.join()         
        
        for row in matrix:
            row[0] = ', '.join(row[0]) if type(row[0]) is list else row[0]      
            row[5] = ','.join(row[5]) if row[5] else ''      
            row[6] = ','.join(row[6]) if row[6] else ''
            t.add_row(str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5]), str(row[6]), str(row[7]), str(row[8]), str(row[9]), str(row[10]))
            
    rprint(t)
    rprint(f'Number of rows in table: {len(matrix)}. Threads: {threads}. Execution time: {round((time.time() - start_time), 2)} sec')
    
    if args.o == 'csv':
        filename = 'outout_' + datetime.now().strftime('%Y-%m-%d') + '.csv'
        with open(filename, 'w', newline='') as csvfile:
            w = csv.writer(csvfile)
            w.writerow(columns)
            for r in matrix:
                w.writerow(r)
        log.info('Export to CSV done.')
