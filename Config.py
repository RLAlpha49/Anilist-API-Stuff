# Import necessary modules
import os
import json

# Function to create a configuration dictionary
def create_config(client, secret, token=None):
    # Create and return the configuration dictionary directly
    return {
        'ANILIST_CLIENT_ID': client,  # The client ID for the AniList API
        'ANILIST_CLIENT_SECRET': secret,  # The client secret for the AniList API
        'ACCESS_TOKEN': token,  # The access token for the AniList API
    }

# Function to save the configuration dictionary to a file
def save_config(config, file_path):
    # Open the configuration file in write mode
    with open(file_path, 'w') as file:
        # Write the configuration dictionary to the file in JSON format
        json.dump(config, file, indent=4)

# Function to load the configuration dictionary from a file
def load_config(file_path):
    try:
        # Open the configuration file in read mode
        with open(file_path, 'r') as file:
            # Load the configuration dictionary from the file
            config = json.load(file)
        # Return the configuration dictionary
        return config
    except FileNotFoundError:
        # If the configuration file is not found, return None
        return None

# Function to set the environment variables
def Set_Environment_Variables(config):
    # Set the environment variables with the values from the configuration dictionary
    for key, value in config.items():
        if value is not None:
            os.environ[key] = value
            
def load_excluded_ids():
    try:
        with open('excluded_ids.json', 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_excluded_ids(excluded_ids):
    with open('excluded_ids.json', 'w') as f:
        json.dump(list(excluded_ids), f)