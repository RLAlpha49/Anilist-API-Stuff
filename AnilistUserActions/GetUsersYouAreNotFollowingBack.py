# Import necessary modules
from APIUsage.UserActions import Follow_User
from APIUsage.Utils import Get_User_ID, Get_Followers, Get_Following, Get_Valid_Input
from Config import load_unfollowed_ids

# Function to print statistics about followers and following
def print_statistics(followers, following, not_following):
    print(f"\nNumber of Followers: {len(followers)}")
    print(f"Number of Following: {len(following)}")
    print(f"Number of Followers Not Following Back: {len(not_following)}")
    print(f"\nList of ID's:\n{list(not_following)}\n")

# Function to exclude unfollowed users from the list of users not being followed back
def exclude_unfollowed_users(not_following):
    if Get_Valid_Input("Would you like to exclude unfollowed users from being followed again? (y/n): ", ['y', 'n']) == 'y':
        unfollowed_ids = load_unfollowed_ids()
        not_following = not_following - unfollowed_ids
        print(f"\nList of ID's:\n{list(not_following)}\n")
    return not_following

# Function to follow users not being followed back
def follow_users(not_following):
    if Get_Valid_Input("Would you like to follow these users? (y/n): ", ['y', 'n']) == 'y':
        for id in not_following:
            Follow_User(id)
        print("\nFollowed all users not followed.")

# Main function to get users that the user is not following back
def GetUsersYouAreNotFollowingBack():
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