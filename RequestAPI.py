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
    response_json = response.json()
    #print(response_json)

    # If the response contains errors, print them
    if 'errors' in response_json:
        for error in response_json['errors']:
            print(f"Error: {error['message']}. Status: {error['status']}.")

    # Check the rate limit headers
    rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
    rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))
    
    # If the rate limit has been hit, print a message and wait
    if response.status_code == 429:
        wait_time = rate_limit_reset - int(time.time())
        # Happens alot when program is rate limited from just doing one feature. Not full site rate limited.
        if wait_time < 0:
            print(f"\nReset time: {wait_time} Seconds\nError: Rate limit reset time is in the past.")
            print("Most likely 1 minute rate limited from a specific feature.")
            wait_time = 60
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
        print(f"\nFailed to retrieve data. Status code: {response.status_code}\n")
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

        # Print the ids on this page
        print(f"Checking Followers, Page {page} ID's: {follower_ids[-len(response['data']['Page']['followers']):]}")

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

        # Print the ids on this page
        print(f"Checking Following, Page {page} ID's: {following_ids[-len(response['data']['Page']['following']):]}")

        # Check if there are more pages
        hasNextPage = response['data']['Page']['pageInfo']['hasNextPage']

        # Go to the next page
        page += 1

    return following_ids

def Unfollow_User(id):
    query, variables = QM.Mutations.Follow_Mutation(id)
    response = api_request(query, variables)
    if response is not None:
        if response['data']['ToggleFollow']['isFollowing'] == False:
            print(f"Unfollowed {response['data']['ToggleFollow']['name']} with ID: {id}")
        else:
            print(f"Error: {response['data']['ToggleFollow']['name']} already unfollowed with ID: {id}")
            api_request(query, variables)
    else:
        print(f"Failed to unfollow user with ID: {id}")

def Follow_User(id):
    query, variables = QM.Mutations.Follow_Mutation(id)
    response = api_request(query, variables)
    if response is not None:
        if response['data']['ToggleFollow']['isFollowing'] == True:
            print(f"Followed {response['data']['ToggleFollow']['name']} with ID: {id}")
        else:
            print(f"Error: {response['data']['ToggleFollow']['name']} already followed with ID: {id}")
            api_request(query, variables)
    else:
        print(f"Failed to follow user with ID: {id}")

def Get_Global_Activities(pages, total_people_to_follow):
    page = 1
    activity_ids = []
    people_followed = 0
    following = Get_Following()

    while page <= pages and people_followed < total_people_to_follow:
        query, variables = QM.Queries.Global_Activity_Feed_Query(page)
        response = api_request(query, variables)
        print()
        
        # Add the ids to the list and follow the user if they are not following the main user
        for activity in response['data']['Page']['activities']:
            activity_ids.append(activity['id'])
            if activity['user']['id'] not in following and people_followed < total_people_to_follow:
                Follow_User(activity['user']['id'])
                following.append(activity['user']['id'])
                people_followed += 1

        # Print the ids on this page
        print(f"\nPage {page} ids: {activity_ids[-len(response['data']['Page']['activities']):]}")

        # Go to the next page
        page += 1

    return activity_ids

def Like_Activity(id):
    query, variables = QM.Mutations.Like_Mutation(id)
    response = api_request(query, variables)
    #print(response)
    if response is not None:
        for item in response['data']['ToggleLike']:
            if item['id'] == id:
                print(f"Liked activity with ID: {id}")
                break
    else:
        print(f"Failed to like activity with ID: {id}")

def Like_Activities(total_activities_to_like, include_message_activity):
    activities_liked = 0
    following_users = Get_Following()
    print()

    for following_user_id in following_users:
        page = 1
        activities_liked = 0
        print()
        while activities_liked < total_activities_to_like:
            query, variables = QM.Queries.User_Activity_Feed_Query(following_user_id, page, include_message_activity)
            response = api_request(query, variables)

            # Like the activity if it was not liked before
            for activity in response['data']['Page']['activities']:
                if activity and 'isLiked' in activity and not activity['isLiked'] and activities_liked < total_activities_to_like:
                    Like_Activity(activity['id'])
                    print(f"Liked activity with ID: {activity['id']} from user with ID: {following_user_id}")
                    activities_liked += 1

            # Go to the next page
            page += 1