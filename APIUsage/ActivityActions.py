# Import necessary modules
import QueriesAndMutations as QM
from .APIRequests import API_Request
from .Utils import Get_Following, Get_User_ID, Get_Valid_Input, Is_Positive_Integer, Is_Valid_Time_Period, Convert_Time_To_Seconds
from .UserActions import Follow_User, Unfollow_User, Like_Activity
import Config
import requests
import time
import keyboard

def Get_Global_Activities(total_people_to_follow):
    page = 1
    people_followed = 0
    following = Get_Following()
    unfollowed_ids = Config.load_unfollowed_ids()
    print()

    while people_followed < total_people_to_follow:
        query, variables = QM.Queries.Global_Activity_Feed_Query(page)
        response = API_Request(query, variables)

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
            response = API_Request(query, variables)

            if response is None:
                failed_requests += 1
                break

            # Like the activity if it was not liked before and the activity's user ID is not the viewer's ID
            activities = [activity for activity in response['data']['Page']['activities'] if activity and 'isLiked' in activity and not activity['isLiked'] and ('user' not in activity or activity['user']['id'] != viewer_ID) and ('recipientId' not in activity or activity['recipientId'] == user_id)]

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

def Like_Following_Activities(refresh_interval, total_pages):
    page = 1
    last_checked_page = 1
    pages_without_likes = 0
    start_time = time.time()
    stop = False
    total_likes = 0
    failed_requests = 0
    already_liked = 0
    timer_reset = False
    
    viewer_ID = Get_User_ID()

    def set_stop(e):
        nonlocal stop
        stop = True

    keyboard.on_press_key('F12', set_stop)

    while not stop:  # Run until 'F12' is pressed
        if page == total_pages + 1:
            print("\nPage limit reached. Resetting to page 1.")
            time.sleep(5)
            page = 1
        elif total_pages >= 5 and pages_without_likes >= 2 and timer_reset:
                page = last_checked_page if last_checked_page > 1 else 1
                pages_without_likes = 0
                timer_reset = False
                print(f"\nNo activities liked after 2 pages. Skipping to page {last_checked_page}")

        query, variables = QM.Queries.Following_Activity_Feed_Query(page)
        while True:
            try:
                response = API_Request(query, variables)
                break
            except requests.exceptions.ConnectionError:
                print("A connection error occurred. Retrying...")
        following_activity_feed = response['data']['Page']['activities']
        print(f"\nChecking Page {page} for following activity feed")

        page_likes = 0
        for activity in following_activity_feed:
            try:
                if activity['isLiked']:
                    already_liked += 1
                    continue
            except:
                continue

            user_id = activity['user']['id'] if 'user' in activity else None
            if user_id != viewer_ID:
                activity_liked = Like_Activity(activity['id'])
                if activity_liked:
                    print(f"Liked activity with ID: {activity['id']}, User ID: {user_id}")
                    total_likes += 1
                    page_likes += 1
                else:
                    print(f"Error: Activity with ID: {activity['id']}, User ID: {user_id}\n")
                    failed_requests += 1

            if stop:
                break

        if stop:
            break

        if page_likes > 0:
            pages_without_likes = 0
        else:
            pages_without_likes += 1

        if timer_reset is False:
            last_checked_page = page
        page += 1

        if time.time() - start_time >= refresh_interval * 60 and not timer_reset:
            print(f"\nRefreshing following activity feed after {refresh_interval} minutes")
            page = 1
            start_time = time.time()
            timer_reset = True
            pages_without_likes = 0

    print(f"\nTotal likes: {total_likes}")
    print(f"Activities skipped: {already_liked}")
    print(f"Failed requests: {failed_requests}")

    keyboard.unhook_all()

def Get_Liked_Activities(perPage, totalPages, include_message_activity):
    viewer_ID = Get_User_ID()

    user_likes_count = {}
    following_users = Get_Following()  # Assuming this function returns a list of user IDs
    not_appeared_users = {user_id: 0 for user_id in following_users}
    activity_count = 0

    follow_unfollowed_users = Get_Valid_Input("\nWould you like to follow users who like your activity but you are not following them? (y/n): ", valid_inputs=['y', 'n']).lower() == 'y'
    followed_users = []

    # Load the unfollowed IDs
    unfollowed_ids = Config.load_unfollowed_ids()
    
    # Ask the user for a time frame
    time_back = Get_Valid_Input("\nHow far back should it check for activities? Enter a number for days, or append 'w' for weeks, 'm' for months, or 'y' for years (e.g., '2w' for 2 weeks): ", validation_func=Is_Valid_Time_Period)
    time_back_seconds = Convert_Time_To_Seconds(time_back)
    end_time = int(time.time())  # Current time in Unix timestamp
    start_time = end_time - time_back_seconds # Subtract the number of seconds in the specified number of days

    # Set the threshold for the number of activities a user needs to have liked
    likes_threshold = Get_Valid_Input("\nEnter the minimum number of activities a user needs to have liked to be included in the list: ", validation_func=Is_Positive_Integer)

    for page in range(1, totalPages + 1):
        print(f"\nChecking page {page}...")
        query, variables = QM.Queries.User_Activity_Feed_Query(viewer_ID, page, perPage, include_message_activity, start_time, end_time)
        response = API_Request(query, variables)

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

                    # If the user is not in the following list, not in the unfollowed list, not in the list already, and the user has chosen to follow unfollowed users, add them to the list to be followed
                    if user_id not in following_users and user_id not in unfollowed_ids and follow_unfollowed_users and user_id != viewer_ID and user_id not in followed_users:
                        followed_users.append(user_id)

    # Follow the users in the followed_users list
    for user_id in list(followed_users):  # Use list() to create a copy of the list for iteration
        if user_likes_count.get(user_id, 0) >= likes_threshold:  # Only follow users who have liked more than the threshold number of activities
            if Follow_User(user_id):
                following_users.append(user_id)  # Add the user ID to the following_users list
        else:
            # If the user's like count is not above the threshold, remove them from the followed_users list
            followed_users.remove(user_id)

    if followed_users:
        print(f"\nFollowed Users: {followed_users}")

    print(f"\nTotal Activities processed: {activity_count}")

    # Sort the dictionary items by count in descending order
    sorted_user_likes = sorted(user_likes_count.items(), key=lambda item: item[1], reverse=True)

    print(f"\nUser Likes Count ({len(sorted_user_likes)}):")
    for user_id, count in sorted_user_likes:  # Iterate over the sorted items
        if count >= likes_threshold:  # Only display users who have liked at least likes_threshold activities
            print(f"User ID: {user_id}, Count: {count}")
        else:
            # If the count is not greater than the likes_threshold, remove the user from the user_likes_count list and add them to the not_appeared_users list
            del user_likes_count[user_id]
            # Only add the user to the not_appeared_users list if they are in the following_users list
            if user_id in following_users:
                not_appeared_users[user_id] = 0

    display_not_appeared = input("\nDisplay users not appeared? (y/n): ").lower() == 'y'
    if display_not_appeared:
        # Load the excluded IDs
        excluded_ids = Config.load_excluded_ids()

        # Exclude the users from the unfollowed IDs list
        not_appeared_users = {user_id: count for user_id, count in not_appeared_users.items() if user_id not in excluded_ids}

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