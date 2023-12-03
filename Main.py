import Config
from API import Get_Access_Token
import RequestAPI as RequestAPI
import os

class Main():
    def __init__(self):
        config = Config.load_config('config.json')
        if not config:
            input("Config file not found. Press enter to continue...")
            print("Please create an API on Anilist for the following values (Set Rediruct URL to: https://anilist.co/api/v2/oauth/pin):")
            client = input("Enter Client ID:")
            secret = input("Enter Secret ID:")
            config = Config.create_config(client, secret)
            Config.save_config(config, 'config.json')
            Config.Set_Environment_Variables(config)
            config = Config.create_config(client, secret, Get_Access_Token())
            Config.save_config(config, 'config.json')
        else:
            Config.Set_Environment_Variables(config)
            if os.environ.get('ACCESS_TOKEN') is None:
                config = Config.create_config(client, secret, Get_Access_Token())
                Config.save_config(config, 'config.json')
            RequestAPI.Set_Access_Token()
            
            refresh = RequestAPI.Check_Access_Token()
            while refresh:
                config = Config.load_config('config.json')
                config = Config.create_config(config['ANILIST_CLIENT_ID'], config['ANILIST_CLIENT_SECRET'], Get_Access_Token())
                Config.save_config(config, 'config.json')
                RequestAPI.Set_Access_Token()
                refresh = RequestAPI.Check_Access_Token()
        while True:
            option = input("\n0. Exit\n1. Get Users Not Following Back\n2. Get Users You Are Not Following Back\n3. Follow Random Users From Global Activity Feed\nOption: ")
            if option == '0':
                break
            elif option == '1':
                print()
                RequestAPI.Get_User_ID()
                followers = RequestAPI.Get_Followers()
                print()
                following = RequestAPI.Get_Following()

                # Convert the lists to sets for easier comparison
                followers_set = set(followers)
                following_set = set(following)

                # Find the users that you are following but are not your followers
                not_following_back = following_set - followers_set

                # Load the excluded ids
                excluded_ids = list(Config.load_excluded_ids())
                not_following_back -= set(excluded_ids)
                
                if not_following_back != set():
                    print(f"\nNumber of Followers: {len(followers)}")
                    print(f"Number of Following: {len(following)}")
                    print(f"Number of Following Not Following Back: {len(not_following_back)}")
                    print(f"\nList of ID's:\n{list(not_following_back)}\n")

                    # Ask the user if they want to exclude any ids
                    while True:
                        action = input("Enter 'add' to exclude an ID, 'edit' to edit excluded IDs, 'done' to finish: ")
                        if action.lower() == 'done':
                            break
                        elif action.lower() == 'add':
                            exclude_id = input("Enter an ID to exclude: ")
                            excluded_id = int(exclude_id)
                            not_following_back.discard(excluded_id)
                            excluded_ids.append(excluded_id)
                        elif action.lower() == 'edit':
                            # Print the excluded ids in a numbered list
                            for i, id in enumerate(excluded_ids, start=1):
                                print(f"{i}. {id}")

                            # Ask the user if they want to remove or edit any ids
                            while True:
                                edit_id = input("Enter the number of the ID to remove or edit, 'add' to add a new ID, or 'done' to finish: ")
                                if edit_id.lower() == 'done':
                                    break
                                elif edit_id.lower() == 'add':
                                    new_id = input("Enter the new ID to add: ")
                                    excluded_ids.append(int(new_id))
                                else:
                                    edit_id = int(edit_id) - 1  # Subtract 1 because the list is 0-indexed
                                    if 0 <= edit_id < len(excluded_ids):
                                        action = input("Enter 'remove' to remove the ID or 'change' to change it: ")
                                        if action.lower() == 'remove':
                                            excluded_ids.pop(edit_id)
                                        elif action.lower() == 'change':
                                            new_id = input("Enter the new ID: ")
                                            excluded_ids[edit_id] = int(new_id)

                                # Reprint the list of excluded ids
                                print("\nExcluded IDs:")
                                for i, id in enumerate(excluded_ids, start=1):
                                    print(f"{i}. {id}")

                    # Save the excluded ids
                    Config.save_excluded_ids(set(excluded_ids))

                    print(f"\nNew List:\n{list(not_following_back)}")

                    option = input("\nWould you like to unfollow these users? (y/n): ")
                    if option == 'y':
                        for id in not_following_back:
                            RequestAPI.Unfollow_User(id)
                        print("Unfollowed all users not following back.")
                else:
                    print("No Followers Not Following Back.")
            elif option == '2':
                print()
                RequestAPI.Get_User_ID()
                followers = RequestAPI.Get_Followers()
                print()
                following = RequestAPI.Get_Following()

                # Convert the lists to sets for easier comparison
                followers_set = set(followers)
                following_set = set(following)

                # Find the users that are your followers but you are not following them
                not_following = followers_set - following_set
                if not_following != set():
                    print(f"\nNumber of Followers: {len(followers)}")
                    print(f"Number of Following: {len(following)}")
                    print(f"Number of Followers Not Following Back: {len(not_following)}")
                    print(f"\nList of ID's:\n{list(not_following)}\n")
                    
                    option = input("Would you like to follow these users? (y/n): ")
                    if option == 'y':
                        for id in not_following:
                            RequestAPI.Follow_User(id)
                        print("Followed all users not followed.")
                else:
                    print("\nYou are following all your followers.")
            elif option == '3':
                print()
                RequestAPI.Get_User_ID()
                total_people_to_follow = int(input("Enter the number of people you would like to follow: "))
                pages = total_people_to_follow // 50  # Each page contains 50 activities
                if pages < 1:
                    pages = 1
                RequestAPI.Get_Global_Activities(pages, total_people_to_follow)
                
        
if __name__ == '__main__':
    Main()