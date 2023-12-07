# Import necessary modules
import webbrowser
import os
import platform

# Define the authorization URL for AniList OAuth
authorization_url = 'https://anilist.co/api/v2/oauth/authorize'

# Function to get the access token
def Get_Access_Token():
    client_id = os.environ.get('ANILIST_CLIENT_ID')
    if client_id:
        return Get_Authentication_Code(client_id)

# Function to get the authentication code
def Get_Authentication_Code(client_id): 
    # Set the authentication parameters and create the URL
    auth_params = {'client_id': client_id, 'response_type': 'token'}
    url = f'{authorization_url}?{"&".join([f"{key}={value}" for key, value in auth_params.items()])}'
    
    # Open the URL in the default browser
    if platform.system() == 'Linux':
        os.system(f'xdg-open {url}')  # For Linux
    else:
        webbrowser.open(url)  # For other platforms
    
    # Ask the user to enter the token from the URL and set it as an environment variable
    token = input("Please enter the token from the URL: ")
    os.environ['ACCESS_TOKEN'] = token
    return token