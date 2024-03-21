"""
This module contains the actions related to activities.
"""

# pylint: disable=C0103, E0401

# Import necessary modules
import time

import Config
import keyboard  # pylint: disable=C0411
import QueriesAndMutations as QM
import requests  # pylint: disable=C0411

from .APIRequests import API_Request  # pylint: disable=E0402
from .UserActions import (  # pylint: disable=E0402
    Follow_User,
    Like_Activity,
    Unfollow_User,
)
from .Utils import (  # pylint: disable=E0402
    Convert_Time_To_Seconds,
    Get_Following,
    Get_User_ID,
    Get_Valid_Input,
    Is_Positive_Integer,
    Is_Valid_Time_Period,
)


def Get_Global_Activities(total_people_to_follow):
    """
    Retrieves global activities and follows users.

    This function retrieves global activities from the Anilist API and follows
    users who are not already being followed and have not been unfollowed
    before. It stops when it has followed the specified number of people.

    Args:
        total_people_to_follow (int): The total number of people to follow.

    Returns:
        list: A list of IDs of the activities retrieved in the last API request.
    """
    page = 1
    people_followed = 0
    following = Get_Following()
    unfollowed_ids = Config.load_unfollowed_ids()
    print()

    activity_ids = []

    while people_followed < total_people_to_follow:
        query, variables = QM.Queries.Global_Activity_Feed_Query(page)
        response = API_Request(query, variables)

        # Add the ids to the list and follow the user if they are not following the main user
        activity_ids = (
            activity["id"]
            for activity in response["data"]["Page"]["activities"]
            if "user" in activity
        )
        for activity_id in activity_ids:
            user_id = next(
                (
                    activity["user"]["id"]
                    for activity in response["data"]["Page"]["activities"]
                    if activity["id"] == activity_id
                ),
                None,
            )
            if (
                user_id
                and user_id not in following
                and user_id not in unfollowed_ids
                and people_followed < total_people_to_follow
            ):
                Follow_User(user_id)
                following.append(user_id)
                people_followed += 1

        # Go to the next page
        page += 1

    return list(activity_ids)


def Like_Activities(total_activities_to_like, include_message_activity, user_list=None):
    """
    Likes activities of users.

    This function likes a specified number of activities of each user in a list.
    If no list is provided, it likes activities of the users the viewer is following.
    It can also include message activities.

    Args:
        total_activities_to_like (int): The total number of activities to like per user.
        include_message_activity (bool): Whether to include message activities.
        user_list (list, optional): A list of user IDs. Defaults to None.

    Returns:
        None
    """
    if user_list is None:
        user_list = Get_Following()
    viewer_ID = Get_User_ID()

    # Initialize counters and lists
    counters = {
        "expected_likes": total_activities_to_like * len(user_list),
        "total_likes": 0,
        "no_activities_users": 0,
        "failed_requests": 0,
    }
    no_activities_user_ids = []

    print(f"\nExpected number of likes: {counters['expected_likes']}\n")

    for user_id in user_list:
        page = 1
        activities_liked = 0
        while activities_liked < total_activities_to_like:
            query, variables = QM.Queries.User_Activity_Feed_Query(
                user_id, page, 50, include_message_activity
            )
            response = API_Request(query, variables)

            if response is None:
                counters["failed_requests"] += 1
                break

            # Like the activity if it was not liked before & the activity's user ID is not viewer ID
            activities = [
                activity
                for activity in response["data"]["Page"]["activities"]
                if activity
                and "isLiked" in activity
                and not activity["isLiked"]
                and ("user" not in activity or activity["user"]["id"] != viewer_ID)
                and (
                    "recipientId" not in activity or activity["recipientId"] == user_id
                )
            ]

            for activity in activities:
                if activities_liked < total_activities_to_like:
                    activity_liked = Like_Activity(activity["id"])
                    if activity_liked:
                        print(
                            f"Liked activity with ID: {activity['id']}, User ID: {user_id}"
                        )
                        activities_liked += 1
                        counters["total_likes"] += 1
                    else:
                        print(f"Error: Activity with ID: {activity['id']}")
                        counters["failed_requests"] += 1

            # If there are no more activities, break the loop
            if not response["data"]["Page"]["activities"]:
                if not activities:
                    counters["no_activities_users"] += 1
                    no_activities_user_ids.append(user_id)
                break

            # Go to the next page
            page += 1

        if total_activities_to_like > 1:
            print()  # Print a line after each user's activities have been processed

    print(f"\nExpected number of likes: {counters['expected_likes']}")
    print(f"Total number of likes: {counters['total_likes']}")
    print(f"Users with no activities to like: {counters['no_activities_users']}")
    print(f"Failed requests: {counters['failed_requests']}")
    print(f"User IDs with no more activities: {no_activities_user_ids}")


def Like_Following_Activities(refresh_interval, total_pages):
    """
    Likes activities of the users the viewer is following.

    This function likes activities from the following activity feed. It stops
    when it has liked activities from the specified number of pages or when 'F12'
    is pressed. It refreshes the activity feed after a specified interval.

    Args:
        refresh_interval (int): The interval in minutes after which to refresh the activity feed.
        total_pages (int): The total number of pages to like activities from.

    Returns:
        None
    """
    # Initialize counters and flags
    state = {
        "page": 1,
        "last_checked_page": 1,
        "pages_without_likes": 0,
        "start_time": time.time(),
        "stop": False,
        "total_likes": 0,
        "failed_requests": 0,
        "already_liked": 0,
        "timer_reset": False,
    }

    viewer_ID = Get_User_ID()

    def set_stop():
        nonlocal state
        state["stop"] = True

    keyboard.on_press_key("F12", set_stop)

    while not state["stop"]:  # Run until 'F12' is pressed
        handle_page_limit(state, total_pages)
        handle_no_likes(state, total_pages)
        handle_activities(state, viewer_ID)
        handle_page_likes(state)
        handle_refresh_interval(state, refresh_interval)

    print(f"\nTotal likes: {state['total_likes']}")
    print(f"Activities skipped: {state['already_liked']}")
    print(f"Failed requests: {state['failed_requests']}")

    keyboard.unhook_all()


def handle_page_limit(state, total_pages):
    """
    Handles the page limit for liking activities.

    This function checks if the current page has reached the total number of pages.
    If it has, it resets the page to 1.

    Args:
        state (dict): A dictionary that holds the state of the activity liking process.
        total_pages (int): The total number of pages to like activities from.

    Returns:
        None
    """
    if state["page"] == total_pages + 1:
        print("\nPage limit reached. Resetting to page 1.")
        time.sleep(5)
        state["page"] = 1


def handle_no_likes(state, total_pages):
    """
    Handles the scenario where no activities are liked on a page.

    This function checks if no activities have been liked after 2 pages. If so,
    it skips to the last checked page or to page 1 if the last checked page is not greater than 1.

    Args:
        state (dict): A dictionary that holds the state of the activity liking process.
        total_pages (int): The total number of pages to like activities from.

    Returns:
        None
    """
    if total_pages >= 5 and state["pages_without_likes"] >= 2 and state["timer_reset"]:
        state["page"] = (
            state["last_checked_page"] if state["last_checked_page"] > 1 else 1
        )
        state["pages_without_likes"] = 0
        state["timer_reset"] = False
        print(
            f"\nNo activities liked after 2 pages. Skipping to page {state['last_checked_page']}"
        )


def handle_activities(state, viewer_ID):
    """
    Handles the activities for a given page.

    This function sends an API request to get the activities for the current page.
    It then iterates over these activities, liking each one that is not already liked
    and that was not created by the viewer. It updates the state dictionary to keep track
    of the total number of likes, the number of likes on the current page, the number of
    activities that were already liked, and the number of failed requests.

    Args:
        state (dict): A dictionary that holds the state of the activity liking process.
        viewer_ID (str): The ID of the viewer.

    Returns:
        None
    """
    query, variables = QM.Queries.Following_Activity_Feed_Query(state["page"])
    while True:
        try:
            response = API_Request(query, variables)
            if response is not None:
                break
        except requests.exceptions.ConnectionError:
            print("A connection error occurred. Retrying...")
    following_activity_feed = response["data"]["Page"]["activities"]
    print(f"\nChecking Page {state['page']} for following activity feed")

    state["page_likes"] = 0
    for activity in following_activity_feed:
        try:
            if activity["isLiked"]:
                state["already_liked"] += 1
                continue
        except Exception:  # pylint: disable=W0718
            continue

        user_id = activity["user"]["id"] if "user" in activity else None
        if user_id != viewer_ID:
            activity_liked = Like_Activity(activity["id"])
            if activity_liked:
                print(f"Liked activity with ID: {activity['id']}, User ID: {user_id}")
                state["total_likes"] += 1
                state["page_likes"] += 1
            else:
                print(
                    f"Error: Activity with ID: {activity['id']}, User ID: {user_id}\n"
                )
                state["failed_requests"] += 1

        if state["stop"]:
            break


def handle_page_likes(state):
    """
    Handles the likes for a given page.

    This function checks if any activities were liked on the current page. If so,
    it resets the count of pages without likes. If not, it increments this count.
    It also updates the last checked page if the timer has not been reset. Finally,
    it increments the current page.

    Args:
        state (dict): A dictionary that holds the state of the activity liking process.

    Returns:
        None
    """
    if state["page_likes"] > 0:
        state["pages_without_likes"] = 0
    else:
        state["pages_without_likes"] += 1

    if state["timer_reset"] is False:
        state["last_checked_page"] = state["page"]
    state["page"] += 1


def handle_refresh_interval(state, refresh_interval):
    """
    Handles the refresh interval for the activity feed.

    This function checks if the refresh interval has passed since the start time.
    If it has and the timer has not been reset, it refreshes the activity feed by
    resetting the page, start time, timer, and count of pages without likes.

    Args:
        state (dict): A dictionary that holds the state of the activity liking process.
        refresh_interval (int): The interval in minutes after which to refresh the activity feed.

    Returns:
        None
    """
    if (
        time.time() - state["start_time"] >= refresh_interval * 60
        and not state["timer_reset"]
    ):
        print(f"\nRefreshing following activity feed after {refresh_interval} minutes")
        state["page"] = 1
        state["start_time"] = time.time()
        state["timer_reset"] = True
        state["pages_without_likes"] = 0


class ActivityProcessingContext:  # pylint: disable=R0902, R0903
    """
    A class to represent the context for processing activities.

    This class provides a way to group all the necessary information for processing activities.

    Attributes:
        viewer_ID (str): The ID of the viewer.
        perPage (int): The number of activities to retrieve per page.
        totalPages (int): The total number of pages to retrieve.
        include_message_activity (bool): Whether to include message activities.
        start_time (int): The start time for retrieving activities.
        end_time (int): The end time for retrieving activities.
        following_users (list): The list of users the viewer is following.
        unfollowed_ids (list): The list of users the viewer has unfollowed.
        follow_unfollowed_users (bool): Whether to follow users the viewer has unfollowed.
        user_likes_count (dict): A dictionary to count the likes per user.
        not_appeared_users (dict): A dictionary to track the users who have not appeared.
        followed_users (list): The list of users the viewer has followed.
    """

    def __init__(  # pylint: disable=R0913
        self,
        viewer_ID,
        perPage,
        totalPages,
        include_message_activity,
        start_time,
        end_time,
        following_users,
        unfollowed_ids,
        follow_unfollowed_users,
    ):
        self.viewer_ID = viewer_ID
        self.perPage = perPage
        self.totalPages = totalPages
        self.include_message_activity = include_message_activity
        self.start_time = start_time
        self.end_time = end_time
        self.following_users = following_users
        self.unfollowed_ids = unfollowed_ids
        self.follow_unfollowed_users = follow_unfollowed_users
        self.user_likes_count = {}
        self.not_appeared_users = {user_id: 0 for user_id in following_users}
        self.followed_users = []


def Get_Liked_Activities(perPage, totalPages, include_message_activity):
    """
    Retrieves and processes liked activities.

    Args:
        perPage (int): The number of activities to retrieve per page.
        totalPages (int): The total number of pages to retrieve.
        include_message_activity (bool): Whether to include message activities.

    This function retrieves the liked activities for the current user, processes them,
    and follows/unfollows users based on the user's preferences. It also displays the
    count of likes per user and the users who have not appeared.
    """
    viewer_ID, following_users = get_viewer_id_and_following_users()
    follow_unfollowed_users, time_back, likes_threshold = get_user_input()
    unfollowed_ids = Config.load_unfollowed_ids()
    time_back_seconds = Convert_Time_To_Seconds(time_back)
    end_time = int(time.time())  # Current time in Unix timestamp
    start_time = (
        end_time - time_back_seconds
    )  # Subtract the number of seconds in the specified number of days

    context = ActivityProcessingContext(
        viewer_ID,
        perPage,
        totalPages,
        include_message_activity,
        start_time,
        end_time,
        following_users,
        unfollowed_ids,
        follow_unfollowed_users,
    )

    (
        context.user_likes_count,
        context.not_appeared_users,
        context.followed_users,
    ) = process_activities(context)

    context.followed_users, context.following_users = follow_users(
        context.followed_users,
        context.user_likes_count,
        likes_threshold,
        context.following_users,
    )
    context.user_likes_count, context.not_appeared_users = display_user_likes_count(
        context.user_likes_count,
        likes_threshold,
        context.following_users,
        context.not_appeared_users,
    )
    display_not_appeared_users(context.not_appeared_users)


def get_viewer_id_and_following_users():
    """
    Retrieves the viewer's ID and the list of users they are following.

    Returns:
        tuple: A tuple containing the viewer's ID and a list of users they are following.
    """
    viewer_ID = Get_User_ID()
    following_users = Get_Following()
    return viewer_ID, following_users


def get_user_input():
    """
    Prompts the user for various inputs needed for the program.

    Returns:
        tuple: A tuple containing the user's responses to the prompts. The first element
        is a boolean indicating whether the user wants to follow users who like their
        activity but they are not following. The second element is a string indicating
        how far back to check for activities. The third element is an integer indicating
        the minimum number of activities a user needs to have liked to be included in the list.
    """
    follow_unfollowed_users = (
        Get_Valid_Input(
            "\nWould you like to follow users who like your activity "
            "but you are not following them? (y/n): ",
            valid_inputs=["y", "n"],
        ).lower()
        == "y"
    )
    time_back = Get_Valid_Input(
        "\nHow far back should it check for activities? Enter a number for days, "
        "or append 'w' for weeks, 'm' for months, or 'y' for years "
        "(e.g., '2w' for 2 weeks): ",
        validation_func=Is_Valid_Time_Period,
    )
    likes_threshold = Get_Valid_Input(
        "\nEnter the minimum number of activities a user needs to have "
        "liked to be included in the list: ",
        validation_func=Is_Positive_Integer,
    )
    return follow_unfollowed_users, time_back, likes_threshold


def process_activities(context):
    """
    Processes the activities of the user.

    Args:
        context (ActivityProcessingContext): The context containing all the necessary
        information for processing activities.

    Returns:
        tuple: A tuple containing the updated user likes count, not appeared users,
        and followed users.
    """
    for page in range(1, context.totalPages + 1):
        print(f"\nChecking page {page}...")
        query, variables = QM.Queries.User_Activity_Feed_Query(
            context.viewer_ID,
            page,
            context.perPage,
            context.include_message_activity,
            context.start_time,
            context.end_time,
        )
        response = API_Request(query, variables)
        activities = response["data"]["Page"]["activities"]
        if not activities:
            print("No more activities to retrieve.")
            break
        for activity in activities:
            if "likes" in activity:
                for user in activity["likes"]:
                    user_id = user["id"]
                    if user_id in context.user_likes_count:
                        context.user_likes_count[user_id] += 1
                    else:
                        context.user_likes_count[user_id] = 1
                    if user_id in context.not_appeared_users:
                        del context.not_appeared_users[user_id]
                    if (
                        user_id not in context.following_users
                        and user_id not in context.unfollowed_ids
                        and context.follow_unfollowed_users
                        and user_id != context.viewer_ID
                        and user_id not in context.followed_users
                    ):
                        context.followed_users.append(user_id)
    return context.user_likes_count, context.not_appeared_users, context.followed_users


def follow_users(followed_users, user_likes_count, likes_threshold, following_users):
    """
    Follows users based on the likes threshold.

    Args:
        followed_users (list): The list of users the viewer has followed.
        user_likes_count (dict): A dictionary to count the likes per user.
        likes_threshold (int): The minimum number of likes a user must have to be followed.
        following_users (list): The list of users the viewer is following.

    This function iterates over the list of followed users. If a user's likes count is greater
    than or equal to the likes threshold, the function attempts to follow the user. If the follow
    is successful, the user is added to the list of following users. If a user's likes count is
    less than the likes threshold, the user is removed from the list of followed users.

    Returns:
        tuple: A tuple containing the updated lists of followed users and following users.
    """
    for user_id in list(followed_users):
        if user_likes_count.get(user_id, 0) >= likes_threshold:
            if Follow_User(user_id):
                following_users.append(user_id)
        else:
            followed_users.remove(user_id)
    return followed_users, following_users


def display_user_likes_count(
    user_likes_count, likes_threshold, following_users, not_appeared_users
):
    """
    Displays the count of likes per user and updates the lists of users.

    Args:
        user_likes_count (dict): A dictionary to count the likes per user.
        likes_threshold (int): The minimum number of likes a user must have to be displayed.
        following_users (list): The list of users the viewer is following.
        not_appeared_users (dict): A dictionary to track the users who have not appeared.

    This function sorts the user_likes_count dictionary in descending order of likes count.
    It then iterates over the sorted list and prints the user ID and likes count for each user
    whose likes count is greater than or equal to the likes threshold. If a user's likes count
    is less than the likes threshold, the user is removed from the user_likes_count dictionary
    and, if the user is in the list of following users, the user is added to the
    not_appeared_users dictionary with a count of 0.

    Returns:
        tuple: A tuple containing the updated user_likes_count dictionary and
        not_appeared_users dictionary.
    """
    sorted_user_likes = sorted(
        user_likes_count.items(), key=lambda item: item[1], reverse=True
    )
    print(f"\nUser Likes Count ({len(sorted_user_likes)}):")
    for user_id, count in sorted_user_likes:
        if count >= likes_threshold:
            print(f"User ID: {user_id}, Count: {count}")
        else:
            del user_likes_count[user_id]
            if user_id in following_users:
                not_appeared_users[user_id] = 0
    return user_likes_count, not_appeared_users


def display_not_appeared_users(not_appeared_users):
    """
    Displays the users who have not appeared and optionally unfollows them.

    Args:
        not_appeared_users (dict): A dictionary to track the users who have not appeared.

    This function first asks the user if they want to display the users who have not appeared.
    If the user answers 'y', the function loads the list of excluded user IDs and filters out
    these IDs from the not_appeared_users dictionary. It then prints the user IDs and counts
    of the users who have not appeared.

    The function then asks the user if they want to unfollow the users who have not appeared.
    If the user answers 'y', the function unfollows each user in the not_appeared_users dictionary
    and adds their user ID to the unfollowed_ids list.

    Finally, the function asks the user if they want to save the unfollowed user IDs.
    If the user answers 'y', the function saves the unfollowed user IDs to a file.
    """
    display_not_appeared = input("\nDisplay users not appeared? (y/n): ").lower() == "y"
    if display_not_appeared:
        excluded_ids = Config.load_excluded_ids()
        not_appeared_users = {
            user_id: count
            for user_id, count in not_appeared_users.items()
            if user_id not in excluded_ids
        }
        print(f"\nUsers Not Appeared ({len(not_appeared_users)}): {not_appeared_users}")
        unfollow_not_appeared = (
            input("\nUnfollow users not appeared? (y/n): ").lower() == "y"
        )
        if unfollow_not_appeared:
            unfollowed_ids = []
            for user_id in not_appeared_users:
                Unfollow_User(user_id)
                unfollowed_ids.append(user_id)
            save_unfollowed = (
                input("\nSave unfollowed user IDs? (y/n): ").lower() == "y"
            )
            if save_unfollowed:
                Config.save_unfollowed_ids(set(unfollowed_ids))
