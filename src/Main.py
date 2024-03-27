"""
This module contains the main entry point for the program. It provides a
menu for the user to select various options related to the Anilist API and
performs the corresponding actions based on the user's selection.

Classes:
    Main

Functions:
    __init__(self)
"""

# pylint: disable=C0103

# Import necessary modules
from Setup import Setup
from src.AnilistUserActions import (
    FollowRandomUsers,
    GetActivityCount,
    GetUsersNotFollowingBack,
    GetUsersYouAreNotFollowingBack,
    LikeFollowingFeed,
    LikeUsersActivity,
)
from src.APIUsage.Utils import Get_Valid_Input


class Main:  # pylint: disable=R0903
    """
    This class serves as the main entry point for the program. It provides a
    menu for the user to select various options and performs the corresponding
    actions based on the user's selection.
    """

    def __init__(self):
        Setup()

        print(
            "Notice: Anilist will rate limit often, so please be patient when "
            "using this program. (Most times it rate limits a specific feature "
            "so you should be able to use other features on the site while this "
            "is running.)"
        )
        while True:
            option = Get_Valid_Input(
                "\n0. Exit\n1. Get Users Not Following Back\n"
                "2. Get Users You Are Not Following Back\n"
                "3. Follow Random Users From Global Activity Feed\n"
                "4. Like Users Activity\n5. Like Following Feed\n"
                "6. Get Activity Count\nOption: ",
                ["0", "1", "2", "3", "4", "5", "6"],
            )
            if option == "0":
                break
            if option == "1":
                GetUsersNotFollowingBack.GetUsersNotFollowingBack()
            if option == "2":
                GetUsersYouAreNotFollowingBack.GetUsersYouAreNotFollowingBack()
            if option == "3":
                FollowRandomUsers.FollowRandomUsers()
            if option == "4":
                LikeUsersActivity.LikeUsersActivity()
            if option == "5":
                LikeFollowingFeed.LikeFollowingFeed()
            if option == "6":
                GetActivityCount.GetActivityCount()


if __name__ == "__main__":
    Main()
