import os.path
import twitter as twitter_api
from nsb_config import options

def _read_config(file_name):
    with open(os.path.join(options['twitter_keys'], file_name),
            encoding='utf-8') as f:
        return f.read().rstrip()

class Twitter:
    def __init__(self):
        consumer_key = _read_config('consumer_key')
        consumer_secret = _read_config('consumer_secret')
        oauth_token, oauth_secret = twitter_api.read_token_file(
                os.path.join(options['twitter_keys'], 'credentials'))
        self.agent = twitter_api.Twitter(auth=twitter_api.OAuth(
            oauth_token, oauth_secret, consumer_key, consumer_secret))

    def checkTwitterHandle(self, handle):
        try:
            self.agent.users.show(screen_name=handle)
            return handle
        except Exception as e: # pylint: disable=broad-except
            print(f'you should specify {e} in this except.')
            return None

    def postTweet(self, text):
        self.agent.statuses.update(status=text)

if options['twitter_keys']:
    twitter = Twitter()
else:
    twitter = None
