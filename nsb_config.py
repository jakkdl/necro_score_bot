import argparse
import collections
import configparser
import abc
import os
from typing import Optional


def evaluate_path(path):
    '''
    Evaluates user/environment variables and relative path.
    '''
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.abspath(path)
    return path


# inspired by https://bitbucket.org/htv2013/argparse_actions/src
class _MyAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, collections.abc.Iterable):
            folders = list(map(self.parse_value, values))
        else:
            folders = self.parse_value(values)
        setattr(namespace, self.dest, folders)

    @staticmethod
    @abc.abstractmethod
    def parse_value(value):
        pass


class _File(_MyAction):
    @staticmethod
    def parse_value(value):
        string = evaluate_path(value)
        if not os.path.isfile(string):
            print(f"Warning: invalid file {string}")
        return string


class _Bool(_MyAction):
    @staticmethod
    def parse_value(value):
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        raise argparse.ArgumentTypeError(f'{value} is not a boolean')


class _Read_File(_MyAction):
    @staticmethod
    def parse_value(value):
        with open(evaluate_path(value), encoding='utf8') as file:
            return file.read().rstrip()


class _Directory(_MyAction):
    @staticmethod
    def parse_value(value):
        string = evaluate_path(value)
        if not os.path.isdir(string):
            raise argparse.ArgumentTypeError(f'{string} is not a directory')
        return string


class _Create_Directory(_MyAction):
    @staticmethod
    def parse_value(value):
        string = evaluate_path(value)
        if not os.path.isdir(string):
            print(f'Creating directory: {string}')
            os.mkdir(string)
        return string


class Options(argparse.ArgumentParser):
    def __init__(self):
        super().__init__()
        self._configparser = configparser.ConfigParser()
        self._config_values = {}
        self._options = {}

    def __getitem__(self, key):
        return self._options[key]

    def add_parameter(  # pylint: disable=arguments-differ
        self,
        argument: str,
        config=False,
        command_line=False,
        **kwargs,
    ):
        action = kwargs.get('action')
        if not config and not command_line:
            config = command_line = True
        if config:
            if not action:
                action = kwargs['type']
            self._config_values[argument] = action
        if command_line:
            super().add_argument(f"--{argument}", **kwargs)

    def add_action(self, *args, **kwargs):
        super().add_argument(*args, **kwargs)

    def read_config(self, path):
        parser = configparser.ConfigParser()
        parser.read(path)
        print('hi')

        # more friendly error message in case file/section is missing
        if 'general' not in parser:
            print(f'Warning: section [general] missing from {path}')

        # look up expected entries and convert as specified
        for name, action in self._config_values.items():
            value = parser['general'].get(name)

            if value is not None:
                #TODO: Broken
                self._options[name] = action(value)

    def parse_args(self, args=None, namespace=None):
        # Will exit here if --help is supplied
        args = super().parse_args(args, namespace).__dict__
        cl_options = {k: v for k, v in args.items() if v is not None}

        print(cl_options['config'])
        if os.path.isfile(cl_options['config']):
            self.read_config(cl_options['config'])

        self._options.update(cl_options)

print('whoop')
options = Options()


####################### COMMAND-LINE ARGS SETTINGS ########################


# commands
options.add_action(
    'action',
    help='action to perform',
    choices=['init', 'update', 'postDaily', 'discord', 'printBoard', 'none'],
)
# flags
options.add_parameter(
    'config', help='specify config path', metavar='DIRECTORY', action=_File,
    command_line=True, default= evaluate_path(
        os.path.join('$XDG_CONFIG_HOME', 'necro_score_bot', 'necro_score_bot.conf')
    )
)

options.add_parameter(
    'data', help='specify data path', metavar='DIRECTORY', action=_Create_Directory
)

options.add_parameter(
    'steam-key', help='specify file with steam keys', metavar='FILE', action=_Read_File
)

options.add_parameter(
    'discord_token',
    help='specify file with discord token',
    metavar='FILE',
    action=_File,
)

options.add_parameter('board', help='board to update/print', metavar='BOARD',
        type=str)

options.add_parameter(
    'twitter-keys',
    help='Specify directory with twitter keys. ' 'Set to None to disable twitter.',
    metavar='DIRECTORY',
    action=_Directory,
)

# --dry-run requires dest, otherwise it
#   stores it as dry_run instead of dry-run
options.add_parameter(
    'dry-run',
    help="Don't tweet, download or change any files",
    action='store_true', config=False,
    default=False,
    dest='dry-run',
)

options.add_parameter(
    'handle-new',
    help='Handle boards without history',
    action='store_true',
    default=False,
    dest='handle-new',
)

options.add_parameter(
    'debug',
    help='display debug messages, prints tweets to stdout',
    action='store_true', config=False,
    default=False,
)

options.add_parameter(
    'tweet', help='enable tweeting', action='store_true', default=False, config=False
)

options.add_parameter(
    'backup',
    help='backup files to history after downloading',
    metavar='bool',
    action=_Bool,
    default=True,
)

options.add_parameter(
    'churn',
    help='churn through changes quickly, not composing or posting any messages',
    action='store_true', config=False,
    default=False,
)

options.add_parameter(
    'necrolab',
    help='use necrolab api to get linked accounts',
    metavar='bool',
    action=_Bool,
    default=False,
)

options.parse_args()
