from datetime import datetime
from typing import List, Tuple
import requests
from requests.adapters import HTTPAdapter
import time
import subprocess
import pytz

# Look up a tutorial on how to set up Discord webhooks for your own server

# Put your general notifications webhook here
WEBHOOK_GENERAL = ""

# The port your subtensors use (must be the same for all)
SUBTENSOR_PORT = 9944

# How many seconds between pings
PING_INTERVAL = 300

# Number of attempts to make if the initial server connection fails
NUM_ATTEMPTS = 5  # Max 10

# How many seconds to wait after each failed attempt
SLEEP_DELAY = 2  # Max 4 (if NUM_ATTEMPTS=5)


class User:
    def __init__(
        self,
        name: str,
        webhook: str,
        servers: List[Tuple[str, str, bool]],
        debug: bool = False,
        tz: str = "Etc/GMT+0",
    ):
        self.name = name
        self.servers = servers
        self.webhook = webhook
        self.debug = debug
        self.pytz = tz
        self.timezone_display = self.pytz.split("/")[-1]
        self.tz = pytz.timezone(self.pytz)

    """
    Note that the servers should be a list of tuples containing the server name,
    server IP and a True/False value for whether to check subtensor or not. (True=check)
    """

    def __send_notification(self, message: str):
        """
        Send a notification to the Discord webhook
        """
        json_dict = {"content": f"{message}"}
        r = requests.post(self.webhook, json_dict)

        if self.debug:
            print(f"\nDiscord headers:")
            if r:
                print(f"{r.status_code=}")
                print(f"{r.headers['x-ratelimit-limit']=}")
                print(f"{r.headers['x-ratelimit-remaining']=}")
                print(f"{r.headers['x-ratelimit-reset']=}")
                print(f"{r.headers['x-ratelimit-reset-after']=}\n")
            else:
                print("An error occurred: request is None")

    def __ping_server(self, ip: str):
        """
        Send a ping to the specified IP.
        Returns true if the server is online.
        It is possible to get a false-positive.
        """
        is_server_online = False
        for i in range(NUM_ATTEMPTS):
            try:
                subprocess.check_call(
                    ["ping", "-c", "1", ip],
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    timeout=5,
                )
                is_server_online = True
            except Exception as e:
                if self.debug:
                    print(f"{i+1}: {e=}")

            if is_server_online or (i == NUM_ATTEMPTS - 1):
                break

            # Add an increasing delay after each attempt
            time.sleep(SLEEP_DELAY + (SLEEP_DELAY * i))

        return is_server_online

    def __ping_subtensor(self, ip: str):
        """
        Send a ping to subtensor at the specified IP.
        You should not see false positives.
        """
        is_subtensor_online = False
        try:
            with requests.Session() as s:
                s.mount("http://", HTTPAdapter(max_retries=1))
                response = s.get(
                    f"http://{ip}:{SUBTENSOR_PORT}"
                )  # Default timeout is 2.5 seconds

            if self.debug:
                print(f"Subtensor: {response.status_code=}")

            # Status code 400 = Bad request
            # If this is returned, it means subtensor is online
            if response.status_code == 400:
                is_subtensor_online = True
            else:
                if self.debug:
                    print(f"Subtensor-alt: {response.status_code=}")
        except Exception as e:
            if self.debug:
                pass
                # print(f"Sub error {e=}")
        return is_subtensor_online

    def ping_servers(self):
        """
        Iterate the servers provided for each user and ping the subtensor on them.
        """
        for name, ip, check_subtensor in self.servers:
            if self.debug:
                print(f"[----Pinging {name}'s IP {ip}----]")

            is_server_online: bool = self.__ping_server(ip)

            if self.debug:
                print(f"Server online: {is_server_online}")

            dt = datetime.strftime(datetime.now(tz=self.tz), "%d/%m/%y %I:%M %p")

            # You can adjust how the message looks here
            lines = "----------------------------------------------------------------------------------------------------"
            message = f"{lines}\n---- {name} @ {ip}\n{lines}\n---- {dt} ({self.timezone_display})\n{lines}\n"
            message = (
                f"{message}---- Server: {'ONLINE' if is_server_online else 'OFFLINE'}"
            )

            if not is_server_online:
                self.__send_notification(f"{message}\n{lines}")
            else:
                if check_subtensor:
                    is_subtensor_online: bool = self.__ping_subtensor(ip)
                    if self.debug:
                        print(f"Subtensor online: {is_subtensor_online}")
                    message = f"{message} ---- Subtensor: {'ONLINE' if is_subtensor_online else 'OFFLINE'}\n{lines}"
                    if not is_subtensor_online:
                        self.__send_notification(f"{message}")

            if self.debug:
                print("\n")


def ping_all_servers(sc, users):
    """
    Iterate the list of users and call the ping_servers() function.
    Ping the global webhook (optional).
    """
    for user in users:
        dt = datetime.strftime(datetime.now(tz=user.tz), "%d/%m/%Y at %I:%M %p")
        if user.debug:
            print(f"Pinging {user.name} on {dt} ({user.timezone_display})")
        user.ping_servers()
        if user.debug:
            print(
                f"Finished pinging {user.name}'s servers on {dt} ({user.timezone_display})"
            )

        if WEBHOOK_GENERAL:
            requests.post(
                WEBHOOK_GENERAL,
                {
                    "content": f"Pinged {user.name}'s servers on {dt} ({user.timezone_display})"
                },
            )

    sc.enter(PING_INTERVAL, 1, ping_all_servers, (sc, users))
