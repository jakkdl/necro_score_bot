import math
import os.path
import twitter as twitter_api


class twitter:
    def readConfig(self, config_file):
        if not os.path.isfile(config_file):
            return None
        with open(config_file, encoding='utf8') as file:
            result = file.read()
        return result.rstrip()

    def initTwitterAgent(self, file, consumer_key, consumer_secret):

        oauth_token, oauth_secret = twitter_api.read_token_file(file)

        return twitter_api.Twitter(
            auth=twitter_api.OAuth(
                oauth_token, oauth_secret, consumer_key, consumer_secret
            )
        )

    def __init__(self, configDir):
        key = self.readConfig(configDir + 'consumer_key')
        secret = self.readConfig(configDir + 'consumer_secret')
        credentialsFile = configDir + 'credentials'
        if key and secret and credentialsFile:
            self.agent = self.initTwitterAgent(credentialsFile, key, secret)
        else:
            self.agent = None

        self.tweetCount = 0
        self.blockFile = configDir + 'blockFile'
        self.blockCheck()
        # self.block = self.blockCheck()

    def createBlock(self):
        # TODO: wtf???
        open(self.blockFile, 'w', encoding='utf-8')

    def blockExists(self):
        return os.path.isfile(self.blockFile)

    def blockCheck(self):
        if self.tweetCount > 20:
            self.createBlock()
        if self.blockExists():
            raise LookupError('Tweeting is blocked')

    def incrementCount(self):
        self.tweetCount += 1

    def checkTwitterHandle(self, handle):
        try:
            self.agent.users.show(screen_name=handle)
            return handle
        except:
            return None

    def postTweet(self, text):
        self.incrementCount()
        self.blockCheck()
        self.agent.statuses.update(status=text)

    def userTweetCount(self, name):
        return self.agent.users.show(screen_name=name)['statuses_count']

    def timeline(self, name, count=-1, max_id=-1):
        if count == -1:
            count = self.userTweetCount(name)

        result = []

        for _ in range(math.ceil(count / 200)):
            print(max_id)
            if max_id == -1:
                tmp = self.agent.statuses.user_timeline(screen_name=name, count=count)
            else:
                tmp = self.agent.statuses.user_timeline(
                    screen_name=name, count=count, max_id=max_id
                )

            # extract id of last tweet gathered, and get tweets at least
            # one id smaller(older
            max_id = tmp[-1]['id'] - 1
            result += tmp

        return result
