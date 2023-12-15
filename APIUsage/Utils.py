# Import necessary modules
import QueriesAndMutations as QM
from .API import Get_Access_Token
from .APIRequests import API_Request, Set_Headers
import Config
import requests
import operator

# Define the API endpoint
url = 'https://graphql.anilist.co'

# Token and header related functions: These functions are related to setting and checking the access token.

def Set_Access_Token():
    global headers
    config = Config.load_config('config.json')
    try:
        if config['ACCESS_TOKEN'] is not None:
            # Get the access token
            access_token = config['ACCESS_TOKEN']
            
            # Define the headers for the API request
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            Set_Headers(headers)
        else:
            print("No access token found.")
            config['ACCESS_TOKEN'] = Get_Access_Token()
            Config.save_config(config, 'config.json')
            Config.Set_Environment_Variables(config)
    except TypeError:
        print("No config file found")
        return

def Check_Access_Token():
    try:
        query = QM.Queries.Check_Authentication()
        response = requests.post(url, json={'query': query}, headers=headers)
        status_code_errors = {401: "Error: Invalid Access Token", 400: "Error: Invalid Access Token"}
        if response.status_code in status_code_errors:
            print(status_code_errors[response.status_code])
            return True
        print("\nToken is valid.\n")
        return False
    except NameError:
        Set_Access_Token()
        return Check_Access_Token()

# User ID related functions: These functions are related to getting user IDs.

def Get_User_ID():
    global user_id
    query = QM.Queries.Check_Authentication()
    response = API_Request(query)
    user_id = response['data']['Viewer']['id']
    return response['data']['Viewer']['id']

def Get_User_ID_From_Username(username):
    query, variables = QM.Queries.Get_User_ID_Query(username)
    response = API_Request(query, variables)
    try:
        return response['data']['User']['id']
    except TypeError:
        print(f"Error: User {username} not found")
        return None

# Follow data related functions: These functions are related to getting follow data.

def get_follow_data(query_func, message, key, page=1):
    hasNextPage = True
    ids = []

    while hasNextPage:
        query, variables = query_func(user_id, page)
        response = API_Request(query, variables)

        for user in response['data']['Page'][key]:
            ids.append(user['id'])

        print(f"{message}, Page {page} ID's: {ids[-len(response['data']['Page'][key]):]}")
        hasNextPage = response['data']['Page']['pageInfo']['hasNextPage']
        page += 1
    return ids

def Get_Followers():
    return get_follow_data(QM.Queries.Follower_Query, "Checking Followers", 'followers')

def Get_Following():
    return get_follow_data(QM.Queries.Following_Query, "Checking Following", 'following')

# Comparison functions: These functions are related to comparing followers and following.

def Compare_Followers(followers, following, operation):
    result = operation(set(following), set(followers))
    return list(result)

def Get_Mutual_Followers():
    followers = Get_Followers()
    print()
    following = Get_Following()
    print()
    return Compare_Followers(followers, following, operator.and_)

def Get_Not_Followed_Followers():
    followers = Get_Followers()
    print()
    following = Get_Following()
    print()
    return Compare_Followers(followers, following, operator.sub)

# Input functions: These functions are related to getting user input.

def Get_Valid_Input(prompt, valid_inputs=None, validation_func=None):
            while True:
                user_input = input(prompt)
                if valid_inputs and user_input in valid_inputs:
                    return user_input
                elif validation_func and validation_func(user_input):
                    return int(user_input)
                else:
                    print("Invalid input. Please try again.")

def Is_Positive_Integer(s):
    return s.isdigit() and int(s) > 0