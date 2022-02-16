import os.path
from typing import Optional
import twitter as twitter_api
from nsb_config import options


def _read_config(file_name: str) -> str:
    with open(
        os.path.join(options["twitter_keys"], file_name), encoding="utf-8"
    ) as file:
        return file.read().rstrip()


class Twitter:
    def __init__(self) -> None:
        try:
            consumer_key = _read_config("consumer_key")
            consumer_secret = _read_config("consumer_secret")
            oauth_token, oauth_secret = twitter_api.read_token_file(
                os.path.join(options["twitter_keys"], "credentials")
            )
        except FileNotFoundError:
            self.agent = None
        finally:
            self.agent = twitter_api.Twitter(
                auth=twitter_api.OAuth(
                    oauth_token, oauth_secret, consumer_key, consumer_secret
                )
            )

    def check_twitter_handle(self, handle: str) -> Optional[str]:
        if not self.agent:
            return None
        try:
            self.agent.users.show(screen_name=handle)
            return handle
        except Exception as exception:  # pylint: disable=broad-except
            print(f"you should specify {exception} in this except.")
            return None

    def post_tweet(self, text: str) -> None:
        if not self.agent:
            print(f"Tweet: {text}")
            return
        self.agent.statuses.update(status=text)


twitter = Twitter()
