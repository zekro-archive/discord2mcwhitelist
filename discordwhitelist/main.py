import logging
import argparse
from rcon import RCON
from database import SQLite
from discord.ext import commands
from discord.ext.commands import Context


# TODO:
#  - add remove and list command
#  - make rcon requests asyncronous and
#    out-timable that they dont block
#    the bot loop if they stuck
#  - remove people from white list when
#    they quit the server

def parse_args():
    """
    Initializes command line arguments and
    parses them on startup returning the parsed
    args namespace.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--token', '-t', required=True, type=str,
        help='The discord bot token')
    parser.add_argument(
        '--prefix', '-p', default='>', type=str,
        help='The command prefix of the bot (def: \'>\')')
    parser.add_argument(
        '--log-level', '-l', default=20, type=int,
        help='Set log level of the default logger (def: 20)')
    return parser.parse_args()


def main():
    args = parse_args()

    logging.basicConfig(
        level=args.log_level,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    rcon = RCON('localhost', '123')
    rcon.connect()

    db = SQLite('database.db')

    bot = commands.Bot(command_prefix=args.prefix)

    ##########
    # EVENTS #
    ##########

    @bot.event
    async def on_ready():
        logging.info(
            'Ready (logged in as {}#{} [{}])'.format(
                bot.user.name, bot.user.discriminator, bot.user.id))

    ############
    # COMMANDS #
    ############

    @bot.command(
        brief='Add to whitelist',
        description='Register a minecraft ID to your discord profile ' +
                    'and add it to the minecraft servers whitelist.',
        aliases=('add', 'set'))
    async def bind(ctx: Context, *args):
        if len(args) == 0:
            return

        mc_id: str = args[0].lower()

        dc_id, curr_mc_id = db.get_whitelist_by_mc_id(mc_id)

        if curr_mc_id is not None and mc_id == curr_mc_id:
            await ctx.send(':warning:  This minecraft ID is already ' +
                           'bound to your account!')
            return

        if dc_id is not None and dc_id != str(ctx.message.author.id):
            await ctx.send(':warning:  This minecraft ID is already ' +
                           'registered by another user!')
            return

        old_mc_id = db.set_witelist(str(ctx.message.author.id), mc_id)

        if old_mc_id is not None:
            rcon.command('whitelist remove {}'.format(old_mc_id))
        rcon.command('whitelist add {}'.format(mc_id))

        await ctx.send(
            ':white_check_mark:  You are now bound to the mc ' +
            'account `{}` and added to the servers whitelist.'.format(mc_id))

    ###########
    # RUN BOT #
    ###########

    bot.run(args.token)


if __name__ == '__main__':
    main()
