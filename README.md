# F5

###F5 REST API

####Basic Authentication

- '**f5api_call.py**', Makes a F5 GET RESTFUL API call using an basic authentication
- '**f5_ltm_stats_call.py**', Using basic authentication this imports an F5 LTM Virtual Server details and Pool stats from API. Coverts
    the JSON output to a dictionary and extracts the relevant information to
    ascertain if that Virtual Server/LTM Pool is in use or not

####Token Authentication

- '**get_f5_token.py**', Retrieves an F5 authentication token for F5 RESTFUL API calls.
- '**f5api_token_call.py**', Makes a F5 GET RESTFUL API call using an authentication token
- '**f5_ltm_stats_token_call.py**', Using a token this imports an F5 LTM Virtual Server details and Pool stats from API. Coverts
    the JSON output to a dictionary and extracts the relevant information to
    ascertain if that Virtual Server/LTM Pool is in use or not
