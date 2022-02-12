# Necro Score Bot
Bot that posts tweets on leaderboard updates in crypt of the necrodancer.  
Is currently running at [twitter.com/necro_score_bot](https://twitter.com/necro_score_bot) with >200 followers

## Functionality
* Discord support finished, but not in use.  
* add a link to your twitter in your steam profile to get tagged in tweets, [like so](https://steamcommunity.com/profiles/76561198074553183)
* * this will also make the bot post your score updates that do not hit the treshold for significance, but only as a "reply" to you.
* uses [crypt.toofz.com](https://crypt.toofz.com/leaderboards) by [@Leonard_Thieu](https://github.com/leonard-thieu/toofz-necrodancer) as backend now, instead of Steams old API - which was quite unreliable
* adheres to official python coding standards with minimal exceptions
* default configuration is in file [necro_score_bot.conf](https://github.com/jakkdl/necro_score_bot/blob/master/necro_score_bot.conf) but is superseded by any configuration in `$XDG_CONFIG_DIR/necro_score_bot.conf`
* configuration file can be overridden with use of command-line flags
* the Discord branch has thread support, but that is currently not merged into main

### Deprecated functionality
* Supports [NecroLab power rankings](https://www.necrolab.com/) by [@Tommy Bolger](https://github.com/tommy-bolger), but the website is WIP and unreliable so functionality is disabled.
* Had support for [SpeedRunsLive race rankings](https://www.speedrunslive.com/races/game/necrodancer), but that is not in use so no longer maintaned and was never activated.

### Planned functionality
* [Synchrony](https://necro.marukyu.de/)


## Usage
```
usage: main.py [-h] [--config DIRECTORY] [--data DIRECTORY] [--steam-key FILE]
               [--twitter-keys DIRECTORY] [--dry-run] [--handle-new] [--debug] [--tweet]
               [--backup bool] [--churn]
               {init,postDaily,update,printBoard,none}

positional arguments:
  {init,postDaily,update,printBoard,none}
                        action to perform

options:
  -h, --help            show this help message and exit
  --config DIRECTORY    specify config path
  --data DIRECTORY      specify data path
  --steam-key FILE      specify file with steam keys
  --twitter-keys DIRECTORY
                        Specify directory with twitter keys. Set to None to disable twitter.
  --dry-run             Don't tweet, download or change any files
  --handle-new          Handle boards without history
  --debug               display debug messages
  --tweet               enable tweeting
  --backup bool         backup files to history after downloading
  --churn               churn through changes quickly, not composing or posting any messages
```


## Credits
* written by [@jakkdl](https://github.com/jakkdl)  
* maintained by [@AlexisYj](https://github.com/alexismartin)
* with several pull requests and feedback from the wonderful community ❤️
