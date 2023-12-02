from Config import load_config
from API import Get_Access_Token
import QueriesAndMutations as QM
import requests
import time

# Define the API endpoint
url = 'https://graphql.anilist.co'

# Function to handle API requests
def api_request(query, variables=None):
    # Send a POST request to the API endpoint
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    
    # Check the rate limit headers
    rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
    rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))
    
    # If the rate limit has been hit, print a message and wait
    if response.status_code == 429:
        wait_time = rate_limit_reset - int(time.time())
        if wait_time < 0:
            print(f"\nReset time: {wait_time} Seconds\nError: Rate limit reset time is in the past.")
            wait_time = 65
            print(f"Waiting for {wait_time} seconds.\n")
            time.sleep(wait_time)
        else:
            print(f"\nRate limit hit. Waiting for {wait_time} seconds.")
            time.sleep(wait_time)
        return api_request(query, variables)

    # If the rate limit is close to being hit, print a warning
    elif rate_limit_remaining < 5:
        print(f"\nWarning: Only {rate_limit_remaining} requests remaining until rate limit reset.")

    # If the request was successful, return the JSON response
    if response.status_code == 200:
        return response.json()
    # If the request was not successful, print an error message and return None
    else:
        print(f"\nFailed to retrieve data. Status code: {response.status_code}\nAssumming title is not on list\n")
        return None

def Set_Access_Token():
    global headers
    config = load_config('config.json')
    try:
        if config['ACCESS_TOKEN'] is not None:
            # Get the access token
            access_token = config['ACCESS_TOKEN']
            
            # Define the headers for the API request
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
        else:
            print("No access token found.")
            Get_Access_Token()
    except TypeError:
        print("No config file found")
        return
    
def Check_Access_Token():
    query = QM.Queries.Check_Authentication()
    response = requests.post(url, json={'query': query}, headers=headers)
    try:
        # Send a POST request to the API endpoint
        response = requests.post(url, json={'query': query}, headers=headers)
    except:
        print("Error: Cannot resolve graphql.anilist.co")
        print("Possibly due to internet connection\n")
        return

    # If the status code is 401 (Unauthorized), the access token is invalid
    if response.status_code == 401 or response.status_code == 400:
        print("Error: Invalid Access Token")
        return True

    # If the status code is not 401, the access token is valid
    print("\nToken is valid.\n")
    return False

def Get_User_ID():
    global user_id
    query = QM.Queries.Check_Authentication()
    response = api_request(query)
    user_id = response['data']['Viewer']['id']
    return response['data']['Viewer']['id']

def Get_Followers():
    page = 1
    hasNextPage = True
    follower_ids = []

    while hasNextPage:
        query, variables = QM.Queries.Follower_Query(user_id, page)
        response = api_request(query, variables)

        # Add the ids to the list
        for follower in response['data']['Page']['followers']:
            follower_ids.append(follower['id'])

        # Check if there are more pages
        hasNextPage = response['data']['Page']['pageInfo']['hasNextPage']

        # Go to the next page
        page += 1

    return follower_ids

def Get_Following():
    page = 1
    hasNextPage = True
    following_ids = []

    while hasNextPage:
        query, variables = QM.Queries.Following_Query(user_id, page)
        response = api_request(query, variables)

        # Add the ids to the list
        for following in response['data']['Page']['following']:
            following_ids.append(following['id'])

        # Check if there are more pages
        hasNextPage = response['data']['Page']['pageInfo']['hasNextPage']

        # Go to the next page
        page += 1

    return following_ids

