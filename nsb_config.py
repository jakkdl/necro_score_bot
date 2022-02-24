import argparse
import collections
import configparser
import abc
import os
import logging
from typing import Callable, Any, Optional, Sequence

logger = logging.getLogger("necro_score_bot")

_DEFAULT_XDG = {
    "$XDG_CONFIG_HOME": "$HOME/.config",
    "$XDG_DATA_HOME": "$HOME/.local/share",
}


def evaluate_path(path: str) -> str:
    """
    Evaluates user/environment variables and relative path.
    """
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    unresolved_xdg = False
    for key, val in _DEFAULT_XDG.items():
        if key in path:
            path.replace(key, val)
            unresolved_xdg = True
    if unresolved_xdg:
        path = os.path.expandvars(path)
    path = os.path.abspath(path)
    return path


# inspired by https://bitbucket.org/htv2013/argparse_actions/src
class _MyAction(argparse.Action):
    def __call__(
        self,
        parser: Any,
        namespace: argparse.Namespace,
        values: Any,
        option_string: Any = None,
    ) -> None:
        if isinstance(values, collections.abc.Iterable) and not isinstance(values, str):
            folders = list(map(self.parse_value, values))
        else:
            folders = self.parse_value(values)
        setattr(namespace, self.dest, folders)

    @staticmethod
    @abc.abstractmethod
    def parse_value(value: str) -> Any:
        pass


class _File(_MyAction):
    @staticmethod
    def parse_value(value: str) -> Any:
        string = evaluate_path(value)
        if not os.path.isfile(string):
            logger.warning("invalid file %s", string)
        return string


class _Bool(_MyAction):
    @staticmethod
    def parse_value(value: str) -> Any:
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        raise argparse.ArgumentTypeError(f"{value} is not a boolean")


class _Directory(_MyAction):
    @staticmethod
    def parse_value(value: str) -> Any:
        string = evaluate_path(value)
        if not os.path.isdir(string):
            raise argparse.ArgumentTypeError(f"{string} is not a directory")
        return string


class _CreateDirectory(_MyAction):
    @staticmethod
    def parse_value(value: str) -> Any:
        string = evaluate_path(value)
        if not os.path.isdir(string):
            logger.info("Creating directory: %s", string)
            os.mkdir(string)
        return string


class _SetLogLevel(_MyAction):
    @staticmethod
    def parse_value(value: str) -> Any:
        logger.setLevel(value.upper())
        return value


def parse_file(value: str) -> str:
    with open(evaluate_path(value), encoding="utf8") as file:
        return file.read().rstrip()


class Options(argparse.ArgumentParser):
    def __init__(self) -> None:
        super().__init__(add_help=False)
        self._options = argparse.Namespace()
        self._post_process: dict[str, Callable[[str], str]] = {}

    def __getitem__(self, key: str) -> Any:
        return getattr(self._options, key)

    def parse_config(self) -> argparse.Namespace:
        path = getattr(self._options, "config")
        config_args = []

        # print('config not a file')
        if os.path.isfile(path):
            parser = configparser.ConfigParser()
            parser.read(path)

            # more friendly error message in case file/section is missing
            if "general" not in parser:
                logger.warning("section [general] missing from %s", path)

            # look up expected entries and convert as specified
            for name, value in parser["general"].items():
                config_args.append(f"--{name.replace('_', '-')}={value}")

        super().parse_known_args(args=config_args, namespace=self._options)
        return self._options

    def parse_known_args(
        self,
        args: Optional[Sequence[str]] = None,
        namespace: Optional[argparse.Namespace] = None,
    ) -> tuple[argparse.Namespace, list[str]]:
        if namespace is None:
            namespace = self._options
        return super().parse_known_args(args, namespace)

    def generate_default_config(self) -> None:
        # import ipdb; ipdb.set_trace()
        super().parse_known_args(args=[], namespace=self._options)
        config_values = self._options.__dict__.copy()

        path = config_values.pop("config")
        config_values.pop("generate_config")
        values = {key: str(val) for key, val in config_values.items()}

        parser = configparser.ConfigParser(defaults=values, default_section="general")

        with open(path, "w", encoding="utf-8") as file:
            parser.write(file)

    def add_post_process(self, key: str, func: Callable[[str], str]) -> None:
        self._post_process[key] = func

    def post_process(self) -> None:
        for key, func in self._post_process.items():
            assert key in self._options
            setattr(self._options, key, func(getattr(self._options, key)))


options = Options()

options.add_argument(
    "--config",
    help="specify config path",
    metavar="DIRECTORY",
    action=_File,
    default=evaluate_path(
        os.path.join("$XDG_CONFIG_HOME", "necro_score_bot", "necro_score_bot.conf")
    ),
)

options.add_argument(
    "--generate-config",
    help="generate default config",
    action="store_true",
    default=False,
)

options.parse_known_args()


####################### COMMAND-LINE ARGS SETTINGS ########################

# commands
# flags


options.add_argument(
    "--data-dir",
    help="specify data directory",
    dest="data",
    metavar="DIRECTORY",
    action=_CreateDirectory,
    default=evaluate_path("$XDG_DATA_HOME/necro_score_bot/"),
)

options.add_argument(
    "--log-level",
    help="set log level",
    action=_SetLogLevel,
    choices=["info", "debug", "warning", "error", "critical"],
)

options.add_argument(
    "--steam-key",
    help="specify file with steam keys",
    metavar="FILE",
    action=_File,
    default=evaluate_path("$XDG_CONFIG_HOME/necro_score_bot/steam_key"),
)
options.add_post_process("steam_key", parse_file)

options.add_argument(
    "--discord_token",
    help="specify file with discord token",
    metavar="FILE",
    action=_File,
    default=evaluate_path("$XDG_CONFIG_HOME/necro_score_bot/discord_token"),
)
options.add_post_process("discord_token", parse_file)

options.add_argument(
    "--twitter-keys",
    help="Specify directory with twitter keys. Set to None to disable twitter.",
    metavar="DIRECTORY",
    action=_Directory,
    default=evaluate_path("$XDG_CONFIG_HOME/necro_score_bot/twitter/"),
)


options.add_argument(
    "--handle-new",
    help="Handle boards without history",
    action=_Bool,
    default=False,
)

options.add_argument("--tweet", help="enable tweeting", action=_Bool, default=False)
options.add_argument(
    "--threaded", help="multi-threaded updating", action=_Bool, default=False
)
options.add_argument(
    "--post-discord", help="enable posting to discord", action=_Bool, default=False
)

options.add_argument(
    "--backup",
    help="backup files to history after downloading",
    metavar="bool",
    action=_Bool,
    default=True,
)

options.add_argument(
    "--necrolab",
    help="use necrolab api to get linked accounts",
    metavar="bool",
    action=_Bool,
    default=False,
)

options.add_argument(
    "--private-report-rank-diff",
    help="highest rank to report rank increase, if registered",
    metavar="num",
    type=int,
    default=100,
)

options.add_argument(
    "--private-report-points-diff",
    help="highest rank to report points increase, if registered",
    metavar="num",
    type=int,
    default=100,
)

options.add_argument(
    "--public-report-rank-diff",
    help="highest rank to report rank increase",
    metavar="num",
    type=int,
    default=5,
)

options.add_argument(
    "--public-report-points-diff",
    help="highest rank to report points increase",
    metavar="num",
    type=int,
    default=3,
)

options.add_argument(
    "--impossible-score",
    help="score above which it will be reported as bugged",
    metavar="num",
    type=int,
    default=1000000,
)

options.add_argument(
    "--deathless-message-new-entry",
    type=str,
    default="$NAME$ claims rank $RANK$ in $BOARD$ with $PROGRESS$ $TOOFZURL$",
)
options.add_argument(
    "--deathless-message-new-rank",
    type=str,
    default="$NAME$ claims rank $RANK$ (+$DELTARANK$) in $BOARD$ with $PROGRESS$ ($DELTAPROGRESS$) $TOOFZURL$",
)
options.add_argument(
    "--deathless-message-same-rank",
    type=str,
    default="$NAME$, $RANKTH$ in $BOARD$ improves streak to $PROGRESS$ ($DELTAPROGRESS$) $TOOFZURL$",
)
options.add_argument(
    "--speedrun-message-new-entry",
    type=str,
    default="$NAME$ claims rank $RANK$ in $BOARD$ with $TIME$ $TOOFZURL$",
)
options.add_argument(
    "--speedrun-message-new-rank",
    type=str,
    default="$NAME$ claims rank $RANK$ (+$DELTARANK$) in $BOARD$ with $TIME$ ($DELTATIME$) $TOOFZURL$",
)
options.add_argument(
    "--speedrun-message-same-rank",
    type=str,
    default="$NAME$, $RANKTH$ in $BOARD$ improves time to $TIME$ ($DELTATIME$) $TOOFZURL$",
)
options.add_argument(
    "--score-message-new-entry",
    type=str,
    default="$NAME$ claims rank $RANK$ in $BOARD$ with $SCORE$ gold $TOOFZURL$",
)
options.add_argument(
    "--score-message-new-rank",
    type=str,
    default="$NAME$ claims rank $RANK$ (+$DELTARANK$) in $BOARD$ with $SCORE$ ($DELTASCORE$) gold $TOOFZURL$",
)
options.add_argument(
    "--score-message-same-rank",
    type=str,
    default="$NAME$, $RANKTH$ in $BOARD$ improves to $SCORE$ ($DELTASCORE$) gold $TOOFZURL$",
)


if options["generate_config"]:
    options.generate_default_config()
else:
    options.parse_config()

## command-line only actions
options.add_argument(
    "action",
    help="action to perform",
    choices=["update", "postDaily", "discord", "printBoard", "none"],
)

options.add_argument(
    "--churn",
    help="churn through changes quickly, not composing or posting any messages",
    action="store_true",
    default=False,
)

options.add_argument(
    "--dry-run",
    help="Don't tweet, download or change any files",
    action="store_true",
    default=False,
)

options.add_argument("--board", help="board to update/print", metavar="BOARD", type=str)

options.add_argument(
    "-h",
    "--help",
    action="help",
    default=argparse.SUPPRESS,
    help="show this help message and exit",
)

options.parse_args()
options.post_process()
