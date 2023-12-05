# Import necessary modules
import os
import json

# Helper function to load JSON data from a file
def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None

# Helper function to save JSON data to a file
def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to create a configuration dictionary
def create_config(client, secret, token=None):
    return {
        'ANILIST_CLIENT_ID': client,
        'ANILIST_CLIENT_SECRET': secret,
        'ACCESS_TOKEN': token,
    }

# Function to save a configuration dictionary to a file
def save_config(config, file_path):
    save_json(config, file_path)

# Function to load a configuration dictionary from a file
def load_config(file_path):
    config = load_json(file_path)
    return config if config is not None else None

# Function to set environment variables from a configuration dictionary
def Set_Environment_Variables(config):
    for key, value in config.items():
        if value is not None:
            os.environ[key] = value

# Function to load a set of excluded IDs from a file
def load_excluded_ids():
    excluded_ids = load_json('excluded_ids.json')
    return set(excluded_ids) if excluded_ids is not None else set()

# Function to save a set of excluded IDs to a file
def save_excluded_ids(excluded_ids):
    save_json(list(excluded_ids), 'excluded_ids.json')