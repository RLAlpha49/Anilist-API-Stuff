"""
This module contains functions for handling API requests and rate limits.

Functions:
    Handle_Rate_Limit: Handles the rate limit of the API.
    API_Request: Sends a POST request to the API.
    Set_Headers: Sets the headers for the API requests.
"""

# pylint: disable=C0103

# Import necessary modules
import time

import requests

# Define the API endpoint
URL = "https://graphql.anilist.co"


def Handle_Rate_Limit(response):
    """
    Handles the rate limit of the API.

    Args:
        response (requests.Response): The response from the API request.

    Returns:
        None
    """
    rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
    rate_limit_reset = int(response.headers.get("X-RateLimit-Reset", 0))
    if response.status_code == 429:
        wait_time = max(rate_limit_reset - int(time.time()), 60)
        print(f"\nRate limit hit. Waiting for {wait_time} seconds.\n")
        time.sleep(wait_time)
    elif rate_limit_remaining < 5:
        print(
            f"Warning: Only {rate_limit_remaining} requests remaining until rate limit reset."
        )


def API_Request(query, variables=None):
    """
    Sends a POST request to the API.

    Args:
        query (str): The GraphQL query to send.
        variables (dict, optional): The variables for the GraphQL query. Defaults to None.

    Returns:
        dict: The JSON response from the API if the request is successful, None otherwise.
    """
    response = requests.post(
        URL, json={"query": query, "variables": variables}, headers=headers, timeout=10
    )
    # print(response.json())
    Handle_Rate_Limit(response)
    if response.status_code == 200:
        return response.json()
    if response.status_code == 429:
        return API_Request(query, variables)
    if response.status_code == 502:
        print("\nServer/Gateway error. Retrying...\n")
        return API_Request(query, variables)
    print(f"\nFailed to retrieve data. Status code: {response.status_code}\n")
    return None


def Set_Headers(header):
    """
    Sets the headers for the API requests.

    Args:
        header (dict): The headers to set for the API requests.
    """
    global headers  # pylint: disable=W0601
    headers = header
