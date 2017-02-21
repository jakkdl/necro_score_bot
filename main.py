#!/usr/bin/python3
import os
import os.path
import shutil
from pprint import pprint

from nsb_config import options
from nsb_config import default_global_path
import nsb_twitter
import cotn_twitter


def main():
    debug = options['debug']
    dry_run = options['dry-run']

    
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
    
    elif options['action'] == 'postDaily':
        cotn_twitter.postYesterday(twitter)

    elif options['action'] == 'printBoard':
        cotn_twitter.printBoard()

    elif options['action'] == 'updateJson':
        cotn_twitter.updateJson(twitter)
    
    elif options['action'] == 'updateSRL':
        cotn_twitter.updateSRL(twitter)
    
    elif options['action'] == 'none':
        print("exiting")




if __name__ == '__main__':
    main()
