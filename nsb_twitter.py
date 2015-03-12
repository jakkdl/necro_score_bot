import twitter
import os

class twit:
    def readConfig(self, file):
        f = open(file)
        result = f.read()
        f.close()
        return result.rstrip()

    def initTwitterAgent(self, file, consumer_key, consumer_secret):

        oauth_token, oauth_secret = twitter.read_token_file(file)

        return twitter.Twitter(auth=twitter.OAuth(
            oauth_token, oauth_secret, consumer_key, consumer_secret))



    def __init__(self, configDir):
        print(configDir)
        key = self.readConfig(configDir + 'consumer_key')
        secret = self.readConfig(configDir + 'consumer_secret')
        credentialsFile = configDir + 'credentials'
        self.agent = self.initTwitterAgent(credentialsFile, key, secret)






    def checkTwitterHandle(self, handle):
        try:
            self.agent.users.show(screen_name=handle)
            return handle
        except:
            return None


    def postTweet(self, text):
        self.agent.statuses.update(status=text)
