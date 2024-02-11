# Import necessary modules
import requests
import time

# Define the API endpoint
url = "https://graphql.anilist.co"


def Handle_Rate_Limit(response):
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
    response = requests.post(
        url, json={"query": query, "variables": variables}, headers=headers
    )
    # print(response.json())
    Handle_Rate_Limit(response)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        return API_Request(query, variables)
    elif response.status_code == 502:
        print("\nServer/Gateway error. Retrying...\n")
        return API_Request(query, variables)
    else:
        print(f"\nFailed to retrieve data. Status code: {response.status_code}\n")
        return None


def Set_Headers(header):
    global headers
    headers = header
