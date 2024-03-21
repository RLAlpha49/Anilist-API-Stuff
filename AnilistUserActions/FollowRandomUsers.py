"""
This module contains a function to follow a specified number of random users.
It gets user inputs for the number of people they would like to follow,
then calls a function to get the global activities of the specified number of people.
"""

# pylint: disable=C0103

# Import necessary modules
from APIUsage.ActivityActions import Get_Global_Activities
from APIUsage.Utils import Get_User_ID, Get_Valid_Input, Is_Positive_Integer


def FollowRandomUsers():
    """
    Follows a specified number of random users.

    The function asks the user for the number of people they would like to follow,
    then calls a function to get the global activities of the specified number of people.
    """
    print()
    # Get the current user's ID
    Get_User_ID()
    total_people_to_follow = Get_Valid_Input(
        "Enter the number of people you would like to follow: ",
        validation_func=Is_Positive_Integer,
    )
    # Call the function to get global activities of the specified number of people
    Get_Global_Activities(total_people_to_follow)
