import argparse
import collections
import configparser
import abc
import os


def evaluate_path(path):
    """
    Evaluates user/environment variables and relative path.
    """
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.abspath(path)
    return path


# inspired by https://bitbucket.org/htv2013/argparse_actions/src
class _MyAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, collections.abc.Iterable) and not isinstance(values, str):
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
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        raise argparse.ArgumentTypeError(f"{value} is not a boolean")


class _ReadFile(_MyAction):
    @staticmethod
    def parse_value(value):
        with open(evaluate_path(value), encoding="utf8") as file:
            return file.read().rstrip()


class _Directory(_MyAction):
    @staticmethod
    def parse_value(value):
        string = evaluate_path(value)
        if not os.path.isdir(string):
            raise argparse.ArgumentTypeError(f"{string} is not a directory")
        return string


class _CreateDirectory(_MyAction):
    @staticmethod
    def parse_value(value):
        string = evaluate_path(value)
        if not os.path.isdir(string):
            print(f"Creating directory: {string}")
            os.mkdir(string)
        return string


class Options(argparse.ArgumentParser):
    def __init__(self):
        super().__init__()
        self._configparser = configparser.ConfigParser()
        self._config_values = None
        self._options = argparse.Namespace()

    def __getitem__(self, key):
        return getattr(self._options, key)

    def add_parameter(
        self,
        argument: str,
        **kwargs,
    ):
        # argument = argument.replace('-', '_')
        super().add_argument(argument, **kwargs)

    def parse_config(self) -> argparse.Namespace:
        path = getattr(self._options, "config")
        config_args = []

        # print('config not a file')
        if os.path.isfile(path):
            parser = configparser.ConfigParser()
            parser.read(path)

            # more friendly error message in case file/section is missing
            if "general" not in parser:
                print(f"Warning: section [general] missing from {path}")

            # look up expected entries and convert as specified
            for name, value in parser["general"].items():
                config_args.append(f"--{name.replace('_', '-')}={value}")

        super().parse_known_args(args=config_args, namespace=self._options)
        self._config_values = self._options.__dict__.copy()
        return self._options

    def parse(self):
        # Will exit here if --help is supplied
        super().parse_args(namespace=self._options)

        # cl_options = {k: v for k, v in self._options.items() if v is not None}

        return self._options

    def parse_known_args(self, args=None, namespace=None):
        if namespace is None:
            namespace = self._options
        return super().parse_known_args(args, namespace)

    def generate_default_config(self):
        path = self._config_values.pop("config")
        values = {key: str(val) for key, val in self._config_values.items()}

        parser = configparser.ConfigParser(defaults=values, default_section="general")

        with open(path, "w", encoding="utf-8") as file:
            parser.write(file)


options = Options()

options.add_parameter(
    "--config",
    help="specify config path",
    metavar="DIRECTORY",
    action=_File,
    default=evaluate_path(
        os.path.join("$XDG_CONFIG_HOME", "necro_score_bot", "necro_score_bot.conf")
    ),
)

options.parse_known_args()


####################### COMMAND-LINE ARGS SETTINGS ########################

# commands
# flags


options.add_parameter(
    "--data-dir",
    help="specify data directory",
    metavar="DIRECTORY",
    action=_CreateDirectory,
    default=evaluate_path("$XDG_DATA_HOME/necro_score_bot/"),
)

options.add_parameter(
    "--steam-key",
    help="specify file with steam keys",
    metavar="FILE",
    action=_ReadFile,
    default=evaluate_path("$XDG_CONFIG_HOME/necro_score_bot/steam_key"),
)

options.add_parameter(
    "--discord_token",
    help="specify file with discord token",
    metavar="FILE",
    action=_File,
    default=evaluate_path("$XDG_CONFIG_HOME/necro_score_bot/discord_token"),
)

options.add_parameter(
    "--twitter-keys",
    help="Specify directory with twitter keys. Set to None to disable twitter.",
    metavar="DIRECTORY",
    action=_Directory,
    default=evaluate_path("$XDG_CONFIG_HOME/necro_score_bot/twitter/"),
)


options.add_parameter(
    "--handle-new",
    help="Handle boards without history",
    action=_Bool,
    default=False,
)

options.add_parameter("--tweet", help="enable tweeting", action=_Bool, default=False)

options.add_parameter(
    "--backup",
    help="backup files to history after downloading",
    metavar="bool",
    action=_Bool,
    default=True,
)

options.add_parameter(
    "--necrolab",
    help="use necrolab api to get linked accounts",
    metavar="bool",
    action=_Bool,
    default=False,
)

options.parse_config()


## command-line only actions
options.add_parameter(
    "action",
    help="action to perform",
    choices=["update", "postDaily", "discord", "printBoard", "none"],
)

options.add_parameter(
    "--generate-config",
    help="generate default config",
    action="store_true",
    default=False,
)

options.add_parameter(
    "--churn",
    help="churn through changes quickly, not composing or posting any messages",
    action="store_true",
    default=False,
)

options.add_parameter(
    "--debug",
    help="display debug messages, prints tweets to stdout",
    action="store_true",
    default=False,
)

options.add_parameter(
    "--dry-run",
    help="Don't tweet, download or change any files",
    action="store_true",
    default=False,
)

options.add_parameter(
    "--board", help="board to update/print", metavar="BOARD", type=str
)

options.parse()

if options["generate_config"]:
    options.generate_default_config()
