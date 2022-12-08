#!/usr/bin/env python

""" Makes an API call to an F5 LTM appliance and returns results """

# Author: Wayne Bellward
# Date: 08/12/2022

import os
import requests
import ipaddress
from pprint import pprint
from getpass import getpass
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning
    

def f5api_get_call(ipaddr, token, uri_ext):

    """ Makes two F5 API calls for Virtual Server details and LTM Pool stats """
    
    # Disable warning from using unsigned certificate
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    # Form Base URI
    base_uri = 'https://{}/mgmt/tm/ltm/'.format(ipaddr)

    # Form complete API call URL
    api_url = base_uri + uri_ext

    # Open Requests Session and set relevant attributes
    api_call = requests.session()
    api_call.verify = False
    api_call.headers.update({'Content-Type':'application/json',
                             'X-F5-Auth-Token': token})

    # Make REST API call and perform error handling
    try:
        myapi = api_call.get(api_url, timeout=5)
        myapi.raise_for_status()
    except requests.exceptions.HTTPError as err_h:
        os.system('cls')
        print('\nHTTP Error: {}'.format(err_h, api_url))
        input('\nPress Enter to Exit')
        raise SystemExit(err_h)
    except requests.exceptions.ConnectionError as err_c:
        os.system('cls')
        print ('\nError Connecting: {}'.format(err_c))
        print('\nIs the F5 LTM IP address correct, or reachable?')
        input('\nPress Enter to Exit')
        raise SystemExit(err_c)
    except requests.exceptions.Timeout as err_t:
        os.system('cls')
        print('\nTimeout Error: {}'.format(err_t))
        print('\nIs the F5 LTM IP address you entered correct, or is there '
              'a problem with the LTM API configuration for your account?')
        input('\nPress Enter to Exit')
        raise SystemExit(err_t)
    except requests.exceptions.TooManyRedirects as err_tr:
        os.system('cls')
        print('\nToo many redirects: {}'.format(err_tr))
        input('\nPress Enter to Exit')
        raise SystemExit(err_tr)
    except requests.exceptions.RequestException as err_re:
        os.system('cls')
        print('\nSerious unknown error encountered, exiting program, please rerun'
              ' and try again.')
        input('\nPress Enter to Exit')
        raise SystemExit(err_re)

    return myapi.json()


def write_api(myapi):
    
    """ Write REST API call response to a text file with pretty print """

    now = datetime.now()
    dt_str = now.strftime('%d-%m-%y_%H%M%S')

    suffix = '_' + dt_str

    filename = input('\n\nPlease enter the name of the file you wish to save '
                     'without the file extension: ')
    filename = filename + suffix +'.txt'
             
    with open(filename, 'w') as file:
        pprint(myapi, file)
                
    print('\nThe file has been written to timestamped "', filename,
          '" in the local directory', sep = '')
    print()


def main():

    """ Main Program """

    # Input F5 authentication credentials for REST API Call
    print('\nF5 REST API Authentication')
    print('-'*30,)
    username = input('\nPlease enter your username: ')
    passwd = getpass('Please enter your password: ')
    os.system('cls')

    # Intialise variable
    ipaddr = False
    
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

    # Get authentication token
    token = get_token(username, passwd, ipaddr)

    # Input URI extension for specific API call
    print('\nThe Base URI is: https://{}/mgmt/tm/ltm/'.format(ipaddr))
    uri_ext = input('Please enter the URI extension: ')

    # Make REST API Get Call
    myapi = f5api_get_call(ipaddr, token, uri_ext)

    # Write the REST API response to a file
    write_api(myapi)

    input('\nPress Enter to Exit')

if __name__ == "__main__":

    main()
