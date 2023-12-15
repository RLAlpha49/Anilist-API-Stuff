# Import necessary modules
from APIUsage.ActivityActions import Like_Activities
from APIUsage.Utils import Get_User_ID, Get_Mutual_Followers, Get_Not_Followed_Followers, Get_User_ID_From_Username, Get_Valid_Input, Is_Positive_Integer

def LikeUsersActivity():
    print()
    # Get the current user's ID
    Get_User_ID()

    # Ask the user to choose an option for the list of users
    choice = Get_Valid_Input("Do you want to enter a list of users, use the whole follower list, or only followers who follow you back? (Enter 'list', 'followers', 'mutual', or 'not followed'): ", ['list', 'followers', 'mutual', 'not followed'])

    # Process the user's choice
    if choice == 'list':
        # Convert the user input into a list of user IDs
        user_list = [int(user.strip()) if user.strip().isdigit() else Get_User_ID_From_Username(user.strip()) for user in input("Enter a comma-separated list of user IDs or usernames (e.g., 12345, 67890, username1, username2): ").split(',')]
    elif choice == 'mutual':
        # Get the list of mutual followers
        user_list = Get_Mutual_Followers()
    elif choice == 'not followed':
        # Get the list of followers not followed back
        user_list = Get_Not_Followed_Followers()
    elif choice == 'followers':
        # Use the whole follower list
        user_list = None

    # Get the number of activities to like per followed user and whether to include message activities
    total_activities_to_like = Get_Valid_Input("Enter the number of activities you would like to like per user (Max 100): ", validation_func=Is_Positive_Integer)
    include_message_activity = Get_Valid_Input("Do you want to like message activities? - Messages sent to the user are considered that users activity. (y/n): ", ['y', 'n']).lower() == 'y'

    print()
    # Call the function to like activities
    Like_Activities(total_activities_to_like, include_message_activity, user_list)