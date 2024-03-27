"""
This module contains functions for liking users' activities on a social media platform.

The main function is `LikeUsersActivity`, which likes a number of activities for a list of users.
The list of users can be manually entered by the user, or it can be the whole follower list,
only followers who follow the user back, or followers not followed back by the user.
The user also specifies the number of activities to like and whether to include message activities.

This module also contains helper functions `get_user_list` and `get_activities_to_like`.
"""

# pylint: disable=C0103

# Import necessary modules
from src.APIUsage.ActivityActions import Like_Activities
from src.APIUsage.Utils import (
    Get_Mutual_Followers,
    Get_Not_Followed_Followers,
    Get_User_ID,
    Get_User_ID_From_Username,
    Get_Valid_Input,
    Is_Positive_Integer,
)


# Function to get a list of users based on the user's choice
def get_user_list(choice):
    """
    Returns a list of users based on the user's choice.

    Args:
        choice (str): The user's choice. Can be 'list', 'mutual', 'not followed', or 'followers'.

    Returns:
        list: A list of user IDs or usernames, or None if the user chooses 'followers'.
    """
    if choice == "list":
        # If the user chooses 'list', get a list of user IDs or usernames from the user
        return [
            (
                int(user.strip())
                if user.strip().isdigit()
                else Get_User_ID_From_Username(user.strip())
            )
            for user in input(
                "Enter a comma-separated list of user IDs or usernames "
                "(e.g., 12345, 67890, username1, username2): "
            ).split(",")
        ]

    if choice == "mutual":
        # If the user chooses 'mutual', get a list of mutual followers
        return Get_Mutual_Followers()

    if choice == "not followed":
        # If the user chooses 'not followed', get a list of followers not followed back
        return Get_Not_Followed_Followers()

    if choice == "followers":
        # If the user chooses 'followers', return None to use the whole follower list
        return None

    # If the user's choice is not recognized, return an empty list
    return []


# Function to get the number of activities to like and whether to include message activities
def get_activities_to_like():
    """
    Prompts the user for the number of activities to like per user and whether
    to include message activities.

    Returns:
        tuple: A tuple containing the total number of activities to like per user
        and a boolean indicating whether to include message activities.
    """
    total_activities_to_like = Get_Valid_Input(
        "Enter the number of activities you would like to like per user (Max 100): ",
        validation_func=Is_Positive_Integer,
    )
    include_message_activity = (
        Get_Valid_Input(
            "Do you want to like message activities? - Messages sent to the user are "
            "considered that users activity. (y/n): ",
            ["y", "n"],
        ).lower()
        == "y"
    )
    return total_activities_to_like, include_message_activity


# Main function to like users' activity
def LikeUsersActivity():
    """
    Likes a specified number of activities for a list of users.

    The list of users can be manually entered by the user, or it can be the whole follower list,
    only followers who follow the user back, or followers not followed back by the user.
    The user specifies the number of activities to like and whether to include message activities.
    """
    print()
    Get_User_ID()

    # Get the user's choice of user list
    choice = Get_Valid_Input(
        "Do you want to enter a list of users, use the whole follower list, "
        "or only followers who follow you back? "
        "(Enter 'list', 'followers', 'mutual', or 'not followed'): ",
        ["list", "followers", "mutual", "not followed"],
    )

    # Get the user list based on the choice
    user_list = get_user_list(choice)
    print()

    # Get the number of activities to like and whether to include message activities
    total_activities_to_like, include_message_activity = get_activities_to_like()

    # Like the specified number of activities for each user in the user list
    Like_Activities(total_activities_to_like, include_message_activity, user_list)
