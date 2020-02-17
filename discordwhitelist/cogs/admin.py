import sys
from typing import Optional
from discord import Role, TextChannel
from discord.ext.commands import command, check, Cog, \
    Context, MissingRequiredArgument, BadArgument, CheckFailure
from asyncrcon import AsyncRCON
from database import SQLite


def is_guild_owner() -> bool:
    async def predicate(ctx: Context) -> bool:
        return ctx.author.id == ctx.guild.owner.id
    return check(predicate)


class Admin(Cog, name='Admin'):

    _rcon: AsyncRCON
    _db: SQLite
    _sudo_enabled: bool

    def __init__(self, bot, rcon: AsyncRCON, db: SQLite, sudo_enabled=False):
        self.bot = bot
        self._rcon = rcon
        self._db = db
        self._sudo_enabled = sudo_enabled

    async def _check_admin(self, ctx: Context) -> bool:
        role_id = self._db.get_admin_role(ctx.guild.id)
        admin = (role_id and role_id in [str(r.id) for r in ctx.author.roles])
        admin = admin or ctx.author.id == ctx.guild.owner.id
        if not admin:
            await ctx.send(':warning:  Insufficient permission.')
        return admin

    # adminrole

    @command(
        brief='Set admin role',
        description='Sets a role as admin role.')
    @is_guild_owner()
    async def adminrole(self, ctx: Context, role: Role):
        async with ctx.typing():
            self._db.set_admin_role(ctx.guild.id, role.id)
            await ctx.send(
                ':white_check_mark:  Role ' +
                '`{}` is now set as admin role.'.format(role.name))

    @adminrole.error
    async def adminrole_error(self, ctx: Context, err):
        if isinstance(err, MissingRequiredArgument):
            await ctx.send_help()
        if isinstance(err, BadArgument):
            await ctx.send(':warning:  Bad argument: {}'.format(err))
        if isinstance(err, CheckFailure):
            await ctx.send(':warning:  Insufficient permission.')

    # sudo

    @command(
        brief='Execute RCON command',
        description='Execute RCON command directly on server')
    async def sudo(self, ctx: Context, *cmd):
        async with ctx.typing():
            if not await self._check_admin(ctx):
                return

            if not self._sudo_enabled:
                await ctx.send(':warning:  Sudo is disbaled by configuration.')
                return

            res = await self._rcon.command(' '.join(cmd))
            await ctx.send(
                'Result:\n```{}```'.format(res or '[empty]'))

    # restart

    @command(
        brief='Restart the bot',
        description='Restart the bot instance - this only works if the script auto-restarts!')
    async def restart(self, ctx: Context):
        if not await self._check_admin(ctx):
            return

        await ctx.send(':repeat:  Restarting...')
        await ctx.bot.close()
        sys.exit(1)

    # restart

    @command(
        brief='Setup tatus channel',
        description='Set up the channel where the server status message will be spawned')
    async def statuschan(self, ctx: Context, channel: Optional[TextChannel] = None):
        if not await self._check_admin(ctx):
            return

        if channel is None:
            channel = ctx.message.channel

        self._db.set_status_channel(ctx.guild.id, channel.id)

        await ctx.send(':white_check_mark:  Set <#{}> as status channel.'.format(channel.id))
