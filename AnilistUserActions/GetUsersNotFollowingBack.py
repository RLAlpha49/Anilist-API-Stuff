# Import necessary modules
from APIUsage.UserActions import Unfollow_User
from APIUsage.Utils import Get_User_ID, Get_Followers, Get_Following, Get_Valid_Input, Is_Positive_Integer
import Config

def GetUsersNotFollowingBack():
    print()
    Get_User_ID()
    followers = Get_Followers()
    print()
    following = Get_Following()

    # Identify users that you are following but are not your followers
    not_following_back = set(following) - set(followers)

    # Exclude certain users from the list
    excluded_ids = list(Config.load_excluded_ids())
    not_following_back -= set(excluded_ids)
    old_not_following_back = not_following_back
    
    # Load the list of unfollowed users
    unfollowed_ids = list(Config.load_unfollowed_ids())
    
    if not_following_back:
        # Print the number of followers, following, and not following back
        print(f"\nNumber of Followers: {len(followers)}")
        print(f"Number of Following: {len(following)}")
        print(f"Number of Excluded IDs: {len(excluded_ids)}")
        print(f"Number of Following Not Following Back: {len(not_following_back)}")
        print(f"\nList of ID's:\n{list(not_following_back)}\n")

        # Ask the user if they want to exclude any ids
        action = Get_Valid_Input("Enter 'add' to exclude an ID, 'edit' to edit excluded IDs, 'done' to finish: ", ['add', 'edit', 'done'])
        if action == 'add':
            # Exclude the specified id
            exclude_id = Get_Valid_Input("Enter an ID to exclude: ", validation_func=Is_Positive_Integer)
            excluded_id = int(exclude_id)
            not_following_back.discard(excluded_id)
            excluded_ids.append(excluded_id)
        elif action == 'edit':
            # Print the excluded ids in a numbered list
            for i, id in enumerate(excluded_ids, start=1):
                print(f"{i}. {id}")

            # Ask the user to edit the excluded ids
            edit_id = Get_Valid_Input("Enter the number of the ID to remove or edit, 'add' to add a new ID, or 'done' to finish: ", list(map(str, range(1, len(excluded_ids) + 1))) + ['add', 'done'])
            if edit_id == 'add':
                # Add a new id to the excluded ids
                new_id = Get_Valid_Input("Enter the new ID to add: ", validation_func=Is_Positive_Integer)
                excluded_ids.append(int(new_id))
            elif edit_id != 'done':
                # Edit the specified id
                edit_id = int(edit_id) - 1  # Subtract 1 because the list is 0-indexed
                action = Get_Valid_Input("Enter 'remove' to remove the ID or 'change' to change it: ", ['remove', 'change'])
                if action == 'remove':
                    # Remove the specified id
                    excluded_ids.pop(edit_id)
                elif action == 'change':
                    # Change the specified id
                    new_id = Get_Valid_Input("Enter the new ID: ", validation_func=Is_Positive_Integer)
                    excluded_ids[edit_id] = int(new_id)

            # Reprint the list of excluded ids
            print("\nExcluded IDs:")
            for i, id in enumerate(excluded_ids, start=1):
                print(f"{i}. {id}")

        # Save the excluded ids
        Config.save_excluded_ids(set(excluded_ids))

        # Compare and print
        if old_not_following_back != not_following_back:
            print(f"\nNew List:\n{list(not_following_back)}")
        else:
            print("\nThe list has not changed.")

        # Ask the user if they want to unfollow these users
        if Get_Valid_Input("\nWould you like to unfollow these users? (y/n): ", ['y', 'n']) == 'y':
            print()
            # Unfollow each user in the list
            for id in not_following_back:
                Unfollow_User(id)
                # Add the user to the list of unfollowed users
                unfollowed_ids.append(id)
            # Print a confirmation message
            print("\nUnfollowed all users not following back.")

            if Get_Valid_Input("\nWould you like to save the ID's of the unfollowed users so they are not followed again? (y/n): ", ['y', 'n']) == 'y':
                # Save the list of unfollowed users
                Config.save_unfollowed_ids(set(unfollowed_ids))
    else:
        # Print a message indicating that there are no followers to follow
        print("\nNo Followers Not Following Back.")