import json
import fitbit
import requests
import pandas as pd
import datetime
import traceback
import sqlite3
import gather_keys_oauth2 as Oauth2

from pprint import pprint
from collections import ChainMap

# store in a configuration
CLIENT_ID = ''
CLIENT_SECRET = ''
USER_DETAILS_FILE = 'user_details.json'


class FitbitAuthorization:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = ''
        self.refresh_token = ''
        self.expires_at = ''

    def _authorize(self):
        try:
            server=Oauth2.OAuth2Server(self.client_id, self.client_secret)
            server.browser_authorize()
        except Exception as e:
            print(traceback.format_exc())

    def process(self):
        # get user details
        self.access_token, self.refresh_token, self.expires_at = self._get_user_details()

        # browser authenticate if date today is greater than expires_at
        today = datetime.datetime.now().timestamp()
        if today > self.expires_at:
            self._authorize()

        return fitbit.Fitbit(
            self.client_id,
            self.client_secret,
            oauth2=True,
            access_token=self.access_token,
            refresh_token=self.refresh_token
        )
    
    def _get_user_details(self):
        """
        The specific user that you want to retrieve data for.
        """
        with open(USER_DETAILS_FILE) as f:
            fitbit_user = json.load(f)
            access_token = fitbit_user['access_token']
            refresh_token = fitbit_user['refresh_token']
            expires_at = fitbit_user['expires_at']

        return access_token, refresh_token, expires_at


def main():
    f = FitbitAuthorization(CLIENT_ID, CLIENT_SECRET)

    # returns a fitbit.exceptions.HTTPUnauthorized exception
    # access token is expired in the file while accessing the fitbit methods
    client = f.process()

    dt = datetime.datetime(2021, 4, 1)
    # sleep = client.get_sleep(dt)
    activities_heart = client.time_series(
        resource='activities/heart',
        base_date=dt,
        period='1d'
    )

    # just the detail of the activity
    # activities = client.activity_detail(activity_id=27)

    # activity type
    activities = client.activities_list()
    activity_categories = pd.DataFrame(activities['categories'], index=None)

    # activity_categories['id']
    # activity_categories['name']
    # activity_categories['activities']

    activities = activity_categories['activities']

    for s in activities:
        x = pd.DataFrame(s[0])
        print(x)



if __name__ == '__main__':
    main()