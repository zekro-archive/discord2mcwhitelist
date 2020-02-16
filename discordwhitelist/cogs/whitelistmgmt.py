import asyncio
from discord import Embed
from discord.ext.commands import command, Cog, Context, MissingRequiredArgument
from shared import verbose_output, lower, EMBED_COLOR
from asyncrcon import AsyncRCON
from database import SQLite


class WhitelistMgmt(Cog, name='Whitelist Management'):

    _rcon: AsyncRCON
    _db: SQLite

    def __init__(self, bot, rcon: AsyncRCON, db: SQLite):
        self.bot = bot
        self._rcon = rcon
        self._db = db

    # bind

    @command(
        brief='Add to whitelist',
        description='Register a minecraft ID to your discord profile ' +
                    'and add it to the minecraft servers whitelist.',
        aliases=('add', 'set'))
    async def bind(self, ctx: Context, mc_id: str, *argv):
        async with ctx.typing():
            dc_id, curr_mc_id = self._db.get_whitelist_by_mc_id(mc_id)

            if curr_mc_id is not None and mc_id == curr_mc_id:
                await ctx.send(':warning:  This minecraft ID is already ' +
                               'bound to your account!')
                return

            if dc_id is not None and dc_id != str(ctx.message.author.id):
                await ctx.send(':warning:  This minecraft ID is already ' +
                               'registered by another user!')
                return

            old_mc_id = self._db.set_witelist(str(ctx.message.author.id), mc_id)

            vbop = []

            if old_mc_id is not None:
                vbop.append(await self._rcon.command(
                    'whitelist remove {}'.format(old_mc_id)))
                await asyncio.sleep(0.5)
            vbop.append(await self._rcon.command('whitelist add {}'.format(mc_id)))
            await asyncio.sleep(0.5)
            vbop.append(await self._rcon.command('whitelist reload'))

            await ctx.send(
                ':white_check_mark:  You are now bound to the mc ' +
                'account `{}` and added to the servers whitelist.'.format(mc_id))

            await verbose_output(ctx, argv, vbop)

    @bind.error
    async def bind_error(self, ctx: Context, err):
        if isinstance(err, MissingRequiredArgument):
            await ctx.send_help()

    # unbind

    @command(
        brief='Remove from whitelist',
        description='Unregisters a bound minecraft ID from your account ' +
                    'and removes you from the whitelist of the server.',
        aliases=('remove', 'unset'))
    async def unbind(self, ctx: Context, *argv):
        async with ctx.typing():
            _, mc_id = self._db.get_whitelist_by_discord_id(
                str(ctx.message.author.id))
            if mc_id is None:
                await ctx.send(':warning:  Ypur account is not bound to any ' +
                               'minecraft ID.')
                return

            vbop = []
            vbop.append(await self._rcon.command('whitelist remove {}'.format(mc_id)))
            await asyncio.sleep(0.5)
            vbop.append(await self._rcon.command('whitelist reload'))
            self._db.rem_witelist(str(ctx.message.author.id))

            await ctx.send(
                ':white_check_mark:  Successfully removed you from ' +
                'the servers whitelist and account is unbound.'.format(mc_id))

            await verbose_output(ctx, argv, vbop)

    # info

    @command(
        brief='Displays current binding',
        description='Displays the currently bound minecraft ID.',
        aliases=('bound', 'display'))
    async def info(self, ctx: Context):
        async with ctx.typing():
            _, mc_id = self._db.get_whitelist_by_discord_id(
                str(ctx.message.author.id))
            if mc_id is None:
                await ctx.send(':warning:  Ypur account is not bound to any ' +
                               'minecraft ID.')
                return

            await ctx.send(
                ':information_source:  Your account is currently bound to the ' +
                'minecraft ID `{}`.'.format(mc_id))

    # list

    @command(
        brief='Displays whitelisted users',
        description='Displays currently whitelisted and bound users.',
        name='list',
        aliases=('ls', 'all'))
    async def list_bindings(self, ctx: Context):
        MAX_LEN = 40

        async with ctx.typing():
            wl = self._db.get_whitelist()
            em = Embed()
            em.title = 'Whitelist'
            em.color = EMBED_COLOR
            em.description = ''
            for dc_id, mc_id in list(wl.items())[:MAX_LEN]:
                em.description += '<@{}> - `{}`\n'.format(dc_id, mc_id)

            if len(wl) > MAX_LEN:
                em.description += '*and {} more...*'.format(len(wl) - MAX_LEN)

            await ctx.send(embed=em)

    # serverwl

    @command(
        brief='Displays server whitelist',
        description='Displays the raw output of the ' +
                    '\'whitelist list\' command.',
        aliases=('showwl', 'listserver'))
    async def serverwl(self, ctx: Context):
        async with ctx.typing():
            res = await self._rcon.command('whitelist list')
            await ctx.send('```{}```'.format(res))
