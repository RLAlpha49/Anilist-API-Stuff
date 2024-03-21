"""
This module contains functions to identify and follow users that the current
user is not following back.

The main function `GetUsersYouAreNotFollowingBack` fetches the user's followers
and following lists, identifies users that are followers but not being followed
back, and offers to exclude them from the unfollowed IDs list. If there are such
users, the function offers to follow them.
"""

# pylint: disable=C0103

# Import necessary modules
from APIUsage.UserActions import Follow_User
from APIUsage.Utils import Get_Followers, Get_Following, Get_User_ID, Get_Valid_Input
from Config import load_unfollowed_ids


# Function to print statistics about followers and following
def print_statistics(followers, following, not_following):
    """
    Prints the number of followers, the number of users being followed,
    and the number of followers not being followed back.

    Args:
        followers (list): A list of followers.
        following (list): A list of users being followed.
        not_following (list): A list of followers not being followed back.
    """
    print(f"\nNumber of Followers: {len(followers)}")
    print(f"Number of Following: {len(following)}")
    print(f"Number of Followers Not Following Back: {len(not_following)}")
    print(f"\nList of ID's:\n{list(not_following)}\n")


# Function to exclude unfollowed users from the list of users not being followed back
def exclude_unfollowed_users(not_following):
    """
    Excludes unfollowed users from being followed again, if the user chooses to do so.

    Args:
        not_following (set): A set of user IDs that the current user is not following.

    Returns:
        set: The updated set of user IDs that the current user is not following,
        with unfollowed users excluded if the user chose to do so.
    """
    if (
        Get_Valid_Input(
            "Would you like to exclude unfollowed users from being followed again? (y/n): ",
            ["y", "n"],
        )
        == "y"
    ):
        unfollowed_ids = load_unfollowed_ids()
        not_following = not_following - unfollowed_ids
        print(f"\nList of ID's:\n{list(not_following)}\n")
    return not_following


# Function to follow users not being followed back
def follow_users(not_following):
    """
    Follows users that the current user is not following back, if the user chooses to do so.

    Args:
        not_following (set): A set of user IDs that the current user is not following.
    """
    if (
        Get_Valid_Input("Would you like to follow these users? (y/n): ", ["y", "n"])
        == "y"
    ):
        for user_id in not_following:
            Follow_User(user_id)
        print("\nFollowed all users not followed.")


# Main function to get users that the user is not following back
def GetUsersYouAreNotFollowingBack():
    """
    Fetches the user's followers and following lists, identifies users that are followers
    but not being followed back, and offers to exclude them from the unfollowed IDs list.
    If there are such users, the function offers to follow them.
    """
    # Fetch user's followers and following lists
    print()
    Get_User_ID()
    followers = Get_Followers()
    print()
    following = Get_Following()

    # Identify users that are followers but not being followed back
    not_following = set(followers) - set(following)

    # If there are such users, offer to exclude them from the unfollowed IDs list
    if not_following:
        print_statistics(followers, following, not_following)
        not_following = exclude_unfollowed_users(not_following)
        follow_users(not_following)
    else:
        print("\nYou are following all your followers.")
