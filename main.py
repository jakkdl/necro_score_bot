#!/usr/bin/python3
import shutil

from nsb_config import options
from nsb_config import default_global_path
import nsb_twitter
import cotn_twitter


def main():
    # debug = options['debug']

    if options['twitter_keys']:
        twitter = nsb_twitter.twitter(options['twitter_keys'])
        if not twitter.agent:
            twitter = None
    else:
        twitter = None

    if options['action'] == 'init':
        print(f"copying {default_global_path} to {options['config']}")
        if not options['dry-run']:
            shutil.copy(default_global_path, options['config'])

    elif options['action'] == 'update':
        cotn_twitter.update(twitter)

    elif options['action'] == 'postDaily':
        cotn_twitter.postYesterday(twitter)

    # elif options['action'] == 'printBoard':
    #    cotn_twitter.printBoard()

    elif options['action'] == 'none':
        print('exiting')


if __name__ == '__main__':
    main()
