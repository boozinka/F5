#!/usr/bin/env python

""" Imports an F5 LTM Virtual Server details and Pool stats from API. Coverts
    the JSON output to a dictionary and extracts the relevant information to
    ascertain if that Virtual Server/LTM Pool is in use or not.

    This program expects the following API URLs as follows:

        https://<ip-address>/mgmt/tm/ltm/pool/members/stats
        https://<ip-address>/mgmt/tm/ltm/virtual 
"""

# Author: Wayne Bellward
# Date: 19/10/2022


import os
import sys
import pathlib
import ipaddress
from getpass import getpass
from datetime import datetime
from f5api_call import f5api_get_call


def get_filename(message):

    """ Get the user to input the filename they want to use to write a file """

    now = datetime.now()
    dt_str = now.strftime('%d-%m-%y_%H%M%S')

    filename = input(message)

    return filename, dt_str
    

def write_api(myapi, dict_type):
    
    """ Unpack passed dictionary and write the virtual server info and dump
        to a .csv file.
    """

    message = '\n\nPlease enter the name of the file you wish to save '
    'without the file extension,\nactive or inactive will be '
    'suffixed to the filename along with the date and time: '

    filename, dt_str = get_filename(message)
    suffix = '_'+ dict_type + '_' + dt_str
    os.system('cls')
    filename = filename + suffix +'.csv'

    header = ['Virtual Server Name', ',',
              'Virtual Server Destination IP', ',',
              'Virtual Server Destination Port', ',',
              'Virtual Server Description', ',',
              'Associated Pool Name', ',',
              'Pool Member 1', ',', 'Pool Member 2', ',', 'Pool Member 3', ',',
              'Pool Member 4', ',', 'Pool Member 5', ',', 'Pool Member 6', ',',
              'Pool Member 7', ',', 'Pool Member 8', ',', 'Pool Member 9', ',',
              'Pool Member 10', ',', 'Pool Member 11', ',', 'Pool Member 12',
              '\n']

    with open(filename, 'w') as file:

        # Write header
        file.writelines(header)

        # Iterate over passed dictionary
        for virt, params in myapi.items():
            # Unpack dictionary
            virt_dest = params['virt_dest'].split('/')[2]
            virt_desc = params['virt_desc']
            try:
                pool_name = params['virt_pool']['pool_name'].split('/')[2]
            except IndexError:
                pool_name = params['virt_pool']['pool_name']
            
            pool_mems = params['virt_pool']['pool_mems']

            # Separate IP and port in the virtual server destination
            virt_dest_ip = virt_dest.split(':')[0]
            virt_dest_port = virt_dest.split(':')[1]
            
            # Compose line to be written
            line = [virt, ',', virt_dest_ip, ',', virt_dest_port, ',',
                    virt_desc, ',', pool_name]

            # Unpack pool members list of dicts and add mem id to new list
            for mem in pool_mems:
                for mem_id in mem.keys():
                    line.append(',')
                    line.append(mem_id)

            # Add a newline to the end of the line and write it a to the file
            line.append('\n')
            file.writelines(line)
                
    print('\nThe file has been written to timestamped ', filename,
          ' in the local directory', sep = '')
    input('\nPress enter to return to options menu.')


def write_poolmem_stats(virt_dict):
    
    """ Unpack passed dictionary and write the stats of all pool members to a
        .csv file.
    """

    os.system('cls')
    message = '\n\nPlease enter the name of the file you wish to save '
    'without the file extension,\nthe the date and time will'
    'be suffixed to the filename: '
              
    filename, dt_str = get_filename(message)
    suffix = '_' + dt_str
    filename = filename + suffix +'.csv'
    header = ['Pool Member Id', ',',
              'Server Side Bits In', ',',
              'Server Side Bits Out', ',',
              'Server Side Current Connections', ',',
              'Server Side Max Connections', ',',
              'Server Side Packets In', ',',
              'Server Side Packets Out', ',',
              'Server Side Total Connections', ',',
              '\n']

    with open(filename, 'w') as file:

        # Write header
        file.writelines(header)

        # Iterate over passed dictionary
        for virt, params in virt_dict.items():
            # Unpack dictionary
            pool_mems = params['virt_pool']['pool_mems']

            # Unpack pool members list of dicts and add mem id to new list
            for mem in pool_mems:
                for mem_id, stats in mem.items():
                    line = [mem_id]
                    for ss_stat, value in stats.items():
                        line.append(',')
                        line.append(str(value))

                    # Add a newline character and write line to the file
                    line.append('\n')
                    file.writelines(line)
                
    print('\nThe file has been written to timestamped ', filename,
          ' in the local directory', sep = '')
    input('\nPress enter to return to options menu.')


def print_poolmem_stats(virt_dict):
    
    """ Unpack passed dictionary and print the stats of all pool members for a
        single virtual server to the screen.
    """

    # Initalise Varibles
    stat_names = {'serverside_bitsin': 'Server Side Bits In',
                  'serverside_bitsout': 'Server Side Bits Out',
                  'serverside_curconns': 'Server Side Current Conns',
                  'serverside_maxconns': 'Server Side Max Conns',
                  'serverside_pktsin': 'Server Side Packets In',
                  'serverside_pktsout': 'Server Side Packets Out',
                  'serverside_totconns': 'Server Side Total Conns'
                  }

    # Ask user to input the virtual server name
    my_virt_stats = False
    while not my_virt_stats:
        
        os.system('cls')
        virt_id = input('\n\nThe virtual server name is case sensitive.\n\n'
                        'Please enter the name of the virtual server you '
                        'wish to view the pool member stats for: '
                        )
        try:
            my_virt_stats = virt_dict[virt_id]
        except KeyError:
            input('\nVirtual server does not exist, press enter to try again.')

    # Print the formatted output to the screen
    os.system('cls')
    print('\n\n')
    print('='*60)
    print(f"{'Virtual Server:':<18}{virt_id:<30}")
    print('='*60)
    print()

    try:
        pool_name = my_virt_stats['virt_pool']['pool_name'].split('/')[2]
    except IndexError:
        pool_name = my_virt_stats['virt_pool']['pool_name']
        
    print(f"{'':<10}{'LTM Pool:':<10}{pool_name:<30}")
    print(f"{'':<10}{'-'*50:<50}")
    print()
    
    pool_mems = my_virt_stats['virt_pool']['pool_mems']
    for mem in pool_mems:
        for mem_id, stats in mem.items():
            print()
            print(f"{'':<20}{'Member:':<10}{mem_id:<20}")
            print(f"{'':<20}{'-'*40:<40}")
            print()
            for stat, value in stats.items():
                print(f"{'':<30}{stat_names[stat]:<30}{':':<3}{value:<10}")
    
    input('\nPress enter to return to options menu.')

    
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
            ipaddr = ipaddress.ip_network(input('Please enter the IP address '
                                                'of the F5 LTM you want to '
                                                'make the API call on: '))
        except ValueError:
            ipaddr = False
            print('You entered an invalid IP address, please try again.\n')
            
    # Strip '/32' from the IP address and convert to a string
    ipaddr = str(ipaddr).split('/')[0]

    return username, passwd, ipaddr

    
def create_virt_dict(ltm_virt):

    """ Takes the raw json output in the form of dictionary
        from the API call and create new diction with only the
        information we need.
    """

    #Intialise varibles
    virt_dict = {}
    virt_list = ltm_virt['items']

    # Iterate over virtual server api response and create new dict with our info
    for virt in virt_list:
        virt_name = virt['name']
        try:
            virt_pool = virt['pool']
        except KeyError:
            virt_pool = 'NO POOL CONFIGURED'
        virt_dest = virt['destination']
        try:
            virt_desc = virt['description']
        except KeyError:
            virt_desc = 'No Description'

        virt_dict.update({virt_name: {'virt_desc': virt_desc,
                                      'virt_dest': virt_dest,
                                      'virt_pool': {'pool_name': virt_pool,
                                                    'pool_mems': []
                                                    }
                                      }
                          }
                         )

    return virt_dict


def xref_pools(virt_dict, ltm_stats):

    """ Runs through the virt_dict and cross references it's pools against the
        LTM Pool Stats to see if any of the virtual servers pools have traffic
        against them. Based on the results the dictionary is split into two new
        dictionaries, 'active' and 'inactive'.
    """

    # Shallow copy virt_dict (virt_dict is also updated as part of this function)
    virt_inact_dict = virt_dict.copy()

    # Intialise varibles
    virt_act_dict = {}

    # X-Ref the new virt dict with LTM pools to create active and inactive dict
    for virt, values in virt_dict.items():
        pool_ref = values['virt_pool']['pool_name'].replace('/', '~')
        pool_ref_prefix = 'https://localhost/mgmt/tm/ltm/pool/members/'
        pool_ref_stats = pool_ref_prefix + pool_ref + '/stats'
        pool_ref_mems = pool_ref_prefix +  pool_ref + '/members/stats'

        # Unpack Pool Members and error handle in the event there are none.
        try:
            ltm_mems = ltm_stats['entries'][pool_ref_stats]['nestedStats']['entries']\
                       [pool_ref_mems]['nestedStats']['entries']
        except KeyError:
            virt_inact_dict[virt]['virt_pool']['pool_mems'].append({'': {}})
            mem = {}
            virt_status = False
            break

        # Set virtual server status flag to False at the beginning iteration
        virt_status = False
        for mem, params in ltm_mems.items():
            mem_stats = params['nestedStats']['entries']

            # Grab all stats for that pool member
            ss_bitsin = (mem_stats['serverside.bitsIn']['value'])
            ss_bitsout = (mem_stats['serverside.bitsOut']['value'])
            ss_curconns = (mem_stats['serverside.curConns']['value'])
            ss_maxconns = (mem_stats['serverside.maxConns']['value'])
            ss_pktsin = (mem_stats['serverside.pktsIn']['value'])
            ss_pktsout = (mem_stats['serverside.pktsOut']['value'])
            ss_totconns = (mem_stats['serverside.totConns']['value'])

            # Grab pool member IP address and port to form member id
            ipaddr = mem_stats['addr']['description']
            port = mem_stats['port']['value']
            mem_id = ipaddr + ':' + str(port)

            # Create member dictionary to append to pool member list
            mem = {mem_id: {'serverside_bitsin': ss_bitsin,
                            'serverside_bitsout': ss_bitsout,
                            'serverside_curconns': ss_curconns,
                            'serverside_maxconns': ss_maxconns,
                            'serverside_pktsin': ss_pktsin,
                            'serverside_pktsout': ss_pktsout,
                            'serverside_totconns': ss_totconns
                            }
                   }
            virt_inact_dict[virt]['virt_pool']['pool_mems'].append(mem)
            mem = {}

            # Form list of stats to evaluate as active or inactive pool member
            eval_list = [ss_bitsin, ss_bitsout, ss_curconns, ss_maxconns,
                         ss_pktsin, ss_pktsout, ss_totconns,]
            
            # If any of the stats are not 0, set 'virt_status' to True as the
            # virtual server must be active
            if any(v != 0 for v in eval_list):
                virt_status = True
                eval_list = []
            else:
                eval_list = []

        # If virt_status flag is true, pop that virt into an active dict
        if virt_status == True:
            virt_act_dict.update({virt: virt_inact_dict.pop(virt)})
        else:
            continue

    return virt_act_dict, virt_inact_dict


def write_menu():
    # Setup Write Menu Loop

    os.system('cls')
    mm_choice = None
    while mm_choice != "q":
        print(
            """
            Options Menu
            -------------
            
            Q - Quit.
            1 - Write the active virtual servers to a file.
            2 - Write the inactive virtual servers to a file.
            3 - Write all LTM pool member stats.
            4 - Print a virtual servers pool members stats to the screen.
            """
        )

        mm_choice = input("Choice: ").lower()
        print()
        return mm_choice


def main():

    """ Main Program """

    # Get input parameters for the F5 REST API call
    username, passwd, ipaddr = get_api_params()

    # Hard set the URI for the first API call
    uri_ext = 'pool/members/stats'

    # Make REST API Calls for LTM Pool stats
    ltm_stats = f5api_get_call(username, passwd, ipaddr, uri_ext)
    os.system('cls')

    # Change the URI for the second API call
    uri_ext = 'virtual'
    
    # Make REST API Calls for Virtual server details
    my_ltm_virt = f5api_get_call(username, passwd, ipaddr, uri_ext)
    os.system('cls')

    # Create new dictionary with selected virtual server parameters
    virt_dict = create_virt_dict(my_ltm_virt)

    # Create an active & inactive dictionary of virtual srvs based on pool stats
    virt_act_dict, virt_inact_dict = xref_pools(virt_dict, ltm_stats)

    wm_val = None
    while wm_val != 'q':
        wm_val = write_menu()
        match wm_val:
            case '1':
                os.system('cls')
                print('\nWriting active virtual servers to a .csv file')
                write_api(virt_act_dict, 'active')
            case '2':
                os.system('cls')
                print('\nWriting inactive virtual servers to a .csv file')
                write_api(virt_inact_dict, 'inactive')
            case '3':
                os.system('cls')
                print('\nWriting LTM pool member stats to a .csv')
                write_poolmem_stats(virt_dict)
            case '4':
                os.system('cls')
                print('\nPrinting virtual servers pool members stats.')
                print_poolmem_stats(virt_dict)   
            case 'q':
                break
            case _:
                os.system('cls')
                print('\Invalid input please try again.')
                input('\nPress Enter to try again.')

    input('\nPress enter to exit script ')


if __name__ == "__main__":

    main()
