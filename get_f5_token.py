#!/usr/bin/env python

""" Gets F5 Token for API authentication """

# Author: Wayne Bellward
# Date: 08/12/2022

import requests


def get_token(username, passwd, ipaddr):

    """ Get F5 authentication token """

    body = {
        "username": username,
        "password": passwd,
        "loginProviderName": "tmos"
    }

    token_response = requests.post(
        f'https://{ipaddr}/mgmt/shared/authn/login',
        verify=False,
        auth=(username, passwd),json=body)\
        .json()

    token = token_response['token']['token']

    return token


def main():

    """ Main Program """

    print('This module is designed to be imported, not run directly')
    

if __name__ == "__main__":

    main()
