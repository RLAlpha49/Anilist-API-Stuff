# Import necessary modules
from API import Get_Access_Token
import QueriesAndMutations as QM
import Config
import requests
import time
import operator
import keyboard


# Define the API endpoint
url = 'https://graphql.anilist.co'

def handle_rate_limit(response):
    rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
    rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))
    
    if response.status_code == 429:
        wait_time = rate_limit_reset - int(time.time())
        if wait_time < 0:
            wait_time = 60
        print(f"\nRate limit hit. Waiting for {wait_time} seconds.\n")
        time.sleep(wait_time)
    elif rate_limit_remaining < 5:
        print(f"Warning: Only {rate_limit_remaining} requests remaining until rate limit reset.")

def api_request(query, variables=None):
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    handle_rate_limit(response)
    #print(response.json())
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        return api_request(query, variables)
    else:
        print(f"\nFailed to retrieve data. Status code: {response.status_code}\n")
        return None
    
def get_follow_data(query_func, message, key, page=1):
    hasNextPage = True
    ids = []

    while hasNextPage:
        query, variables = query_func(user_id, page)
        response = api_request(query, variables)

        for user in response['data']['Page'][key]:
            ids.append(user['id'])

        print(f"{message}, Page {page} ID's: {ids[-len(response['data']['Page'][key]):]}")
        hasNextPage = response['data']['Page']['pageInfo']['hasNextPage']
        page += 1

    return ids

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

def Get_User_ID():
    global user_id
    query = QM.Queries.Check_Authentication()
    response = api_request(query)
    user_id = response['data']['Viewer']['id']
    return response['data']['Viewer']['id']

def Get_User_ID_From_Username(username):
    query, variables = QM.Queries.Get_User_ID_Query(username)
    response = api_request(query, variables)
    try:
        return response['data']['User']['id']
    except TypeError:
        print(f"Error: User {username} not found")
        return None

def Get_Followers():
    return get_follow_data(QM.Queries.Follower_Query, "Checking Followers", 'followers')

def Get_Following():
    return get_follow_data(QM.Queries.Following_Query, "Checking Following", 'following')

def Toggle_Follow_User(id, desired_status, success_message, error_message):
    query, variables = QM.Mutations.Follow_Mutation(id)
    response = api_request(query, variables)
    if response is not None:
        if response['data']['ToggleFollow']['isFollowing'] == desired_status:
            print(success_message.format(response['data']['ToggleFollow']['name'], id))
        else:
            print(error_message.format(response['data']['ToggleFollow']['name'], id))
            api_request(query, variables)
    else:
        print(f"Failed to update follow status for user with ID: {id}")

def Unfollow_User(id):
    return Toggle_Follow_User(id, False, "Unfollowed {} with ID: {}", "Error: {} already unfollowed with ID: {}")

def Follow_User(id):
    return Toggle_Follow_User(id, True, "Followed {} with ID: {}", "Error: {} already followed with ID: {}")

def Get_Global_Activities(total_people_to_follow):
    page = 1
    people_followed = 0
    following = Get_Following()
    unfollowed_ids = Config.load_unfollowed_ids()
    print()

    while people_followed < total_people_to_follow:
        query, variables = QM.Queries.Global_Activity_Feed_Query(page)
        response = api_request(query, variables)

        # Add the ids to the list and follow the user if they are not following the main user
        activity_ids = (activity['id'] for activity in response['data']['Page']['activities'] if 'user' in activity)
        for activity_id in activity_ids:
            user_id = next((activity['user']['id'] for activity in response['data']['Page']['activities'] if activity['id'] == activity_id), None)
            if user_id and user_id not in following and user_id not in unfollowed_ids and people_followed < total_people_to_follow:
                Follow_User(user_id)
                following.append(user_id)
                people_followed += 1

        # Go to the next page
        page += 1

    return list(activity_ids)

def Like_Activity(id):
    query, variables = QM.Mutations.Like_Mutation(id)
    response = api_request(query, variables)
    if response is not None and 'errors' not in response:
        return True
    else:
        print(f"Failed to like activity with ID: {id}")
        return False

def Like_Activities(total_activities_to_like, include_message_activity, user_list=None):
    if user_list is None:
        user_list = Get_Following()
    expected_likes = total_activities_to_like * len(user_list)
    print(f"\nExpected number of likes: {expected_likes}\n")
    total_likes = 0

    # Add counters
    no_activities_users = 0
    failed_requests = 0

    # Add list for users with no more activities
    no_activities_user_ids = []
    
    # Get Viewer ID
    viewer_ID = Get_User_ID()

    for user_id in user_list:
        page = 1
        activities_liked = 0
        while activities_liked < total_activities_to_like:
            query, variables = QM.Queries.User_Activity_Feed_Query(user_id, page, 50, include_message_activity)
            response = api_request(query, variables)

            if response is None:
                failed_requests += 1
                break

            # Like the activity if it was not liked before and the activity's user ID is not the viewer's ID
            activities = [activity for activity in response['data']['Page']['activities'] if activity and 'isLiked' in activity and not activity['isLiked'] and 'user' in activity and activity['user']['id'] != viewer_ID]

            for activity in activities:
                if activities_liked < total_activities_to_like:
                    activity_liked = Like_Activity(activity['id'])
                    if activity_liked:
                        print(f"Liked activity with ID: {activity['id']}, User ID: {user_id}")
                        activities_liked += 1
                        total_likes += 1
                    else:
                        print(f"Error: Activity with ID: {activity['id']}")
                        failed_requests += 1

            # If there are no more activities, break the loop
            if not response['data']['Page']['activities']:
                if not activities:
                    no_activities_users += 1
                    no_activities_user_ids.append(user_id)
                break

            # Go to the next page
            page += 1
            
        if total_activities_to_like > 1:
            print()  # Print a line after each user's activities have been processed

    print(f"\nExpected number of likes: {expected_likes}")
    print(f"Total number of likes: {total_likes}")
    print(f"Users with no activities to like: {no_activities_users}")
    print(f"Failed requests: {failed_requests}")
    print(f"User IDs with no more activities: {no_activities_user_ids}")

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

def Like_Following_Activities(refresh_interval, total_pages):
    page = 1
    start_time = time.time()
    stop = False
    total_likes = 0
    failed_requests = 0
    already_liked = 0
    
    viewer_ID = Get_User_ID()

    def set_stop(e):
        nonlocal stop
        stop = True

    keyboard.on_press_key('F12', set_stop)

    while not stop:  # Run until 'F12' is pressed
        if page == total_pages + 1:
            print("\nPage limit reached. Resetting to page 1.")
            # Sleep for 5 seconds before resetting the page
            # Mostly for if total_pages is a low number and to stop the script from running too fast
            time.sleep(5)
            page = 1
            start_time = time.time()  # Reset the start time
        
        # Get the following activity feed
        query, variables = QM.Queries.Following_Activity_Feed_Query(page)
        while True:
            try:
                response = api_request(query, variables)
                break  # If the request is successful, break the loop
            except requests.exceptions.ConnectionError:
                print("A connection error occurred. Retrying...")
        following_activity_feed = response['data']['Page']['activities']
        print(f"\nChecking Page {page} for following activity feed")

        for activity in following_activity_feed:
            try:
                if activity['isLiked']:
                    #print(f"Activity is already liked, skipping...")
                    already_liked += 1
                    continue  # Skip this iteration and move to the next activity
            except:
                # Empty activity or no 'isLiked' key
                continue  # Skip this iteration and move to the next activity

            user_id = activity['user']['id'] if 'user' in activity else None
            if user_id != viewer_ID:
                activity_liked = Like_Activity(activity['id'])
                if activity_liked:
                    print(f"Liked activity with ID: {activity['id']}, User ID: {user_id}")
                    total_likes += 1
                else:
                    print(f"Error: Activity with ID: {activity['id']}, User ID: {user_id}\n")
                    failed_requests += 1
            else:
                print(f"\nActivity is from the viewer, skipping...")

            # Check if 'F12' has been pressed
            if stop:
                break  # Break out of the for loop

        # Check if 'F12' has been pressed
        if stop:
            break  # Break out of the while loop

        page += 1

        # Refresh the following activity feed every refresh_interval minutes
        if time.time() - start_time >= refresh_interval * 60:
            print(f"\nRefreshing following activity feed after {refresh_interval} minutes")
            start_time = time.time()  # Reset the start time
            page = 1  # Go to the beginning activity feed

    print(f"\nTotal likes: {total_likes}")
    print(f"Activities skipped liking: {already_liked}")
    print(f"Failed requests: {failed_requests}")

    keyboard.unhook_all()

def Get_Liked_Activities(perPage, totalPages, include_message_activity):
    viewer_ID = Get_User_ID()

    user_likes_count = {}
    following_users = Get_Following()  # Assuming this function returns a list of user IDs
    not_appeared_users = {user_id: 0 for user_id in following_users}
    activity_count = 0
    
    follow_unfollowed_users = input("\nWould you like to follow users who like your activity but you are not following them? (y/n): ").lower() == 'y'
    followed_users = []
    
    # Load the unfollowed IDs
    unfollowed_ids = Config.load_unfollowed_ids()

    for page in range(1, totalPages + 1):
        print(f"\nChecking page {page}...")
        query, variables = QM.Queries.User_Activity_Feed_Query(viewer_ID, page, perPage, include_message_activity)
        response = api_request(query, variables)

        activities = response['data']['Page']['activities']
        if not activities:
            print("No more activities to retrieve.")
            break
        
        for activity in activities:
            activity_count += 1
            if 'id' in activity:
                print(f"Activity ID: {activity['id']}")
            else:
                print("Activity does not have an ID.")
            if 'likes' in activity:
                for user in activity['likes']:
                    user_id = user['id']
                    if user_id in user_likes_count:
                        user_likes_count[user_id] += 1
                    else:
                        user_likes_count[user_id] = 1
                    if user_id in not_appeared_users:
                        del not_appeared_users[user_id]

                    # If the user is not in the following list, not in the unfollowed list, and the user has chosen to follow unfollowed users, follow them
                    if user_id not in following_users and user_id not in unfollowed_ids and follow_unfollowed_users:
                        Follow_User(user_id)
                        followed_users.append(user_id)  # Add the user ID to the followed_users list
                        following_users.append(user_id)  # Add the user ID to the following_users list
                        
    if followed_users:
        print(f"\nFollowed Users: {followed_users}")

    print(f"\nTotal Activities processed: {activity_count}")

    print(f"\nUser Likes Count ({len(user_likes_count)}):")
    for user_id, count in sorted(user_likes_count.items(), key=lambda item: item[1], reverse=True):
        print(f"User ID: {user_id}, Count: {count}")

    display_not_appeared = input("\nDisplay users not appeared? (y/n): ").lower() == 'y'
    if display_not_appeared:
        # Load the excluded IDs
        excluded_ids = Config.load_excluded_ids()

        # Exclude the users from the unfollowed IDs list
        not_appeared_users = [user_id for user_id in not_appeared_users if user_id not in excluded_ids]
        
        print(f"\nUsers Not Appeared ({len(not_appeared_users)}): {not_appeared_users}")
        
        unfollow_not_appeared = input("\nUnfollow users not appeared? (y/n): ").lower() == 'y'
        if unfollow_not_appeared:
            unfollowed_ids = []
            for user_id in not_appeared_users:
                # Call the function to unfollow the user
                Unfollow_User(user_id)
                unfollowed_ids.append(user_id)

            save_unfollowed = input("\nSave unfollowed user IDs? (y/n): ").lower() == 'y'
            if save_unfollowed:
                Config.save_unfollowed_ids(set(unfollowed_ids))