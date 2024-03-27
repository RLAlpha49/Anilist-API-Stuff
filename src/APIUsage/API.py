"""
This module contains functions for retrieving the access token and authentication code.

Functions:
    Get_Access_Token: Retrieves the access token from the environment variables.
    Get_Authentication_Code: Retrieves the authentication code for a given client ID.
"""

# pylint: disable=C0103

# Import necessary modules
import os
import platform
import webbrowser

# Define the authorization URL for AniList OAuth
AUTHORIZATION_URL = "https://anilist.co/api/v2/oauth/authorize"


# Function to get the access token
def Get_Access_Token():
    """
    Retrieves the access token from the environment variables.

    Returns:
        str: The access token if it exists, None otherwise.
    """
    client_id = os.environ.get("ANILIST_CLIENT_ID")
    if client_id:
        return Get_Authentication_Code(client_id)
    return None


# Function to get the authentication code
def Get_Authentication_Code(client_id):
    """
    Retrieves the authentication code for a given client ID.

    Args:
        client_id (str): The client ID for which to retrieve the authentication code.

    Returns:
        str: The authentication code.
    """
    # Set the authentication parameters and create the URL
    auth_params = {"client_id": client_id, "response_type": "token"}
    url = (
        f"{AUTHORIZATION_URL}?"
        f'{"&".join([f"{key}={value}" for key, value in auth_params.items()])}'
    )

    # Open the URL in the default browser
    if platform.system() == "Linux":
        os.system(f"xdg-open {url}")  # For Linux
    else:
        webbrowser.open(url)  # For other platforms

    # Ask the user to enter the token from the URL and set it as an environment variable
    token = input("Please enter the token from the URL: ")
    os.environ["ACCESS_TOKEN"] = token
    return token
