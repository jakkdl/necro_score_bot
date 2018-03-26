#!/usr/bin/python3
import shutil

from nsb_config import options
from nsb_config import default_global_path
import nsb_twitter
import cotn_twitter
import nsb_discord


def main():


    if options['twitter_keys'] != None:
        twitter = nsb_twitter.twitter(options['twitter_keys'])
    else:
        twitter = None



    if options['action'] == 'init':
        print('copying', default_global_path, 'to', options['config'])
        if not options['dry-run']:
            shutil.copy(default_global_path, options['config'])

    elif options['action'] == 'update':
        cotn_twitter.update(twitter)

    elif options['action'] == 'discord':
        d = nsb_discord.DiscordBot(twitter)
        d.run(options['discord_token'])

    elif options['action'] == 'none':
        print("exiting")




if __name__ == '__main__':
    main()
