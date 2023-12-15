# Import necessary modules
import Config
from API import Get_Access_Token
import RequestAPI

# TODO: When liking following activity feed, go back to previous page before time reset if no activities are liked for 2 or more pages
# TODO: Add option to check activitiy counts within a certain time frame
# TODO: Add option to add users to the list when checking activity counts when above a certain count

class Main():
    def __init__(self):
        def get_valid_input(prompt, valid_inputs=None, validation_func=None):
            while True:
                user_input = input(prompt)
                if valid_inputs and user_input in valid_inputs:
                    return user_input
                elif validation_func and validation_func(user_input):
                    return int(user_input)
                else:
                    print("Invalid input. Please try again.")
                    
        def is_positive_integer(s):
            return s.isdigit() and int(s) > 0
        
        # Load configuration and ask for client and secret IDs if not found
        config = Config.load_config('config.json')
        if not config:
            input("Config file not found. Press enter to continue...")
            print("Please create an API on Anilist for the following values (Set Rediruct URL to: https://anilist.co/api/v2/oauth/pin):")
            client = input("Enter Client ID: ")
            secret = input("Enter Secret ID: ")
            
            # Create and save new configuration, set environment variables and access token
            config = Config.create_config(client, secret, Get_Access_Token())
            Config.save_config(config, 'config.json')
            Config.Set_Environment_Variables(config)
            RequestAPI.Set_Access_Token()
        else:
            client = config['ANILIST_CLIENT_ID']
            secret = config['ANILIST_CLIENT_SECRET']
            Config.Set_Environment_Variables(config)

        # Refresh access token if it's not valid
        refresh = RequestAPI.Check_Access_Token()
        while refresh:
            config = Config.create_config(client, secret, Get_Access_Token())
            Config.save_config(config, 'config.json')
            RequestAPI.Set_Access_Token()
            refresh = RequestAPI.Check_Access_Token()

        print('Notice: Anilist will rate limit often, so please be patient when using this program. (Most times it rate limites a specific feature so you should be able to use other features on the site while this is running.)')
        while True:
            option = get_valid_input("\n0. Exit\n1. Get Users Not Following Back\n2. Get Users You Are Not Following Back\n3. Follow Random Users From Global Activity Feed\n4. Like Users Activity\n5. Like Following Feed\n6. Get Activity Count\nOption: ", ['0', '1', '2', '3', '4', '5', '6'])
            if option == '0':
                break
            elif option == '1':
                print()
                RequestAPI.Get_User_ID()
                followers = RequestAPI.Get_Followers()
                print()
                following = RequestAPI.Get_Following()

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
                    action = get_valid_input("Enter 'add' to exclude an ID, 'edit' to edit excluded IDs, 'done' to finish: ", ['add', 'edit', 'done'])
                    if action == 'add':
                        # Exclude the specified id
                        exclude_id = get_valid_input("Enter an ID to exclude: ", validation_func=is_positive_integer)
                        excluded_id = int(exclude_id)
                        not_following_back.discard(excluded_id)
                        excluded_ids.append(excluded_id)
                    elif action == 'edit':
                        # Print the excluded ids in a numbered list
                        for i, id in enumerate(excluded_ids, start=1):
                            print(f"{i}. {id}")

                        # Ask the user to edit the excluded ids
                        edit_id = get_valid_input("Enter the number of the ID to remove or edit, 'add' to add a new ID, or 'done' to finish: ", list(map(str, range(1, len(excluded_ids) + 1))) + ['add', 'done'])
                        if edit_id == 'add':
                            # Add a new id to the excluded ids
                            new_id = get_valid_input("Enter the new ID to add: ", validation_func=is_positive_integer)
                            excluded_ids.append(int(new_id))
                        elif edit_id != 'done':
                            # Edit the specified id
                            edit_id = int(edit_id) - 1  # Subtract 1 because the list is 0-indexed
                            action = get_valid_input("Enter 'remove' to remove the ID or 'change' to change it: ", ['remove', 'change'])
                            if action == 'remove':
                                # Remove the specified id
                                excluded_ids.pop(edit_id)
                            elif action == 'change':
                                # Change the specified id
                                new_id = get_valid_input("Enter the new ID: ", validation_func=is_positive_integer)
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
                    if get_valid_input("\nWould you like to unfollow these users? (y/n): ", ['y', 'n']) == 'y':
                        print()
                        # Unfollow each user in the list
                        for id in not_following_back:
                            RequestAPI.Unfollow_User(id)
                            # Add the user to the list of unfollowed users
                            unfollowed_ids.append(id)
                        # Print a confirmation message
                        print("\nUnfollowed all users not following back.")

                        if get_valid_input("\nWould you like to save the ID's of the unfollowed users so they are not followed again? (y/n): ", ['y', 'n']) == 'y':
                            # Save the list of unfollowed users
                            Config.save_unfollowed_ids(set(unfollowed_ids))
                else:
                    # Print a message indicating that there are no followers to follow
                    print("\nNo Followers Not Following Back.")
            elif option == '2':
                # Fetch user's followers and following lists
                print()
                RequestAPI.Get_User_ID()
                followers = RequestAPI.Get_Followers()
                print()
                following = RequestAPI.Get_Following()

                # Identify users that are followers but not being followed back
                not_following = set(followers) - set(following)

                # If there are such users, offer to exclude them from the unfollowed IDs list
                if not_following:
                    print(f"\nNumber of Followers: {len(followers)}")
                    print(f"Number of Following: {len(following)}")
                    print(f"Number of Followers Not Following Back: {len(not_following)}")
                    print(f"\nList of ID's:\n{list(not_following)}\n")

                    if get_valid_input("Would you like to exclude unfollowed users from being followed again? (y/n): ", ['y', 'n']) == 'y':
                        unfollowed_ids = Config.load_unfollowed_ids()
                        not_following = not_following - unfollowed_ids
                        print(f"\nList of ID's:\n{list(not_following)}\n")

                    if get_valid_input("Would you like to follow these users? (y/n): ", ['y', 'n']) == 'y':
                        for id in not_following:
                            RequestAPI.Follow_User(id)
                        print("\nFollowed all users not followed.")
                else:
                    print("\nYou are following all your followers.")
            elif option == '3':
                print()
                # Get the current user's ID
                RequestAPI.Get_User_ID()
                total_people_to_follow = get_valid_input("Enter the number of people you would like to follow: ", validation_func=is_positive_integer)
                # Call the function to get global activities of the specified number of people
                RequestAPI.Get_Global_Activities(total_people_to_follow)
            elif option == '4':
                print()
                # Get the current user's ID
                RequestAPI.Get_User_ID()

                # Ask the user to choose an option for the list of users
                choice = get_valid_input("Do you want to enter a list of users, use the whole follower list, or only followers who follow you back? (Enter 'list', 'followers', 'mutual', or 'not followed'): ", ['list', 'followers', 'mutual', 'not followed'])

                # Process the user's choice
                if choice == 'list':
                    # Convert the user input into a list of user IDs
                    user_list = [int(user.strip()) if user.strip().isdigit() else RequestAPI.Get_User_ID_From_Username(user.strip()) for user in input("Enter a comma-separated list of user IDs or usernames (e.g., 12345, 67890, username1, username2): ").split(',')]
                elif choice == 'mutual':
                    # Get the list of mutual followers
                    user_list = RequestAPI.Get_Mutual_Followers()
                elif choice == 'not followed':
                    # Get the list of followers not followed back
                    user_list = RequestAPI.Get_Not_Followed_Followers()
                elif choice == 'followers':
                    # Use the whole follower list
                    user_list = None

                # Get the number of activities to like per followed user and whether to include message activities
                total_activities_to_like = get_valid_input("Enter the number of activities you would like to like per user (Max 100): ", validation_func=is_positive_integer)
                include_message_activity = get_valid_input("Do you want to like message activities? - Messages sent to the user are considered that users activity. (y/n): ", ['y', 'n']).lower() == 'y'

                print()
                # Call the function to like activities
                RequestAPI.Like_Activities(total_activities_to_like, include_message_activity, user_list)
            elif option == '5':
                print()
                # Get the current user's ID
                RequestAPI.Get_User_ID()

                print(f"Press the 'F12' key to stop liking activities. (There may be a slight delay before the program stops)\n")
                # Ask the user for the refresh interval
                refresh_interval = get_valid_input("Enter the refresh interval in minutes (Give it some time, the Anilist API takes some time to sort from newest to oldest activities): ", list(map(str, range(1, 101))))
                total_pages = get_valid_input("Enter the number of pages to like activities from (Max 100): ", list(map(str, range(1, 101))))

                # Call the function to like activities
                RequestAPI.Like_Following_Activities(int(refresh_interval), int(total_pages))
            elif option == '6':
                perPage = get_valid_input("\nEnter the number of activities per page (Max 50): ", list(map(str, range(1, 51))))
                totalPages = int(input("Enter the total number of pages to go through (There is no Max, program will stop when activities stop returning): "))
                print(f"Total activities to check: {int(perPage) * totalPages}\n")
                include_message_activity = get_valid_input("Do you want include message activities? (y/n): ", ['y', 'n']).lower() == 'y'
                print()
                RequestAPI.Get_Liked_Activities(int(perPage), totalPages, include_message_activity)
if __name__ == '__main__':
    Main()