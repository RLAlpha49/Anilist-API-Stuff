# Import necessary modules
from APIUsage.Utils import Get_Valid_Input
from Setup import Setup
from AnilistUserActions import *

# TODO: Add option to like activities within a certain time frame


class Main:
    def __init__(self):
        Setup()

        print(
            "Notice: Anilist will rate limit often, so please be patient when using this program. (Most times it rate limites a specific feature so you should be able to use other features on the site while this is running.)"
        )
        while True:
            option = Get_Valid_Input(
                "\n0. Exit\n1. Get Users Not Following Back\n2. Get Users You Are Not Following Back\n3. Follow Random Users From Global Activity Feed\n4. Like Users Activity\n5. Like Following Feed\n6. Get Activity Count\nOption: ",
                ["0", "1", "2", "3", "4", "5", "6"],
            )
            if option == "0":
                break
            elif option == "1":
                GetUsersNotFollowingBack.GetUsersNotFollowingBack()
            elif option == "2":
                GetUsersYouAreNotFollowingBack.GetUsersYouAreNotFollowingBack()
            elif option == "3":
                FollowRandomUsers.FollowRandomUsers()
            elif option == "4":
                LikeUsersActivity.LikeUsersActivity()
            elif option == "5":
                LikeFollowingFeed.LikeFollowingFeed()
            elif option == "6":
                GetActivityCount.GetActivityCount()


if __name__ == "__main__":
    Main()
