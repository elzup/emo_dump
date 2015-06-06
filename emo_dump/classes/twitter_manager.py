import traceback

import tweepy
from django.conf import settings
from functools import reduce


class TwitterManager:
    def __init__(self, session, set_api=True):
        self.is_login = 'key' in session
        self.auth = None
        self.auth_url = None

        if not self.is_login:
            return
        if set_api:
            self.api = self.get_api(session.get('key'), session.get('secret'))

    def get_api(self, token, secret):
        auth = self.get_auth()
        auth.set_access_token(token, secret)
        return tweepy.API(auth_handler=auth)

    def get_auth(self, callback=None):
        return tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET, callback)

    def user_timeline(self, screen_name=None, page_count=1):
        statuses_all = []
        max_id = None

        for status in tweepy.Cursor(self.api.user_timeline,
                                     screen_name=screen_name,
                                     count=200,
                                     include_rts=False).pages(page_count):
            print(len(status))
            statuses_all.extend(status)
        return statuses_all

    def rate_limit_status_userstimeline(self):
        limit = self.api.rate_limit_status(resources="statuses")
        return limit['resources']['statuses']['/statuses/user_timeline']

    def auth_start(self):
        self.auth = self.get_auth(settings.CALLBACK_URL)
        try:
            self.auth_url = self.auth.get_authorization_url()
        except tweepy.TweepError:
            print(traceback.format_exc())

    def auth_end(self, verifier, token):
        self.auth = self.get_auth()
        self.auth.request_token = token
        self.auth.get_access_token(verifier)
