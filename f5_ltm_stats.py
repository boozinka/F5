#!/usr/bin/env python

""" Imports an F5 LTM Virtual Server details and Pool stats from API. Coverts
    the JSON output to a dictionary and extracts the relevant information to
    ascertain if that Virtual Server/LTM Pool is in use or not.
"""

# Author: Wayne Bellward
# Date: 19/10/2022


import os
import sys
import pathlib
import ipaddress
from pprint import pprint
from getpass import getpass
from datetime import datetime
from f5api_call import f5api_get_call


def write_api(myapi, dict_type):
    
    """ Unpack passed dictionary and write the virtual server info and dump
        to a .csv file.
    """

    now = datetime.now()
    dt_str = now.strftime('%d-%m-%y_%H%M%S')

    suffix = '_'+ dict_type + '_' + dt_str

    os.system('cls')
    filename = input('\n\nPlease enter the name of the file you wish to save '
                     'without the file extension,\nactive or inactive will be '
                     'suffixed to the filename along with the date and time: '
                     )
    
    filename = filename + suffix +'.csv'

    header = ['Virtual Server Name', ',',
              'Virtual Server Destination IP', ',',
              'Virtual Server Destination Port', ',',
              'Virtual Server Description', ',',
              'Associated Pool Name', ',',
              '\n']

    with open(filename, 'w') as file:

        # Write header
        file.writelines(header)

        # Iterate over passed dictionary
        for virt, params in myapi.items():
            # Unpack dictionary
            virt_dest = params['virt_dest'].split('/')[2]
            virt_desc = params['virt_desc']
            virt_pool = params['virt_pool'].split('/')[2]

            # Separate IP and port in the virtual server destination
            virt_dest_ip = virt_dest.split(':')[0]
            virt_dest_port = virt_dest.split(':')[1]
            
            # Compose line to be written
            line = [virt, ',', virt_dest_ip, ',', virt_dest_port, ',',
                    virt_desc, ',', virt_pool, ',', '\n']

            # Write each line to the file
            file.writelines(line)
                
    print('\nThe file has been written to timestamped "', filename,
          '" in the local directory', sep = '')
    input('\nPress Enter to return to main menu.')


def get_api_params():

    """ Function to get input parameters for the F5 REST API call """

    # Intialise variables
    ipaddr = False

    # Input F5 authentication credentials for REST API Call
    print('\nF5 REST API Authentication')
    print('-'*30,)
    username = input('\nPlease enter your username: ')
    passwd = getpass('Please enter your password: ')
    os.system('cls')

    # Input IP address of F5 LTM device, and loop until IP is valid
    while not ipaddr:
        try:
            ipaddr = ipaddress.ip_network(input('Please enter the IP address of'
                                                ' the of the F5 LTM you want to'
                                                ' make the API call on: '))
        except ValueError:
            ipaddr = False
            print('You entered an invalid IP address, please try again.\n')
            
    # Strip '/32' from the IP address and convert to a string
    ipaddr = str(ipaddr).split('/')[0]

    return username, passwd, ipaddr


def get_uri_ext(ipaddr):

    """ Asks the user to input the URI extension to append to the base URI """

    # Input URI extension for specific API call
    print('\nThe Base URI is: https://{}/mgmt/tm/ltm/'.format(ipaddr))
    uri_ext = input('Please enter the URI extension: ')

    return uri_ext

    
def create_virt_dict(ltm_virt):

    """ Takes the raw json output in the form of dictionary
        from the API call and create new diction with only the
        information we need.
    """

    #Intialise varibles
    virt_dict = {}
    virt_list = ltm_virt['items']

    for virt in virt_list:
        virt_name = virt['name']
        virt_pool = virt['pool']
        virt_dest = virt['destination']
        try:
            virt_desc = virt['description']
        except KeyError:
            virt_desc = 'No Description'

        virt_dict.update({virt_name: {'virt_pool': virt_pool, 'virt_desc': virt_desc,
                                      'virt_dest': virt_dest}})

    return virt_dict


def xref_pools(virt_dict, ltm_stats):

    """ Runs through the virt_dict and cross references it's pools against the
        LTM Pool Stats to see if any or the virtual servers pools have traffic
        against them, if a virtual servers pool has traffic then against it,
        it is deleted from the virt_dict, as we are only interested in
        Virtual Servers which are not in use.
    """

    # Copy virt_dict
    virt_inact_dict = virt_dict.copy()

    # Intialise varibles
    virt_act_dict = {}
    eval_list = []

    # X-Ref the new virt dict with LTM pools to create active and inactive dict
    for virt, values in virt_dict.items():
        pool_ref = values['virt_pool'].replace('/', '~')
        pool_ref_prefix = 'https://localhost/mgmt/tm/ltm/pool/members/'
        pool_ref_stats = pool_ref_prefix + pool_ref + '/stats'
        pool_ref_mems = pool_ref_prefix +  pool_ref + '/members/stats'
        
        ltm_mems = ltm_stats['entries'][pool_ref_stats]['nestedStats']['entries']\
                   [pool_ref_mems]['nestedStats']['entries']

        for mem, params in ltm_mems.items():
            mem_stats = params['nestedStats']['entries']
            ipaddr = mem_stats['addr']['description']
            eval_list.append(mem_stats['serverside.bitsIn']['value'])
            eval_list.append(mem_stats['serverside.bitsOut']['value'])
            eval_list.append(mem_stats['serverside.curConns']['value'])
            eval_list.append(mem_stats['serverside.maxConns']['value'])
            eval_list.append(mem_stats['serverside.pktsIn']['value'])
            eval_list.append(mem_stats['serverside.pktsOut']['value'])
            eval_list.append(mem_stats['serverside.totConns']['value'])

            # If any of the stats are not 0, pop that virt into an active dict
            if any(v != 0 for v in eval_list):
                virt_act_dict.update({virt: virt_inact_dict.pop(virt)})
                eval_list = []
                break
            else:
                eval_list = []

    return virt_act_dict, virt_inact_dict


def main_menu():
    # Setup Main Menu Loop

    os.system('cls')
    mm_choice = None
    while mm_choice != "q":
        print(
            """
            Main Menu
            Q - Quit.
            1 - Write the active virtual servers to a file.
            2 - Write the inactive virtual servers to a file.
            """
        )

        mm_choice = input("Choice: ").lower()
        print()
        return mm_choice


def main():

    """ Main Program """

    # Get input parameters for the F5 REST API call
    username, passwd, ipaddr = get_api_params()

    # Get URI extension
    print('\nURI Extension for the LTM Pool Stats REST API Call')
    print('-' * 55)
    uri_ext = get_uri_ext(ipaddr)
    os.system('cls')

    # Make REST API Calls for LTM Pool stats
    ltm_stats = f5api_get_call(username, passwd, ipaddr, uri_ext)
    os.system('cls')

    # Get new URI extension
    print('\nURI Extension for the Virtual Server Info REST API Call')
    print('-' * 55)
    uri_ext = get_uri_ext(ipaddr)
    os.system('cls')
    
    # Make REST API Calls for Virtual server details
    my_ltm_virt = f5api_get_call(username, passwd, ipaddr, uri_ext)
    os.system('cls')

    # Create new dictionary with selected virtual server parameters
    virt_dict = create_virt_dict(my_ltm_virt)

    # Create an active & inactive dictionary of virtual srvs based on pool stats
    virt_act_dict, virt_inact_dict = xref_pools(virt_dict, ltm_stats)

    mm_val = None
    while mm_val != 'q':
        mm_val = main_menu()
        match mm_val:
            case '1':
                os.system('cls')
                print('\nPrint active virtual servers')
                write_api(virt_act_dict, 'active')
            case '2':
                os.system('cls')
                print('\nPrint inactive virtual servers')
                write_api(virt_inact_dict, 'inactive')
            case 'q':
                break
            case _:
                os.system('cls')
                print('\Invalid input please try again.')
                input('\nPress Enter to try again.')

    input('\nPress Enter to exit script ')
    

if __name__ == "__main__":

    main()
