import argparse
import configparser
import os
import sys
from pprint import pprint




########################## CONFIG FILE SETTINGS ###########################
 
# this isn't used directly by the module,
#   it just has to be located *somewhere*
default_global_path = 'necro_score_bot.conf'
 
# parameters to expect from global config file
#   additional entries in file are ignored
_expect_common_config = [('dry-run', bool),
                         ('data', str),
                         ('debug', bool),
                         ('steam_key', str),
                         ('twitter_keys', str),
                         ('json_urls', str)
                         ]

_expect_global_config = _expect_common_config + [('config', str)]
# allow missing entries/sections/file in global config file?
_tolerate_missing_global_entries = False
_tolerate_missing_global_file = False
 
 
_expect_user_config = _expect_common_config
 
_tolerate_missing_user_entries = True
 
####################### COMMAND-LINE ARGS SETTINGS ########################

def _bool(string):
    if string.lower() == 'true':
        return True
    elif string.lower() == 'false':
        return False
    msg = "%r is not a boolean" % string
    raise argparse.ArgumentTypeError(msg)

def _dir(string):
    string = os.path.expanduser(string)
    if not os.path.isdir(string):
        print('Creating directory', string)
        os.mkdir(string)
    return string
 
_parser = argparse.ArgumentParser()
 
# commands
_parser.add_argument('action',
                     help='action to perform',
                     choices=['init', 'postDaily', 'update', 'printBoard', 'none', 'updateJson', 'updateSRL'])
 
# flags
_parser.add_argument('--config', help='specify config path',
                     metavar='DIRECTORY')
 
_parser.add_argument('--data', help='specify data path',
                     metavar='DIRECTORY', type=_dir)

_parser.add_argument('--steam-key', help='specify file with steam keys',
                     metavar='FILE')

_parser.add_argument('--twitter-keys', help='Specify directory with twitter keys. Set to None to disable twitter.',
                     metavar='DIRECTORY')
# --dry-run requires dest, otherwise it
#   stores it as dry_run instead of dry-run
_parser.add_argument('--dry-run', help="Don't tweet, download or change any files",
                     action='store_true', default=False, dest='dry-run')
 
_parser.add_argument('--handle-new', help="Handle boards without history",
                     action='store_true', default=False, dest='handle-new')
 
_parser.add_argument('--debug', help='display debug messages',
                     action='store_true', default=False)
 
_parser.add_argument('--tweet', help='enable tweeting',
                     action='store_true', default=False)

_parser.add_argument('--backup', help='backup files to history after downloading',
                     metavar='bool', type=_bool)
###########################################################################
 

def get_command_line_args():
    args = _parser.parse_args().__dict__
    return {k: v for k, v in args.items()
            if v is not None}
 
 
def get_global_options(path):
    path = evaluate_path(path)
    return _get_config_args(path, _expect_global_config,
            _tolerate_missing_global_file,
            _tolerate_missing_global_entries)
 
 
def get_user_options(path, tolerate_missing_file):
    path = evaluate_path(path)
    return _get_config_args(path, _expect_user_config,
            tolerate_missing_file,
            _tolerate_missing_user_entries)
 
 
def merge_options(*args):
    """
    Merges option dicts.
    Later arguments have priority over earlier ones.
    Example: merge_options(global_conf, user_conf, cmnd_ln_args)
    """
    result = {}
   
    for new_values in args:
        for key, value in new_values.items():
            if value is None:
                continue
            result[key] = value
           
    return result
   
 
def evaluate_path(path, add_trailing_slash=False):
    """
    Evaluates user/environment variables and relative path.
    """
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.abspath(path)
    if add_trailing_slash:
        path += '/'
    return path
 
 
def _get_config_args(path, expected_entries, tolerate_missing_file, tolerate_missing_entries):
    result = {}
 
    parser = configparser.ConfigParser()
    parser.read(path)

    # more friendly error message in case file/section is missing
    if 'general' not in parser:
        message = 'section (or whole file) [general] missing from {}' \
                  ''.format(path)
        if tolerate_missing_file:
            print('NOTICE: ' + message)
            return {}
        else:
            raise Exception('ERROR: ' + message)
           
    # look up expected entries and convert as specified
    for entry, conversion_type in expected_entries:
        if conversion_type is bool:
            value = parser['general'].getboolean(entry)
        else:
            value = parser['general'].get(entry)
           
        if value is None:
            message = 'could not find entry "{}" in section [general] in ' \
                      'config file {}'.format(entry, path)
            if not tolerate_missing_entries:
                raise Exception('ERROR: ' + message)
        else:
            result[entry] = conversion_type(value)
 
    return result

def readFile(path):
    f = open(path)
    result = f.read()
    f.close()
    return result.rstrip()


def createDir(path, options):
    if not os.path.isdir(path):
        print(path, "doesn't exist, creating")
        if not options['dry-run']:
            os.mkdir(path)


def evaluate_paths(options):
    options['twitter_keys'] = evaluate_path(options['twitter_keys'], True)

    options['data'] = evaluate_path(options['data'], True)

    options['config'] = evaluate_path(options['config'], False)

    options['steam_key'] = readFile(evaluate_path(options['steam_key'], False))

    options['json_urls'] = options['json_urls'].split('\n')

    options['json_urls'].remove('')

    return options

def create_paths(options):
    createDir(options['data'], options)
    createDir(options['data'] + 'curr/', options)
    createDir(options['data'] + 'last/', options)

def read_options():
    #Will exit here if --help is supplied
    cl_options = get_command_line_args()

    debug = cl_options['debug']
    if debug:
        print("cl_options: ", end='')
        pprint(sorted(cl_options.items()))
    
    global_path = default_global_path
    global_options = get_global_options(global_path)

    user_path = cl_options.get('config') or global_options['config']
    
    user_path = evaluate_path(user_path)
    
    #We tolerate missing file if 'config' is not supplied
    #at the command line
    user_options = get_user_options(user_path,
            'config' not in cl_options)
    
    options = global_options.copy()
    options.update(user_options)
    options.update(cl_options)

    
    options = evaluate_paths(options)
    create_paths(options)

    if debug:
        print("all_options: ", end='')
        pprint(sorted(options.items()))

    return options




options = read_options()
