# Anilist Follower & Liking Tool

**Notice:** Program is compiled with pyinstaller so some anti-viruses may give false positives. For people who want to compile it themselves download the source files and run `Main.py`. There is a script that will install the necessary python modules in the source files and releases.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [License](#license)

## Features
This program is a utility for interacting with the Anilist API. It provides several features to manage your Anilist account:

### Get Users Not Following Back
This feature retrieves a list of users that you are following but who are not following you back. 
- Option to exclude certain users from this list.
- Option to unfollow these users.

### Get Users You Are Not Following Back
This feature retrieves a list of users who are following you, but you are not following back. 
- Option to follow these users.

### Follow Random Users From Global Activity Feed
This feature allows you to follow a specified number of random users from the global activity feed.

### Like Followed Users Activity
This feature allows you to like a specified number of activities from each user you are following. 
- Option to include message activities.

## Installation
 - The `AnilistFollwerAndLikingTool.exe` file requires no prerequisites. Just run it.
 - For those compiling it themselves
   - Download the source files
   - Download the required python packages with the included `InstallPackages.py` script or yourself
   - Run `Main.py`

## License
Distributed under the GNU General Public License v3.0 License. See `LICENSE` for more information.
