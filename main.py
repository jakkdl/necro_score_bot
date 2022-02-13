#!/usr/bin/env python3
import shutil

import nsb_config
import cotn_twitter
import nsb_discord


def main():
    options = nsb_config.options

    if options['action'] == 'update':
        cotn_twitter.update()

    elif options['action'] == 'discord':
        d = nsb_discord.DiscordBot()
        d.run(options['discord_token'])

    # elif options['action'] == 'postDaily':
    #    cotn_twitter.postYesterday(twitter)

    elif options['action'].lower() == 'printboard':
        cotn_twitter.print_board()

    elif options['action'] == 'none':
        print('exiting')


if __name__ == '__main__':
    main()
