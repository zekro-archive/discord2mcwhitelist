import logging
import argparse
from rcon import RCON
from database import SQLite
from discord import Member, Embed, Message
from discord.ext import commands
from discord.ext.commands import Context


EMBED_COLOR = 0xf90261


def parse_args():
    """
    Initializes command line arguments and
    parses them on startup returning the parsed
    args namespace.
    """
    parser = argparse.ArgumentParser()

    bot = parser.add_argument_group('Discord Bot')
    bot.add_argument(
        '--token', '-t', required=True, type=str,
        help='The discord bot token')
    bot.add_argument(
        '--prefix', '-p', default='>', type=str,
        help='The command prefix of the bot (def: \'>\')')

    rcon = parser.add_argument_group('RCON Connection')
    rcon.add_argument(
        '--rcon-address', '-raddr', default='localhost:25575', type=str,
        help='The address of the RCON server (def: \'localhost:25575\')')
    rcon.add_argument(
        '--rcon-password', '-rpw', required=True, type=str,
        help='The password of the RCON server')

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

    rcon = RCON(args.rcon_address, args.rcon_password)
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

    @bot.event
    async def on_message(msg: Message):
        if bot.user in msg.mentions:
            em = Embed()
            em.color = EMBED_COLOR
            em.title = 'discord2mcwhitelist'
            em.description = ('Hey, I am a bot which can connect your ' +
                              'Discord Account with your Minecraft User ' +
                              'ID and add you to the Guilds Minecraft ' +
                              'Server Whitelist!\n\n' +
                              'Just enter `{}help` in the chat for more ' +
                              'information on how to use ' +
                              'me.').format(args.prefix)
            em.add_field(
                name='GitHub',
                value='https://github.com/zekroTJA/discord2mcwhitelist')
            em.set_footer(
                text='© 2020 zekro.de')
            await msg.channel.send(embed=em)
        await bot.process_commands(msg)

    @bot.event
    async def on_member_remove(member: Member):
        _, mc_id = db.get_whitelist_by_discord_id(str(member.id))
        if mc_id is not None:
            rcon.command('whitelist remove {}'.format(mc_id))
            db.rem_witelist(str(member.id))

    ############
    # COMMANDS #
    ############

    # bind

    @bot.command(
        brief='Add to whitelist',
        description='Register a minecraft ID to your discord profile ' +
                    'and add it to the minecraft servers whitelist.',
        aliases=('add', 'set'))
    async def bind(ctx: Context, mc_id: str):
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

    @bind.error
    async def bind_error(ctx: Context, err):
        if isinstance(err, commands.MissingRequiredArgument):
            await ctx.send_help()

    # unbind

    @bot.command(
        brief='Remove from whitelist',
        description='Unregisters a bound minecraft ID from your account ' +
                    'and removes you from the whitelist of the server.',
        aliases=('remove', 'unset'))
    async def unbind(ctx: Context):
        _, mc_id = db.get_whitelist_by_discord_id(str(ctx.message.author.id))
        if mc_id is None:
            await ctx.send(':warning:  Ypur account is not bound to any ' +
                           'minecraft ID.')
            return

        rcon.command('whitelist remove {}'.format(mc_id))
        db.rem_witelist(str(ctx.message.author.id))

        await ctx.send(
            ':white_check_mark:  Successfully removed you from ' +
            'the servers whitelist and account is unbound.'.format(mc_id))

    # info

    @bot.command(
        brief='Displays current binding',
        description='Displays the currently bound minecraft ID.',
        aliases=('bound', 'display'))
    async def info(ctx: Context):
        _, mc_id = db.get_whitelist_by_discord_id(str(ctx.message.author.id))
        if mc_id is None:
            await ctx.send(':warning:  Ypur account is not bound to any ' +
                           'minecraft ID.')
            return

        await ctx.send(
            ':information_source:  Your account is currently bound to the ' +
            'minecraft ID `{}`.'.format(mc_id))

    # list

    @bot.command(
        brief='Displays whitelisted users',
        description='Displays currently whitelisted and bound users.',
        name='list',
        aliases=('ls', 'all'))
    async def list_bindings(ctx: Context):
        MAX_LEN = 40

        wl = db.get_whitelist()
        em = Embed()
        em.title = 'Whitelist'
        em.color = EMBED_COLOR
        em.description = ''
        for dc_id, mc_id in list(wl.items())[:MAX_LEN]:
            em.description += '<@{}> - `{}`\n'.format(dc_id, mc_id)

        if len(wl) > MAX_LEN:
            em.description += '*and {} more...*'.format(len(wl) - MAX_LEN)

        await ctx.send(embed=em)

    ###########
    # RUN BOT #
    ###########

    bot.run(args.token)


if __name__ == '__main__':
    main()
