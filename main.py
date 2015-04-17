#!/usr/bin/python3.4
import os
import os.path
from pprint import pprint

from nsb_config import options
import nsb_twitter
import cotn_twitter


def main():
    pprint(options)
    debug = options['debug']
    dry_run = options['dry-run']

    
    if options['twitter_keys'] != None:
        twitter = nsb_twitter.twitter(path)
    else:
        twitter = None

    if options['action'] == 'update':
        path = nsb_config.evaluate_path(options['data'], True)
        if not os.path.isdir(path):
            print("Data directory doesn't exist, Creating" + path)
            os.mkdir(path)
        if debug:
            print(path)
        cotn_twitter.update(twitter, path, options['dry-run'], options['tweet'], debug)



if __name__ == '__main__':
    main()
