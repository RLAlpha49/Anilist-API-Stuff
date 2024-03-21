"""
This module contains the Setup function which is responsible for setting up the
environment for the application. It loads the configuration from a JSON file,
sets up the environment variables, and manages the access token for the Anilist API.
"""

# pylint: disable=C0103

# Import necessary modules
import Config
from APIUsage.Utils import Check_Access_Token, Get_Access_Token, Set_Access_Token


def Setup():
    """
    Loads the configuration from a JSON file and sets up the environment variables.
    If the configuration file is not found, it prompts the user to enter the
    Client ID and Secret ID. It then creates and saves a new configuration, sets
    the environment variables, and sets the access token. If the access token is
    not valid, it refreshes the access token.
    """
    # Load configuration and ask for client and secret IDs if not found
    config = Config.load_config("config.json")
    if not config:
        input("Config file not found. Press enter to continue...")
        print(
            "Please create an API on Anilist for the following values "
            "(Set Redirect URL to: https://anilist.co/api/v2/oauth/pin):"
        )
        client = input("Enter Client ID: ")
        secret = input("Enter Secret ID: ")

        # Create and save new configuration, set environment variables and access token
        config = Config.create_config(client, secret, Get_Access_Token())
        Config.save_config(config, "config.json")
        Config.Set_Environment_Variables(config)
        Set_Access_Token()
    else:
        client = config["ANILIST_CLIENT_ID"]
        secret = config["ANILIST_CLIENT_SECRET"]
        Config.Set_Environment_Variables(config)

    # Refresh access token if it's not valid
    refresh = Check_Access_Token()
    while refresh:
        config = Config.create_config(client, secret, Get_Access_Token())
        Config.save_config(config, "config.json")
        Set_Access_Token()
        refresh = Check_Access_Token()
