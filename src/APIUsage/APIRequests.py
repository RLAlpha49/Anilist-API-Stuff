"""
This module contains functions for handling API requests and rate limits.

Functions:
    API_Request: Sends a POST request to the API.
    Set_Headers: Sets the headers for the API requests.
"""

# pylint: disable=C0103

# Import necessary modules
import time

import requests  # pylint: disable=E0401

# Define the API endpoint
URL = "https://graphql.anilist.co"


def API_Request(query, variables=None, max_retries=10):
    """
    Sends a POST request to the API.

    Args:
        query (str): The GraphQL query to send.
        variables (dict, optional): The variables for the GraphQL query. Defaults to None.
        max_retries (int, optional): The maximum number of retries if the request fails.

    Returns:
        dict: The JSON response from the API if the request is successful, None otherwise.
    """
    for _ in range(max_retries):
        try:
            response = requests.post(
                URL,
                json={"query": query, "variables": variables},
                headers=headers,
                timeout=20,
            )
            if response.status_code == 200:
                return response.json()
            if response.status_code == 429:
                print("\nRate limit hit. Waiting for 60 seconds.\n")
                time.sleep(60)
                continue
            if response.status_code == 500:
                print("\nAnilist server error. Retrying...\n")
                time.sleep(5)
                continue
            if response.status_code == 502:
                print("\nServer/Gateway error. Retrying...\n")
                time.sleep(5)
                continue
            print(f"\nFailed to retrieve data. Status code: {response.status_code}\n")
        except requests.exceptions.ReadTimeout:
            print("Request timed out. Retrying...")
    return None


def Set_Headers(header):
    """
    Sets the headers for the API requests.

    Args:
        header (dict): The headers to set for the API requests.
    """
    global headers  # pylint: disable=W0601
    headers = header
