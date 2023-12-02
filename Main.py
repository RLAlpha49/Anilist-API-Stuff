from Config import load_config, save_config, create_config, Get_Config, Set_Environment_Variables
from API import Get_Access_Token
import RequestAPI as RequestAPI
import time
import os
import QueriesAndMutations as QM

class Main():
    def __init__(self):
        config = load_config('config.json')
        if not config:
            input("Config file not found. Press enter to continue...")
            print("Please create an API on Anilist for the following values (Set Rediruct URL to: https://anilist.co/api/v2/oauth/pin):")
            client = input("Enter Client ID:")
            secret = input("Enter Secret ID:")
            config = create_config(client, secret)
            save_config(config, 'config.json')
            Set_Environment_Variables(config)
            config = create_config(client, secret, Get_Access_Token())
            save_config(config, 'config.json')
        else:
            Set_Environment_Variables(config)
            if os.environ.get('ACCESS_TOKEN') is None:
                config = create_config(client, secret, Get_Access_Token())
                save_config(config, 'config.json')
            RequestAPI.Set_Access_Token()
            
            refresh = RequestAPI.Check_Access_Token()
            while refresh:
                config = load_config('config.json')
                config = create_config(config['ANILIST_CLIENT_ID'], config['ANILIST_CLIENT_SECRET'], Get_Access_Token())
                save_config(config, 'config.json')
                RequestAPI.Set_Access_Token()
                refresh = RequestAPI.Check_Access_Token()
        
        option = input("0. Exit\n1. Get Users Not Following Back\n")
        if option == '0':
            return
        elif option == '1':
            RequestAPI.Get_User_ID()
            followers = RequestAPI.Get_Followers()
            following = RequestAPI.Get_Following()

            # Convert the lists to sets for easier comparison
            followers_set = set(followers)
            following_set = set(following)

            # Find the users that you are following but are not your followers
            not_following_back = following_set - followers_set
            
            print(f"\nList of ID's:\n{list(not_following_back)}\n")

            # Ask the user if they want to exclude any ids
            while True:
                exclude_id = input("Enter an ID to exclude or 'done' to finish: ")
                if exclude_id.lower() == 'done':
                    break
                not_following_back.discard(int(exclude_id))

            print(f"\nNew List:\n{list(not_following_back)}")
        
if __name__ == '__main__':
    Main()