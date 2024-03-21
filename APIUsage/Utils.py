"""
This module contains utility functions for the Anilist API. 

It includes functions for setting and checking access tokens, retrieving user IDs, 
getting follow data, comparing followers and following, and validating user input.
"""

# pylint: disable=C0103, E0401

# Import necessary modules
import operator
import requests
import Config
import QueriesAndMutations as QM
from .API import Get_Access_Token  # pylint: disable=E0402
from .APIRequests import API_Request, Set_Headers  # pylint: disable=E0402


# Define the API endpoint
URL = "https://graphql.anilist.co"

# Token and header related functions: These functions are related
# to setting and checking the access token.


def Set_Access_Token():
    """
    Sets the access token for the API requests.

    This function retrieves the access token from the configuration file,
    sets it in the headers for the API requests, and saves it back to the
    configuration file if it was not found.
    """
    global headers  # pylint: disable=w0601
    config = Config.load_config("config.json")
    try:
        if config["ACCESS_TOKEN"] is not None:
            # Get the access token
            access_token = config["ACCESS_TOKEN"]

            # Define the headers for the API request
            headers = {"Authorization": f"Bearer {access_token}"}
            Set_Headers(headers)
        else:
            print("No access token found.")
            config["ACCESS_TOKEN"] = Get_Access_Token()
            Config.save_config(config, "config.json")
            Config.Set_Environment_Variables(config)
    except TypeError:
        print("No config file found")
        return


def Check_Access_Token():
    """
    Checks the validity of the access token.

    This function sends a request to the API with the current access token.
    If the response status code indicates an error, it prints an error message
    and returns True. If the token is valid, it prints a success message and
    returns False. If the headers are not set, it sets the access token and
    checks again.

    Returns:
        bool: True if the access token is invalid, False otherwise.
    """
    try:
        query = QM.Queries.Check_Authentication()
        response = requests.post(
            URL, json={"query": query}, headers=headers, timeout=10
        )
        status_code_errors = {
            401: "Error: Invalid Access Token",
            400: "Error: Invalid Access Token",
        }
        if response.status_code in status_code_errors:
            print(status_code_errors[response.status_code])
            return True
        print("\nToken is valid.\n")
        return False
    except NameError:
        Set_Access_Token()
        return Check_Access_Token()


# User ID related functions: These functions are related to getting user IDs.


def Get_User_ID():
    """
    Retrieves the user ID of the authenticated user.

    This function sends a request to the API to retrieve the user ID of the
    authenticated user and sets the global user_id variable to this value.

    Returns:
        int: The user ID of the authenticated user.
    """
    global user_id  # pylint: disable=w0601
    query = QM.Queries.Check_Authentication()
    response = API_Request(query)
    user_id = response["data"]["Viewer"]["id"]
    return response["data"]["Viewer"]["id"]


def Get_User_ID_From_Username(username):
    """
    Retrieves the user ID of a user given their username.

    Args:
        username (str): The username of the user.

    Returns:
        int: The user ID of the user if found, None otherwise.
    """
    query, variables = QM.Queries.Get_User_ID_Query(username)
    response = API_Request(query, variables)
    if "User" in response["data"] and "id" in response["data"]["User"]:
        return response["data"]["User"]["id"]
    print(f"Error: User {username} not found")
    return None


# Follow data related functions: These functions are related to getting follow data.


def get_follow_data(query_func, message, key, page=1):
    """
    Retrieves follow data for a user.

    This function sends requests to the API to retrieve follow data for a user
    and returns a list of IDs of the followed users.

    Args:
        query_func (function): The function to generate the query and variables.
        message (str): The message to print for each page of results.
        key (str): The key to use to extract the data from the response.
        page (int, optional): The page of results to start from. Defaults to 1.

    Returns:
        list: A list of IDs of the followed users.
    """
    ids = []

    while True:
        query, variables = query_func(user_id, page)
        response = API_Request(query, variables)

        for user in response["data"]["Page"][key]:
            ids.append(user["id"])

        print(
            f"{message}, Page {page} ID's: {ids[-len(response['data']['Page'][key]):]}"
        )
        if not response["data"]["Page"]["pageInfo"]["hasNextPage"]:
            break
        page += 1
    return ids


def Get_Followers():
    """
    Retrieves the followers of the authenticated user.

    This function sends a request to the API to retrieve the followers of the
    authenticated user and returns a list of IDs of the followers.

    Returns:
        list: A list of IDs of the followers.
    """
    return get_follow_data(QM.Queries.Follower_Query, "Checking Followers", "followers")


def Get_Following():
    """
    Retrieves the users that the authenticated user is following.

    This function sends a request to the API to retrieve the users that the
    authenticated user is following and returns a list of IDs of these users.

    Returns:
        list: A list of IDs of the users that the authenticated user is following.
    """
    return get_follow_data(
        QM.Queries.Following_Query, "Checking Following", "following"
    )


# Comparison functions: These functions are related to comparing followers and following.


def Compare_Followers(followers, following, operation):
    """
    Compares the followers and following lists using a specified operation.

    Args:
        followers (list): A list of IDs of the followers.
        following (list): A list of IDs of the users being followed.
        operation (function): The operation to use to compare the lists.

    Returns:
        list: The result of the operation on the followers and following lists.
    """
    result = operation(set(following), set(followers))
    return list(result)


def Get_Mutual_Followers():
    """
    Retrieves the mutual followers of the authenticated user.

    This function sends requests to the API to retrieve the followers and
    following of the authenticated user and returns a list of IDs of the
    mutual followers.

    Returns:
        list: A list of IDs of the mutual followers.
    """
    followers = Get_Followers()
    print()
    following = Get_Following()
    print()
    return Compare_Followers(followers, following, operator.and_)


def Get_Not_Followed_Followers():
    """
    Retrieves the followers of the authenticated user that the user is not following back.

    This function sends requests to the API to retrieve the followers and
    following of the authenticated user and returns a list of IDs of the
    followers that the user is not following back.

    Returns:
        list: A list of IDs of the followers that the user is not following back.
    """
    followers = Get_Followers()
    print()
    following = Get_Following()
    print()
    return Compare_Followers(followers, following, operator.sub)


# Input functions: These functions are related to getting user input.


def Get_Valid_Input(prompt, valid_inputs=None, validation_func=None):
    """
    Prompts the user for input and validates it.

    This function prompts the user for input and checks if it is in a list of
    valid inputs or if it passes a validation function. If the input is valid,
    it is returned. If not, the user is prompted again.

    Args:
        prompt (str): The prompt to display to the user.
        valid_inputs (list, optional): A list of valid inputs. Defaults to None.
        validation_func (function, optional): A function to validate the input.
            Defaults to None.

    Returns:
        str or int: The user's input if it is valid. If the validation function
            is Is_Positive_Integer, the input is returned as an int.
    """
    while True:
        user_input = input(prompt)
        if valid_inputs and user_input in valid_inputs:
            return user_input
        if validation_func and validation_func(user_input):
            return (
                int(user_input)
                if validation_func == Is_Positive_Integer  # pylint: disable=W0143
                else user_input
            )
        print("Invalid input. Please try again.")


def Is_Positive_Integer(s):
    """
    Checks if a string represents a positive integer.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string represents a positive integer, False otherwise.
    """
    return s.isdigit() and int(s) > 0


def Is_Valid_Time_Period(s):
    """
    Checks if a string represents a valid time period.

    A valid time period is a positive integer followed by an optional unit.
    The unit can be 'w' for weeks, 'm' for months, or 'y' for years. If no
    unit is provided, the time period is assumed to be in days.

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string represents a valid time period, False otherwise.
    """
    if s.isdigit():
        return True  # Days
    if s.endswith("w") and s[:-1].isdigit():
        return True  # Weeks
    if s.endswith("m") and s[:-1].isdigit():
        return True  # Months
    if s.endswith("y") and s[:-1].isdigit():
        return True  # Years
    return False


def Convert_Time_To_Seconds(time_back):
    """
    Converts a time period to seconds.

    The time period is a string that ends with 'w', 'm', 'y', or no unit.
    'w' stands for weeks, 'm' stands for months, 'y' stands for years. If no
    unit is provided, the time period is assumed to be in days.

    Args:
        time_back (str): The time period to convert.

    Returns:
        int: The time period in seconds.
    """
    # Convert the time period to seconds
    if time_back.endswith("w"):
        time_back_seconds = int(time_back[:-1]) * 7 * 24 * 60 * 60
    elif time_back.endswith("m"):
        time_back_seconds = int(time_back[:-1]) * 30 * 24 * 60 * 60
    elif time_back.endswith("y"):
        time_back_seconds = int(time_back[:-1]) * 365 * 24 * 60 * 60
    else:
        time_back_seconds = int(time_back) * 24 * 60 * 60
    return time_back_seconds
