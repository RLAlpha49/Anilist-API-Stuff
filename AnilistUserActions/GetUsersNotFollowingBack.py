# Import necessary modules
from APIUsage.UserActions import Unfollow_User
from APIUsage.Utils import Get_User_ID, Get_Followers, Get_Following, Get_Valid_Input, Is_Positive_Integer
import Config

# Function to print statistics about followers, following, excluded IDs, and users not following back
def print_statistics(followers, following, excluded_ids, not_following_back):
    print(f"\nNumber of Followers: {len(followers)}")
    print(f"Number of Following: {len(following)}")
    print(f"Number of Excluded IDs: {len(excluded_ids)}")
    print(f"Number of Following Not Following Back: {len(not_following_back)}")
    print(f"\nList of ID's:\n{list(not_following_back)}\n")

# Function to handle exclusion of certain IDs from the list of users not following back
def handle_exclusion(not_following_back, excluded_ids):
    # Ask the user for an action
    action = Get_Valid_Input("Enter 'add' to exclude an ID, 'edit' to edit excluded IDs, 'done' to finish: ", ['add', 'edit', 'done'])
    if action == 'add':
        # If the action is 'add', ask the user for an ID to exclude
        exclude_id = Get_Valid_Input("Enter an ID to exclude: ", validation_func=Is_Positive_Integer)
        excluded_id = int(exclude_id)
        not_following_back.discard(excluded_id)
        excluded_ids.append(excluded_id)
    elif action == 'edit':
        # If the action is 'edit', call the function to edit excluded IDs
        edit_excluded_ids(excluded_ids)
    # Save the excluded IDs
    Config.save_excluded_ids(set(excluded_ids))
    return not_following_back, excluded_ids

# Function to edit the list of excluded IDs
def edit_excluded_ids(excluded_ids):
    # Print the list of excluded IDs
    for i, id in enumerate(excluded_ids, start=1):
        print(f"{i}. {id}")
    # Ask the user for an ID to edit
    edit_id = Get_Valid_Input("Enter the number of the ID to remove or edit, 'add' to add a new ID, or 'done' to finish: ", list(map(str, range(1, len(excluded_ids) + 1))) + ['add', 'done'])
    if edit_id == 'add':
        # If the user wants to add a new ID, ask for the new ID
        new_id = Get_Valid_Input("Enter the new ID to add: ", validation_func=Is_Positive_Integer)
        excluded_ids.append(int(new_id))
    elif edit_id != 'done':
        # If the user wants to edit an existing ID, ask for the new ID
        edit_id = int(edit_id) - 1
        action = Get_Valid_Input("Enter 'remove' to remove the ID or 'change' to change it: ", ['remove', 'change'])
        if action == 'remove':
            excluded_ids.pop(edit_id)
        elif action == 'change':
            new_id = Get_Valid_Input("Enter the new ID: ", validation_func=Is_Positive_Integer)
            excluded_ids[edit_id] = int(new_id)
    # Print the updated list of excluded IDs
    print("\nExcluded IDs:")
    for i, id in enumerate(excluded_ids, start=1):
        print(f"{i}. {id}")

# Function to unfollow users not following back
def unfollow_users(not_following_back, unfollowed_ids):
    # Ask the user if they want to unfollow the users not following back
    if Get_Valid_Input("\nWould you like to unfollow these users? (y/n): ", ['y', 'n']) == 'y':
        print()
        for id in not_following_back:
            Unfollow_User(id)
            unfollowed_ids.append(id)
        print("\nUnfollowed all users not following back.")
        # Ask the user if they want to save the IDs of the unfollowed users
        if Get_Valid_Input("\nWould you like to save the ID's of the unfollowed users so they are not followed again? (y/n): ", ['y', 'n']) == 'y':
            Config.save_unfollowed_ids(set(unfollowed_ids))

def GetUsersNotFollowingBack():
    # Get user's ID, followers, and following
    print()
    Get_User_ID()
    followers = Get_Followers()
    print()
    following = Get_Following()

    # Calculate users not following back, excluding certain IDs
    not_following_back = set(following) - set(followers)
    excluded_ids = list(Config.load_excluded_ids())
    not_following_back -= set(excluded_ids)

    # Save the original set of users not following back
    old_not_following_back = not_following_back

    # Load the list of unfollowed IDs
    unfollowed_ids = list(Config.load_unfollowed_ids())

    if not_following_back:
        # Print statistics and handle exclusions
        print_statistics(followers, following, excluded_ids, not_following_back)
        not_following_back, excluded_ids = handle_exclusion(not_following_back, excluded_ids)

        # Print the new list if it has changed
        if old_not_following_back != not_following_back:
            print(f"\nNew List:\n{list(not_following_back)}")
        else:
            print("\nThe list has not changed.")

        # Unfollow the users not following back
        unfollow_users(not_following_back, unfollowed_ids)
    else:
        # Print a message if there are no users not following back
        print("\nNo Followers Not Following Back.")