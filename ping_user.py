import sched, time
from typing import List
from core import User, ping_all_servers, PING_INTERVAL

# Put your user specific Discord webhook here
WEBHOOK_EXAMPLE = ""

# You can override PING_INTERVAL here if you want to adjust the frequency of pings per user

if __name__ == "__main__":
    """
    Users can be used to group miners by person, coldkey, etc.
    """
    users: List[User] = []

    # Initialize users
    example = User(
        "example",
        WEBHOOK_EXAMPLE,
        [
            # Name, IP, ping subtensor
            ("S01", "", True),
            ("S02", "", False),
        ],
        debug=True,  # Good for monitoring any potential errors / debug info in the script
        tz="Etc/GMT+0",  # Put in your timezone according to pytz
    )

    # How to find timezones
    # https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones

    # Add all users here
    users.extend([example])

    # Start the schedule
    s = sched.scheduler(time.time, time.sleep)
    s.enter(PING_INTERVAL, 1, ping_all_servers, (s, users))
    s.run()
