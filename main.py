#!/usr/bin/python3.4
import os
import os.path
from pprint import pprint

import nsb_config
import nsb_twitter
import cotn_twitter


def main():
    nsb_config.options = nsb_config.read_options()
    options = nsb_config.options
    debug = options['debug']
    dry_run = options['dry-run']

    
    if options['tweet']:
        twitter = nsb_twitter.twitter(options['twitter_keys'])
    else:
        twitter = None

    if options['action'] == 'update':
        if not os.path.isdir(options['data']):
            print("Data directory doesn't exist, Creating" + path)
            os.mkdir(options['data'])
        cotn_twitter.update(twitter)



if __name__ == '__main__':
    main()
