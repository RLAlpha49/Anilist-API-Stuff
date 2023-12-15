# Import necessary modules
from APIUsage.ActivityActions import Like_Following_Activities
from APIUsage.Utils import Get_User_ID, Get_Valid_Input

def LikeFollowingFeed():
    print()
    # Get the current user's ID
    Get_User_ID()

    print(f"Press the 'F12' key to stop liking activities. (There may be a slight delay before the program stops)\n")
    # Ask the user for the refresh interval
    refresh_interval = Get_Valid_Input("Enter the refresh interval in minutes (Give it some time, the Anilist API takes some time to sort from newest to oldest activities): ", list(map(str, range(1, 101))))
    total_pages = Get_Valid_Input("Enter the number of pages to like activities from (Max 100): ", list(map(str, range(1, 101))))

    # Call the function to like activities
    Like_Following_Activities(int(refresh_interval), int(total_pages))