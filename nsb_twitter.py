import twitter as twitter_api


def readConfig(file_name):
    f = open(file_name)
    result = f.read()
    f.close()
    return result.rstrip()

def initTwitterAgent(file_name, consumer_key, consumer_secret):

    oauth_token, oauth_secret = twitter_api.read_token_file(file_name)

    return twitter_api.Twitter(auth=twitter_api.OAuth(
        oauth_token, oauth_secret, consumer_key, consumer_secret))

class twitter:


    def __init__(self, configDir):
        key = readConfig(configDir + 'consumer_key')
        secret = readConfig(configDir + 'consumer_secret')
        credentialsFile = configDir + 'credentials'
        self.agent = initTwitterAgent(credentialsFile, key, secret)



    def checkTwitterHandle(self, handle):
        try:
            self.agent.users.show(screen_name=handle)
            return handle
        except Exception as e:
            print('you should specify {} in this except.'.format(e))
            return None


    def postTweet(self, text):
        self.agent.statuses.update(status=text)


    def userTweetCount(self, name):
        return self.agent.users.show(screen_name=name)['statuses_count']
