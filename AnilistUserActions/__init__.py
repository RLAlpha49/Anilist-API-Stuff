"""
This module imports all the necessary modules from the AnilistUserActions package 
for easy access in other parts of the program.

Modules:
    GetUsersNotFollowingBack
    GetUsersYouAreNotFollowingBack
    FollowRandomUsers
    LikeUsersActivity
    LikeFollowingFeed
    GetActivityCount
"""

# pylint: disable=C0103

# Allows for me to import all files from this folder
# from AnilistUserActions import *
from . import GetUsersNotFollowingBack
from . import GetUsersYouAreNotFollowingBack
from . import FollowRandomUsers
from . import LikeUsersActivity
from . import LikeFollowingFeed
from . import GetActivityCount
