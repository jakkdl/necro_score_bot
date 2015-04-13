import os
import os.path
from pprint import pprint

import nsb_config
import nsb_twitter
import cotn_twitter

def read_options():
    #Will exit here if --help is supplied
    cl_options = nsb_config.get_command_line_args()

    debug = 'debug' in cl_options
    if debug:
        pprint(sorted(cl_options.items()))
    
    global_path = nsb_config.default_global_path
    global_options = nsb_config.get_global_options(global_path)

    user_path = cl_options.get('config') or global_options['config']
    
    user_path = nsb_config.evaluate_path(user_path)
    
    #We tolerate missing file if 'config' is not supplied
    #at the command line
    user_options = nsb_config.get_user_options(user_path,
            'config' not in cl_options)
    
    options = global_options.copy()
    options.update(user_options)
    options.update(cl_options)

    if debug:
        pprint(sorted(options.items()))
    return options

def main():
    options = read_options()
    debug = options['debug']
    dry_run = options['dry-run']

    
    if options['twitter_keys'] != None:
        path = nsb_config.evaluate_path(options['twitter_keys'], True)
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
