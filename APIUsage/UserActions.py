# Import necessary modules
import QueriesAndMutations as QM
from .APIRequests import API_Request


def Like_Activity(id):
    query, variables = QM.Mutations.Like_Mutation(id)
    response = API_Request(query, variables)
    if response is not None and "errors" not in response:
        return True
    else:
        print(f"Failed to like activity with ID: {id}")
        return False


def Toggle_Follow_User(id, desired_status, success_message, error_message):
    query, variables = QM.Mutations.Follow_Mutation(id)
    response = API_Request(query, variables)
    if response is not None:
        if response["data"]["ToggleFollow"]["isFollowing"] == desired_status:
            print(success_message.format(response["data"]["ToggleFollow"]["name"], id))
            return True
        else:
            print(error_message.format(response["data"]["ToggleFollow"]["name"], id))
            Toggle_Follow_User(id, desired_status, success_message, error_message)
    else:
        print(
            f"Failed to update follow status for user with ID: {id}\nUser account most likely deleted."
        )
        return False


def Unfollow_User(id):
    return Toggle_Follow_User(
        id,
        False,
        "Unfollowed {} with ID: {}",
        "Error: {} already unfollowed with ID: {}",
    )


def Follow_User(id):
    return Toggle_Follow_User(
        id, True, "Followed {} with ID: {}", "Error: {} already followed with ID: {}"
    )
