#!/usr/bin/env python

import requests
import os
from dotenv import load_dotenv, find_dotenv
from configparser import ConfigParser
import re

class Infoblox:
    def __init__(self, verify=False, log='', debug=False) -> None:
        load_dotenv()
        self.base_url = os.environ.get('INFOBLOX_URL')
        self.username = os.environ.get('INFOBLOX_USERNAME')
        self.password = os.environ.get('INFOBLOX_PASSWORD')
        self.verify = verify
        self.log = log
        self.debug = debug
        
        self.config = ConfigParser()
        self.config.read('./settings.ini')

        if verify == False:
            requests.packages.urllib3.disable_warnings()
            
        self.IB_NETWORK_RF = f'&_return_fields={self.config.get('RETURN FIELDS', 'IB_NETWORK_RF')}' if re.search('^[a-z,_]*$', self.config.get('RETURN FIELDS', 'IB_NETWORK_RF')) else ''
        self.IB_DHCP_LEASE_RF = f'&_return_fields={self.config.get('RETURN FIELDS', 'IB_DHCP_LEASE_RF')}' if re.search('^[a-z,_]*$', self.config.get('RETURN FIELDS', 'IB_DHCP_LEASE_RF')) else ''
        self.IB_RECORD_HOST_RF = f'&_return_fields={self.config.get('RETURN FIELDS', 'IB_RECORD_HOST_RF')}' if re.search('^[a-z,_]*$', self.config.get('RETURN FIELDS', 'IB_RECORD_HOST_RF')) else ''
        self.IB_RECORD_A_RF = f'&_return_fields={self.config.get('RETURN FIELDS', 'IB_RECORD_A_RF')}' if re.search('^[a-z,_]*$', self.config.get('RETURN FIELDS', 'IB_RECORD_A_RF')) else ''
        self.IB_RECORD_PTR_RF = f'&_return_fields={self.config.get('RETURN FIELDS', 'IB_RECORD_PTR_RF')}' if re.search('^[a-z,_]*$', self.config.get('RETURN FIELDS', 'IB_RECORD_PTR_RF')) else ''
        

    def __apiCall(self, endpoint):
        try:
            response = requests.get(self.base_url + endpoint, verify=self.verify, auth=(self.username, self.password))
            response.raise_for_status()
            
            if self.debug:
                self.log.info(f'__apiCall() to Endpoint {endpoint}')
                self.log.info(f'__apiCall() Response code {response.status_code}')
                self.log.info(f'__apiCall() Response text {response.text}')
            if response.status_code == 200:
                return response.status_code, response.json()
            else:
                return response.status_code, response.text
        
        except requests.exceptions.RequestException as e:
            raise Exception(e)


    def getRecord(self, input: str, record_type:str = 'host', search_by: str = 'name') -> tuple:
        if record_type == 'host' and search_by == 'name':
            endpoint = f'record:host?name~:={input}{self.IB_RECORD_HOST_RF}'
        elif record_type == 'host' and search_by == 'ipv4addr':
            endpoint = f'record:host?ipv4addr={input}{self.IB_RECORD_HOST_RF}'
        elif record_type == 'a':
            endpoint = f'record:a?name~={input}{self.IB_RECORD_A_RF}'
        elif record_type == 'ptr':
            endpoint = f'record:a?ipv4addr~={input}{self.IB_RECORD_PTR_RF}]'
        else:
            return False, False
        
        sc, response = self.__apiCall(endpoint)
        return sc, response
    

    def getDHCPLease(self, ip:str) -> tuple:
        endpoint = f'lease?address={ip}{self.IB_DHCP_LEASE_RF}'
        status_code, response = self.__apiCall(endpoint)
        return status_code, response
    
    def getNetworkByIP(self, ip:str) -> tuple:
        sc, response = self.getIpv4address(ip)
        if sc == 200 and response:
            network = response[0].get('network')
            types = response[0].get('types')
            usage = response[0].get('usage')
            if network:
                sc2, response2 = self.getNetwork(network)
                if sc2 == 200 and response2:
                    return network, response2[0], types, usage
        
        return False, False, False, False
    
    def getIpv4address(self, ip: str) -> tuple:
        endpoint = f'ipv4address?ip_address={ip}'
        sc, response = self.__apiCall(endpoint)
        return sc, response
    
    def getNetwork(self, network: str) -> tuple:
        endpoint = f'network?network={network}{self.IB_NETWORK_RF}'
        sc, response = self.__apiCall(endpoint)
        return sc, response
    
    def getInfoBySearch(self, searchstr: str, field = 'address') -> tuple:
        # From doc: NOTE: Only one of the following can be used each time: ‘address’, ‘mac_address’, ‘duid’ or ‘fqdn’.
        if field == 'address':
            endpoint = f'search?address={searchstr}'
            sc, response = self.__apiCall(endpoint)
            return sc, response
        return False, False

