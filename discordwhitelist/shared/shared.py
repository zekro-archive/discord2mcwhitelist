from discord.ext.commands import Context


EMBED_COLOR = 0xf90261


def lower(arg: str) -> str:
    return arg.lower()


def is_verbose(argv: list) -> bool:
    return '-v' in argv or '--verbose' in argv


async def verbose_output(ctx: Context, argv: list, op: list):
    if is_verbose(argv) and op:
        await ctx.send(
            'Verbose output:\n```{}```'.format('\n'.join(op)))

