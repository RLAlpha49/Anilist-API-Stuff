# Import necessary modules
import QueriesAndMutations as QM
from .API import Get_Access_Token
from .APIRequests import API_Request, Set_Headers
import Config
import requests
import operator

# Define the API endpoint
url = "https://graphql.anilist.co"

# Token and header related functions: These functions are related to setting and checking the access token.


def Set_Access_Token():
    global headers
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
    try:
        query = QM.Queries.Check_Authentication()
        response = requests.post(url, json={"query": query}, headers=headers)
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
    global user_id
    query = QM.Queries.Check_Authentication()
    response = API_Request(query)
    user_id = response["data"]["Viewer"]["id"]
    return response["data"]["Viewer"]["id"]


def Get_User_ID_From_Username(username):
    query, variables = QM.Queries.Get_User_ID_Query(username)
    response = API_Request(query, variables)
    if "User" in response["data"] and "id" in response["data"]["User"]:
        return response["data"]["User"]["id"]
    print(f"Error: User {username} not found")
    return None


# Follow data related functions: These functions are related to getting follow data.


def get_follow_data(query_func, message, key, page=1):
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
    return get_follow_data(QM.Queries.Follower_Query, "Checking Followers", "followers")


def Get_Following():
    return get_follow_data(
        QM.Queries.Following_Query, "Checking Following", "following"
    )


# Comparison functions: These functions are related to comparing followers and following.


def Compare_Followers(followers, following, operation):
    result = operation(set(following), set(followers))
    return list(result)


def Get_Mutual_Followers():
    followers = Get_Followers()
    print()
    following = Get_Following()
    print()
    return Compare_Followers(followers, following, operator.and_)


def Get_Not_Followed_Followers():
    followers = Get_Followers()
    print()
    following = Get_Following()
    print()
    return Compare_Followers(followers, following, operator.sub)


# Input functions: These functions are related to getting user input.


def Get_Valid_Input(prompt, valid_inputs=None, validation_func=None):
    while True:
        user_input = input(prompt)
        if valid_inputs and user_input in valid_inputs:
            return user_input
        elif validation_func and validation_func(user_input):
            return (
                int(user_input)
                if validation_func == Is_Positive_Integer
                else user_input
            )
        else:
            print("Invalid input. Please try again.")


def Is_Positive_Integer(s):
    return s.isdigit() and int(s) > 0


def Is_Valid_Time_Period(s):
    if s.isdigit():
        return True  # Days
    elif s.endswith("w") and s[:-1].isdigit():
        return True  # Weeks
    elif s.endswith("m") and s[:-1].isdigit():
        return True  # Months
    elif s.endswith("y") and s[:-1].isdigit():
        return True  # Years
    return False


def Convert_Time_To_Seconds(time_back):
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
