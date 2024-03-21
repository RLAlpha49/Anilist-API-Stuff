"""
This module contains functions for interacting with users and activities.

Functions:
    Like_Activity: Sends a 'like' action for a specific activity.
    Toggle_Follow_User: Toggles the follow status of a user.
    Unfollow_User: Unfollows a user.
    Follow_User: Follows a user.
"""

# pylint: disable=C0103, E0401

# Import necessary modules
import QueriesAndMutations as QM
from .APIRequests import API_Request  # pylint: disable=E0402


def Like_Activity(activity_id):
    """
    Sends a 'like' action for a specific activity.

    Args:
        activity_id (str): The ID of the activity to be liked.

    Returns:
        bool: True if the like action was successful, False otherwise.
    """
    query, variables = QM.Mutations.Like_Mutation(activity_id)
    response = API_Request(query, variables)
    if response is not None and "errors" not in response:
        return True
    print(f"Failed to like activity with ID: {activity_id}")
    return False


def Toggle_Follow_User(user_id, desired_status, success_message, error_message):
    """
    Toggles the follow status of a user.

    Args:
        user_id (str): The ID of the user to follow/unfollow.
        desired_status (bool): The desired follow status. True for follow, False for unfollow.
        success_message (str): The message to print if the operation is successful.
        error_message (str): The message to print if the operation fails.

    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    query, variables = QM.Mutations.Follow_Mutation(user_id)
    response = API_Request(query, variables)
    if response is not None:
        if response["data"]["ToggleFollow"]["isFollowing"] == desired_status:
            print(
                success_message.format(
                    response["data"]["ToggleFollow"]["name"], user_id
                )
            )
            return True
        print(error_message.format(response["data"]["ToggleFollow"]["name"], user_id))
        return Toggle_Follow_User(
            user_id, desired_status, success_message, error_message
        )
    print(
        f"Failed to update follow status for user with ID: {user_id}"
        "\nUser account most likely deleted."
    )
    return False


def Unfollow_User(user_id):
    """
    Unfollows a user.

    Args:
        user_id (str): The ID of the user to unfollow.

    Returns:
        bool: True if the unfollow operation was successful, False otherwise.
    """
    return Toggle_Follow_User(
        user_id,
        False,
        "Unfollowed {} with ID: {}",
        "Error: {} already unfollowed with ID: {}",
    )


def Follow_User(user_id):
    """
    Follows a user.

    Args:
        user_id (str): The ID of the user to follow.

    Returns:
        bool: True if the follow operation was successful, False otherwise.
    """
    return Toggle_Follow_User(
        user_id,
        True,
        "Followed {} with ID: {}",
        "Error: {} already followed with ID: {}",
    )
