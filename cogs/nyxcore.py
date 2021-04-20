from asyncio import sleep
from contextlib import closing, redirect_stdout
from io import StringIO
from sys import exc_info

from discord.ext import commands
from discord.ext.commands.view import StringView

import nyxbot.nyxcommands as nyxcommands
from nyxbot.nyxutils import reply

green = ["g", "green", "online"]
yellow = ["idle", "y", "yellow"]
red = ["busy", "r", "red"]
gray = ["gray", "grey", "off", "offline"]


class Core(commands.Cog):
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command(name="privilege", aliases=["rank"], hidden=True,
                      pass_context=True)
    async def check_privilege(self, ctx):
        """Displays your privilege rank."""
        if await self.nyx.is_owner(ctx.message.author):
            privilege = "Owner"
        else:
            privilege = str(
                self.nyx.get_user_data(ctx.message.author).get_privilege())
        if ctx.message.guild is None:
            await ctx.send("Privilege level: " + privilege)
        else:
            await ctx.send("".join(
                [ctx.message.author.mention, ", your privilege level is ",
                 privilege, "."]))

    @commands.command(rest_is_raw=True)
    @commands.is_owner()
    async def exec(self, ctx, *, code):
        """Remote executes code."""
        code = code.strip()
        py_start = code.lower().startswith("```py")
        python_start = py_start and code.lower().startswith("```python")
        view = StringView(code)
        view.skip_string(ctx.prefix)
        view.skip_ws()
        view.skip_string(ctx.invoked_with)
        view.skip_ws()
        code = view.read_rest()
        if python_start:
            code = code[9:]
        elif py_start:
            code = code[5:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        del py_start, python_start, view
        with closing(StringIO()) as log:
            with redirect_stdout(log):
                try:
                    exec(code)
                except Exception:
                    error = exc_info()
                    for e in error:
                        print(e)
            output = log.getvalue()
        output = "```\n" + output + "```"
        await reply(ctx, output)

    @commands.command(rest_is_raw=True)
    @nyxcommands.has_privilege(privilege=-1)
    async def echo(self, ctx, *, words):
        """I copy what you say."""
        stuff = words.strip()  # " ".join(words)
        if ctx.guild is not None and ctx.message.channel.permissions_for(
                ctx.message.guild.get_member(
                    self.nyx.user.id)).manage_messages:
            await ctx.message.delete()
        elif not stuff:
            await ctx.send("What?")
            return
        print(stuff)
        await ctx.send(stuff)

    @commands.command()
    @nyxcommands.has_privilege(privilege=-1)
    async def load(self, ctx, extension):
        try:
            self.nyx.load_extension(extension)
            await ctx.send("Attempted to load {}.".format(extension))
        except Exception:  # I can use "bare except" all I want >:<
            await ctx.send("Failed to load {}.".format(extension))

    @commands.command()
    @nyxcommands.has_privilege(privilege=-1)
    async def reload(self, ctx, extension):
        try:
            self.nyx.reload_extension(extension)
            await ctx.send("Attempted to reload {}.".format(extension))
        except Exception:
            await ctx.send("Failed to reload {}.".format(extension))

    @commands.command()
    @nyxcommands.has_privilege(privilege=-1)
    async def unload(self, ctx, extension):
        try:
            self.nyx.unload_extension(extension)
            await ctx.send("Attempted to unload {}.".format(extension))
        except Exception:
            await ctx.send("Failed to unload {}.".format(extension))

    @commands.command()
    @nyxcommands.has_privilege(privilege=-1)
    async def shutdown(self, ctx):
        """Dun kill me pls..."""
        await ctx.send("Light cannot be without dark!!!")
        await sleep(1)
        await self.nyx.close()


def setup(nyx):
    nyx.add_cog(Core(nyx))
