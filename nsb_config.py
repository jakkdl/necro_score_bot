import argparse
import configparser
from pprint import pprint
import os


########################## CONFIG FILE SETTINGS ###########################

# this isn't used directly by the module,
#   it just has to be located *somewhere*
default_global_path = os.path.join(os.path.dirname(__file__), 'necro_score_bot.conf')

# parameters to expect from global config file
#   additional entries in file are ignored
_expect_common_config = [
    ('dry-run', bool),
    ('data', str),
    ('debug', bool),
    ('steam_key', str),
    ('discord_token', str),
    ('twitter_keys', str),
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
    if string.lower() == 'false':
        return False
    msg = f'{string} is not a boolean'
    raise argparse.ArgumentTypeError(msg)


def evaluate_path(path, add_trailing_slash=False):
    '''
    Evaluates user/environment variables and relative path.
    '''
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.abspath(path)
    if add_trailing_slash:
        path += '/'
    return path

def _dir(string):
    string = evaluate_path(string)
    if not os.path.isdir(string):
        print(f'Creating directory: {string}')
        os.mkdir(string)
    return string

def _file(filename):
    with open(evaluate_path(filename), encoding='utf8') as file:
        return file.read().rstrip()

_parser = argparse.ArgumentParser()

# commands
_parser.add_argument('action',
                     help='action to perform',
                     choices=['init',
                         'update',
                         'postDaily',
                         'discord',
                         'printBoard',
                         'none'])
# flags
_parser.add_argument('--config', help='specify config path', metavar='DIRECTORY')

_parser.add_argument('--data', help='specify data path', metavar='DIRECTORY', type=_dir)

_parser.add_argument('--steam-key', help='specify file with steam keys', metavar='FILE',
        type=_file)

_parser.add_argument('--discord_token',
        help='specify file with discord token',
                     metavar='FILE')

_parser.add_argument('--board', help='board to update/print', metavar='BOARD',
        type=str)

_parser.add_argument(
    '--twitter-keys',
    help='Specify directory with twitter keys. ' 'Set to None to disable twitter.',
    metavar='DIRECTORY',
)
# --dry-run requires dest, otherwise it
#   stores it as dry_run instead of dry-run
_parser.add_argument(
    '--dry-run',
    help="Don't tweet, download or change any files",
    action='store_true',
    default=False,
    dest='dry-run',
)

_parser.add_argument(
    '--handle-new',
    help='Handle boards without history',
    action='store_true',
    default=False,
    dest='handle-new',
)

_parser.add_argument(
    '--debug',
    help='display debug messages,' 'prints tweets to stdout',
    action='store_true',
    default=False,
)

_parser.add_argument(
    '--tweet', help='enable tweeting', action='store_true', default=False
)

_parser.add_argument(
    '--backup',
    help='backup files to history after downloading',
    metavar='bool',
    type=_bool,
    default=True,
)

_parser.add_argument(
    '--churn',
    help='churn through changes quickly, not composing or posting any messages',
    action='store_true',
    default=False,
)

_parser.add_argument(
    '--necrolab',
    help='use necrolab api to get linked accounts',
    metavar='bool',
    type=_bool,
    default=False,
)

###########################################################################


def get_command_line_args():
    args = _parser.parse_args().__dict__
    return {k: v for k, v in args.items() if v is not None}


def get_global_options(path):
    path = evaluate_path(path)
    return _get_config_args(
        path,
        _expect_global_config,
        _tolerate_missing_global_file,
        _tolerate_missing_global_entries,
    )


def get_user_options(path, tolerate_missing_file):
    path = evaluate_path(path)
    return _get_config_args(
        path, _expect_user_config, tolerate_missing_file, _tolerate_missing_user_entries
    )




def _get_config_args(
    path, expected_entries, tolerate_missing_file, tolerate_missing_entries
):
    result = {}

    parser = configparser.ConfigParser()
    parser.read(path)

    # more friendly error message in case file/section is missing
    if 'general' not in parser:
        message = f'section (or whole file) [general] missing from {path}'
        if tolerate_missing_file:
            print('NOTICE: ' + message)
            return {}
        raise Exception('ERROR: ' + message)

    # look up expected entries and convert as specified
    for entry, conversion_type in expected_entries:
        if conversion_type is bool:
            value = parser['general'].getboolean(entry)
        else:
            value = parser['general'].get(entry)

        if value is None:
            message = (
                f'could not find entry {entry} in section [general] in '
                f'config file {path}'
            )
            if not tolerate_missing_entries:
                raise Exception('ERROR: ' + message)
        else:
            result[entry] = conversion_type(value)

    return result



def read_options():
    # Will exit here if --help is supplied
    cl_options = get_command_line_args()

    debug = cl_options['debug']
    if debug:
        print('cl_options: ', end='')
        pprint(sorted(cl_options.items()))

    global_path = default_global_path
    global_options = get_global_options(global_path)

    user_path = cl_options.get('config') or global_options['config']

    user_path = evaluate_path(user_path)

    # We tolerate missing file if 'config' is not supplied
    # at the command line
    user_options = get_user_options(user_path, 'config' not in cl_options)

    _options = global_options.copy()
    _options.update(user_options)
    _options.update(cl_options)

    #_options = evaluate_paths(_options)
    #create_paths(_options)

    if debug:
        print('all_options: ', end='')
        pprint(sorted(_options.items()))

    return _options


options = read_options()
